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
        this.unmarkEdges(this.all_edges || []);
        this.marker_source && this.map.removeLayer(this.marker_source);
        this.marker_dest && this.map.removeLayer(this.marker_dest);
    },

    // Provide a way to unmark everything
    unmarkEdges: function(edges) {
        var self = this;
        this.unmarkLayers(
            $.map(edges, function(edge) { return self.idToLayer(edge.id); })
        );
    },

    // Try to deactivate all styles related to dijkstra
    unmarkLayers: function(layers) {
        var self = this;
        $.each(layers, function(idx, layer) {
            // deactivate lazily and then compute resulting style
            self.cameleon.deactivate('dijkstra_to', layer, true);
            self.cameleon.deactivate('dijkstra_from', layer, true);
            self.cameleon.deactivate('dijkstra_computed', layer, true);
            self.cameleon.applyCurrentStyle(layer);
        });
    },


    removeHooks: function () {
        var self = this;
        this._container.style.cursor = '';
        this.graph_layer.off('click', this._onClick, this);
    },

    // On click on a layer with the graph
    _onClick: function(e) {
        var layer = e.layer;

        if (this.steps.length >= 2) {
            return; // should not happen
        }
        // don't accept twice a step
        if (this.steps.indexOf(e.layer) != -1) {
            return;
        }

        var edge_id = this.layerToId(layer);
        var edge = this.graph.edges[edge_id];

        this.steps.push(edge_id);
        var can_compute = (this.steps.length == 2);

        var marker;
        // mark
        if (can_compute) {
            this._container.style.cursor = '';
            marker = this.marker_dest = this.markersFactory.dest(e.latlng)
            this.cameleon.activate('dijkstra_to', layer);
        } else {
            this._container.style.cursor = 'e-resize';
            marker = this.marker_source = this.markersFactory.source(e.latlng)
            this.cameleon.activate('dijkstra_from', layer);
        }

        if (can_compute) {
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
        var all_edges = [];
        if (computed_paths) {
            computed_paths.forEach(function(cpath) {
                all_edges.push(cpath.from_edge);
                cpath.path.forEach(function(path_component) {
                    all_edges.push(path_component.edge);
                });
            })
            all_edges.push(
                computed_paths[computed_paths.length - 1].to_edge
            );
        }
        // fixme: seems to return more than once the first edge ? :<
        return all_edges;
    },

    _onComputedPaths: function(new_computed_paths) {
        var self = this;
        var old_computed_paths = this.computed_paths;
        this.computed_paths = new_computed_paths;

        // compute and store all edges of the new paths (usefull for further computation)
        this.all_edges = this._extractAllEdges(new_computed_paths);

        // set inner style
        this._eachInnerComputedPathsEdges(new_computed_paths, function(edge) {
            self.cameleon.activate('dijkstra_computed', self.idToLayer(edge.id));
        });

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
//        'from_edge': Edge
//      , 'to_edge': Edge
//      , 'weight': Int
//      , 'path': DisjktraPath as returned by dijkstra_from_nodes.path
//                Array of { start: Node, end: Node, edge: { id, length }, weigh: int }
//   }
//
Caminae.compute_path = (function() {

    function computeTwoStepsPath(graph, steps) {
        if (steps.length > 2) {
            return null; // should raise
        }

        var from_edge_id = steps[0]
          , to_edge_id = steps[1]
          , from_edge = graph.edges[from_edge_id]
          , to_edge = graph.edges[to_edge_id]
          , from_nodes = from_edge.nodes_id
          , to_nodes = to_edge.nodes_id
        ;

        // path: {
        //   weight: ... ,
        //   path : list of { start, end, edge } ids
        var path = Caminae.Dijkstra.get_shortest_path_from_graph(graph, from_nodes, to_nodes);

        if(! path)
            return null;

        // return an array as we may compute more than two steps path
        var computed_paths = [{
              'from_edge': from_edge
            , 'to_edge': to_edge
            , 'path': path.path
            , 'weight': path.weight
        }];

        return computed_paths;
    }

    // TODO: compute more than two steps
    return computeTwoStepsPath;

})();
