L.Control.TopologyPoint = L.Control.extend({
    options: {
        position: 'topright',
    },

    initialize: function (map, options) {
        L.Control.prototype.initialize.call(this, options);
        this.topologyhandler = new L.Handler.TopologyPoint(map);
    },

    onAdd: function (map) {
        this._container = L.DomUtil.create('div', 'leaflet-control-zoom');
        var link = L.DomUtil.create('a', 'leaflet-control-draw-marker', this._container);
        link.href = '#';
        link.title = 'Point';
        var self = this;
        L.DomEvent
                .addListener(link, 'click', L.DomEvent.stopPropagation)
                .addListener(link, 'click', L.DomEvent.preventDefault)
                .addListener(link, 'click', function() {
                     self.topologyhandler.enable();
                });
        return this._container;
    },

    onRemove: function (map) {
    }
});



L.Handler.TopologyPoint = L.Marker.Draw.extend({
    initialize: function (map, options) {
        L.Marker.Draw.prototype.initialize.call(this, map, options);
        map.on('draw:marker-created', function (e) {
            this.fire('added', {marker:e.marker});
        }, this);
    },
});



L.Control.Multipath = L.Control.extend({
    options: {
        position: 'topright',
    },

    /* dijkstra */
    initialize: function (map, graph_layer, dijkstra, markersFactory, options) {
        L.Control.prototype.initialize.call(this, options);
        this.dijkstra = dijkstra;
        this.multipath_handler = new L.Handler.MultiPath(
            map, graph_layer, dijkstra, markersFactory, this.options.handler
        );
    },

    onAdd: function (map) {
        this._container = L.DomUtil.create('div', 'leaflet-control-zoom');
        var link = L.DomUtil.create('a', 'leaflet-control-zoom-out multipath-control', this._container);
        link.href = '#';
        link.title = 'Multipath';

        var self = this;
        L.DomEvent
                .addListener(link, 'click', L.DomEvent.stopPropagation)
                .addListener(link, 'click', L.DomEvent.preventDefault)
                .addListener(link, 'click', function() {
                     self.multipath_handler.enable();
                });

        return this._container;
    },

    onRemove: function (map) {
    }

});

L.Handler.MultiPath = L.Handler.extend({
    includes: L.Mixin.Events,

    initialize: function (map, graph_layer, dijkstra, markersFactory, options) {
        this.map = map;
        this._container = map._container;
        this.graph_layer = graph_layer;
        this.cameleon = this.graph_layer._cameleon;

        // .graph .algo ?
        this.dijkstra = dijkstra;
        this.graph = dijkstra.graph;

        // markers
        this.markersFactory = markersFactory;
        this.marker_source = null;
        this.marker_dest = null;

        this.layerToId = function layerToId(layer) {
            return graph_layer.getPk(layer);
        };

        this.idToLayer = function(id) {
            return graph_layer.getLayer(id);
        };
    },

    setState: function(state, autocompute) {
        autocompute = autocompute === undefined ? true : autocompute;

        // Ensure we got a fresh start
        this.disable();
        this.enable();

        this._onClick({latlng: state.start_ll, layer:state.start_layer});
        this._onClick({latlng: state.end_ll, layer:state.end_layer});

        // We should (must !) find the same old path
        autocompute && this.computePaths();
    },

    // TODO: when to remove/update links..? what's the behaviour ?
    addHooks: function () {
        var self = this;

        // Clean all previous edges if they exist
        this.unmarkAll();

        this.marker_source && this.map.removeLayer(this.marker_source);
        this.marker_dest && this.map.removeLayer(this.marker_dest);

        this.steps = [];
        this.computed_paths = [];
        this.all_edges = [];
        this._container.style.cursor = 'w-resize';

        this.graph_layer.on('click', this._onClick, this);

        this.fire('enabled');
    },

    unmarkAll: function() {
        this.marker_source && this.map.removeLayer(this.marker_source);
        this.marker_dest && this.map.removeLayer(this.marker_dest);
    },

    removeHooks: function () {
        var self = this;
        this._container.style.cursor = '';
        this.graph_layer.off('click', this._onClick, this);
    },

    // On click on a layer with the graph
    _onClick: function(e) {
        if (this.steps.length >= 2) return;
        var self = this;

        var layer = e.layer
          , latlng = e.latlng
          , len = this.steps.length;

        var next_step_idx = this.steps.length;

        // 1. Click - you are adding a new marker
        var marker;
        if (next_step_idx == 0) {
            this._container.style.cursor = 'e-resize';
            marker = this.markersFactory.source(latlng)
        } else {
            this._container.style.cursor = '';
            marker = this.markersFactory.dest(latlng)
        }

        marker.on('move', function (e) {
            var marker = e.target;
            if (marker.snap) marker.fire('snap', {object: marker.snap, 
                                                  location: marker.getLatLng()});
        });
        marker.on('snap', function (e) {
            self.updateStep(next_step_idx, marker, e.object);
        });
        marker.on('unsnap', function () {
            self.steps.splice(next_step_idx, 1, null);
            self.fire('unsnap');
        });

        // Restrict snaplist to layer and snapdistance to max_value
        // will ensure this get snapped and to the layer clicked
        var snapdistance = Number.MAX_VALUE;
        var closest = MapEntity.Utils.closest(map, marker, [ layer ], snapdistance);
        marker.editing.updateClosest(marker, closest);
    },

    updateStep: function(step_idx, marker, layer, autocompute) {
        // Should check that step_idx is < steps.length...
        var autocompute = autocompute === undefined ? true : autocompute;


        if (step_idx == 0) { this.marker_source = marker; }
        else if (step_idx == 1) { this.marker_dest = marker; }
        else { console.log('More than 2 points are unauthorized for now'); return; }

        var pop = new Caminae.TopologyHelper.PointOnPolyline(marker.getLatLng(), layer);

        // Replace the point at idx step_idx
        this.steps.splice(step_idx, 1, pop);

        if (autocompute && this.canCompute()) {
            this.computePaths();
        }
    },

    canCompute: function() {
        if (this.steps.length != 2)
            return false;

        for (var i = 0; i < this.steps.length; i++) {
            if (this.steps[i] === null)
                return false;
        }

        return true;
    },

    computePaths: function() {
        if (this.canCompute()) {
            var computed_paths = this.dijkstra.compute_path(this.graph, this.steps)
            this._onComputedPaths(computed_paths);
        }
    },


    // Extract the complete edges list from the first to the last one
    _eachInnerComputedPathsEdges: function(computed_paths, f) {
        if (computed_paths) {
            computed_paths.forEach(function(cpath) {
                cpath.path.forEach(function(path_component) {
                    f(path_component.edge);
                });
            });
        }
    },

    // Extract the complete edges list from the first to the last one
    _extractAllEdges: function(computed_paths) {
        if (! computed_paths)
            return [];

        return $.map(computed_paths, function(cpath) {
            return $.map(cpath.path, function(path_component) {
                return path_component.real_edge || path_component.edge;
            });
        });
    },

    _onComputedPaths: function(new_computed_paths) {
        var self = this;
        var old_computed_paths = this.computed_paths;
        this.computed_paths = new_computed_paths;

        // compute and store all edges of the new paths (usefull for further computation)
        this.all_edges = this._extractAllEdges(new_computed_paths);

        this.fire('computed_paths', {
            'new': new_computed_paths,
            'new_edges': this.all_edges,
            'old': old_computed_paths,
            'marker_source': this.marker_source,
            'marker_dest': this.marker_dest
        });

        this.disable();
    }

});


// Computed_paths:
//
// Returns:
//   Array of {
//       path : Array of { start: Node_id, end: Node_id, edge: Edge, weight: Int (edge.length) }
//       weight: Int
//   }
//
Caminae.compute_path = (function() {

    function computeTwoStepsPath(graph, steps) {
        if (steps.length > 2) {
            return null; // should raise
        }
        if (! (steps[0].isValid() && steps[1].isValid() )) {
            return null;
        }

        var from_pop = steps[0]
          , to_pop = steps[1];

        // alter graph
        var from_pop_opt = from_pop.addToGraph(graph)
          , to_pop_opt = to_pop.addToGraph(graph);

        var from_nodes = [ from_pop_opt.new_node_id ]
          , to_nodes = [ to_pop_opt.new_node_id ];

        // weighted_path: {
        //   path : Array of { start: Node_id, end: Node_id, edge: Edge, weight: Int (edge.length) }
        //   weight: Int
        // }
        var weighted_path = Caminae.Dijkstra.get_shortest_path_from_graph(graph, from_nodes, to_nodes);

        // restore graph
        from_pop_opt.rmFromGraph();
        to_pop_opt.rmFromGraph();

        if(! weighted_path)
            return null;

        // Some path component may use an edge that does not belong to the graph
        // (a transient edge that was created from a transient point - a marker).
        // In this case, the path component gets a new `real_edge' attribute
        // which is the edge that the virtual edge is part of.
        function markVirtualPath(path, pops_opt) {
            $.each(path, function(i, path_component) {
                var edge_id = path_component.edge.id;
                var pop_opt, edge;

                // Those PointOnPolylines knows the virtual edge and the initial one
                for (var i = 0; i < pops_opt.length; i++) {
                    pop_opt = pops_opt[i];
                    edge = pop_opt.new_edges[edge_id]
                    if (edge !== undefined) {
                        path_component.real_edge = pop_opt.initial_edge;
                        break;
                    }
                }
            });
        }

        markVirtualPath(weighted_path.path, [ from_pop_opt, to_pop_opt ]);

        // return an array as we may compute more than two steps path
        return [
            weighted_path
        ];
    }

    // TODO: compute more than two steps
    return computeTwoStepsPath;

})();
