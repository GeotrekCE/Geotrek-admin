L.Control.TopologyPoint = L.Control.extend({
    options: {
        position: 'topright',
    },

    initialize: function (map, options) {
        L.Control.prototype.initialize.call(this, options);
        this.topologyhandler = new L.Handler.TopologyPoint(map);
        this.topologyhandler.on('added', this.toggle, this);
    },

    toggle: function() {
        if (this.topologyhandler.enabled()) {
            this.topologyhandler.disable.call(this.topologyhandler);
            L.DomUtil.removeClass(this._container, 'enabled');
        } else {
            this.topologyhandler.enable.call(this.topologyhandler);
            L.DomUtil.addClass(this._container, 'enabled');
        }
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
                .addListener(link, 'click', this.toggle, this);
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

    toggle: function() {
        if (this.multipath_handler.enabled()) {
            this.multipath_handler.disable.call(this.multipath_handler);
            L.DomUtil.removeClass(this._container, 'enabled');
        } else {
            this.multipath_handler.enable.call(this.multipath_handler);
            L.DomUtil.addClass(this._container, 'enabled');
        }
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
                .addListener(link, 'click', this.toggle, this);

        return this._container;
    },

    onRemove: function (map) {
    }

});


L.ActivableMarker = L.Marker.extend({
    initialize: function () {
        L.Marker.prototype.initialize.apply(this, arguments);
        this._activated = false;
        // Watch out if a callback is added and we are already in this state.
        // It won't be called !
        this.activate_cbs = [];
        this.deactivate_cbs = [];
    },
    'activated': function() {
        return this._activated;
    },
    'activate': function() {
        if (!this._activated) {
            for (var i = 0; i < this.activate_cbs.length; i++) {
                this.activate_cbs[i](this);
            }
            this._activated = true;
        }
    },
    'deactivate': function() {
        if (this._activated) {
            for (var i = 0; i < this.deactivate_cbs.length; i++) {
                this.deactivate_cbs[i](this);
            }
            this._activated = false;
        }
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

        // Init a fresh state
        this.reset();

        this.layerToId = function layerToId(layer) {
            return graph_layer.getPk(layer);
        };

        this.idToLayer = function(id) {
            return graph_layer.getLayer(id);
        };
    },

    setState: function(state, autocompute) {
        autocompute = autocompute === undefined ? true : autocompute;
        var self = this;

        // Ensure we got a fresh start
        this.disable();
        this.reset();
        this.enable();

        this._onClick({latlng: state.start_ll, layer:state.start_layer});
        this._onClick({latlng: state.end_ll, layer:state.end_layer});

        state.via_markers && $.each(state.via_markers, function(idx, via_marker) {
            self.addViaStep(via_marker.marker, idx + 1);

            self.forceMarkerToLayer(via_marker.marker, via_marker.layer);
        });
    },

    // Reset the whole state
    reset: function() {
        var self = this;

        // remove all markers
        this.steps && $.each(this.steps, function(pop) {
            self.map.removeLayer(pop.marker);
        });

        // reset state
        this.steps = [];
        this.computed_paths = [];
        this.all_edges = [];

        this.marker_source = this.marker_dest = null;
    },

    // Activate/Deactivate existing steps and markers - mostly about (un)bindings listeners
    stepsToggleActivate: function(activate) {
        var cb;
        // /!\ Order in activation is important, first activate marker then pop
        // The marker.move listener must be set before the pop.move listener
        if (activate) {
            cb = function(pop) { pop.marker.activate(); pop.toggleActivate(true); }
        } else {
            cb = function(pop) { pop.marker.deactivate(); pop.toggleActivate(false); }
        }

        $(this.steps).each(function(i, pop) { pop && cb(pop); });
    },

    addHooks: function () {
        this._container.style.cursor = 'w-resize';
        this.graph_layer.on('click', this._onClick, this);

        this.stepsToggleActivate(true);

        this.fire('enabled');
    },

    removeHooks: function() {
        this._container.style.cursor = '';
        this.graph_layer.off('click', this._onClick, this);

        this.stepsToggleActivate(false);

        this.fire('disabled');
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
            this.marker_source = marker;
        } else {
            this._container.style.cursor = '';
            marker = this.markersFactory.dest(latlng)
            this.marker_dest = marker;
        }

        var pop = self.createStep(marker, next_step_idx);

        pop.toggleActivate();

        // If this was clicked, the marker should be close enought, snap it.
        self.forceMarkerToLayer(marker, layer);
    },

    forceMarkerToLayer: function(marker, layer) {
        var self = this;

        // Restrict snaplist to layer and snapdistance to max_value
        // will ensure this get snapped and to the layer clicked
        var snapdistance = Number.MAX_VALUE;
        var closest = MapEntity.Utils.closest(self.map, marker, [ layer ], snapdistance);
        marker.editing.updateClosest(marker, closest);
    },

    createStep: function(marker, idx) {
        var self = this;

        var pop = new Caminae.TopologyHelper.PointOnPolyline(marker);
        this.steps.splice(idx, 0, pop);

        pop.events.on('valid', function() {
            self.computePaths();
        });

        return pop;
    },

    // add an in between step
    addViaStep: function(marker, step_idx) {
        var self = this;

        // A via step idx must be inserted between first and last...
        if (! (step_idx >= 1 && step_idx <= this.steps.length - 1)) {
            throw "NOT";
        }

        var pop = this.createStep(marker, step_idx);

        // remove marker on click
        function removeViaStep() {
            self.steps.splice(self.getStepIdx(pop), 1);
            self.map.removeLayer(marker);
            self.computePaths();
        }

        function removeOnClick() { marker.on('click', removeViaStep); }
        pop.marker.activate_cbs.push(removeOnClick);
        pop.marker.deactivate_cbs.push(function() { marker.off('click', removeViaStep); });

        // marker is already activated, trigger manually removeOnClick
        removeOnClick();
        pop.toggleActivate();
    },

    canCompute: function() {
        if (this.steps.length < 2)
            return false;

        for (var i = 0; i < this.steps.length; i++) {
            if (! this.steps[i].isValid())
                return false;
        }

        return true;
    },

    getStepIdx: function(step) {
        return this.steps.indexOf(step);
    },

    getStepIdxFromMarker: function(marker) {
        for (var i = 0; i < this.steps.length; i++) {
            if (this.steps[i].marker === marker)
                return i;
        }
        return -1
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
            return [ $.map(cpath.path, function(path_component) {
                return path_component.real_edge || path_component.edge;
            }) ];
        });
    },

    _onComputedPaths: function(new_computed_paths) {
        var self = this;
        var old_computed_paths = this.computed_paths;
        this.computed_paths = new_computed_paths;

        // compute and store all edges of the new paths (usefull for further computation)
        this.all_edges = this._extractAllEdges(new_computed_paths);

        this.fire('computed_paths', {
            'computed_paths': new_computed_paths,
            'new_edges': this.all_edges,
            'old': old_computed_paths,
            'marker_source': this.marker_source,
            'marker_dest': this.marker_dest
        });
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

    function computePaths(graph, steps) {
        /*
        if (steps.length < 2) {
            return null;
        }

        for (var i = 0; i < steps.length; i ++) {
            if (! steps[i].isValid())
                return null;
        }
        */

        var paths = [], path;
        for (var j = 0; j < steps.length - 1; j++) {
            path = computeTwoStepsPath(graph, steps[j], steps[j + 1]);

            if (! path)
                return null;

            // may be usefull to check back
            path.from_pop = steps[j];
            path.to_pop = steps[j+1];

            paths.push(path);
        }

        return paths;
    }

    function computeTwoStepsPath(graph, from_pop, to_pop) {

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

        markVirtualPath(weighted_path.path, [ from_pop_opt, to_pop_opt ]);

        // return an array as we may compute more than two steps path
        return weighted_path;
    }

    // TODO: compute more than two steps
    return computePaths;

})();
