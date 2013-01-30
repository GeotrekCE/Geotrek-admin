L.Control.TopologyPoint = L.Control.extend({
    includes: L.Mixin.ActivableControl,

    options: {
        position: 'topright',
    },

    initialize: function (map, options) {
        L.Control.prototype.initialize.call(this, options);
        this.handler = new L.Handler.TopologyPoint(map);
        // Deactivate control once point is added
        this.handler.on('added', this.toggle, this);
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
    includes: L.Mixin.ActivableControl,

    options: {
        position: 'topright',
    },

    initialize: function (map, graph_layer, snapObserver, options) {
        L.Control.prototype.initialize.call(this, options);

        graph_layer.registerStyle('dijkstra_from', 10, {'color': 'yellow', 'weight': 5, 'opacity': 1})
                   .registerStyle('dijkstra_to', 11, {'color': 'yellow', 'weight': 5, 'opacity': 1})
                   .registerStyle('dijkstra_step', 9, {'color': 'yellow', 'weight': 5, 'opacity': 1})
                   .registerStyle('dijkstra_computed', 8, {'color': 'yellow', 'weight': 5, 'opacity': 1});

        this.handler = new L.Handler.MultiPath(
            map, graph_layer, snapObserver, this.options.handler
        );
    },

    setGraph: function (graph) {
        /**
         * Set the Dikjstra graph
         */
        this.handler.setGraph(graph);
        this.activable(true);
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

        // Control is not activable until paths and graph are loaded
        this.activable(false);

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
    
    activated: function() {
        return this._activated;
    },

    activate: function() {
        if (!this._activated) {
            for (var i = 0; i < this.activate_cbs.length; i++) {
                this.activate_cbs[i](this);
            }
            this._activated = true;
        }
    },
    
    deactivate: function() {
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

    initialize: function (map, graph_layer, snapObserver, options) {
        this.map = map;
        this._container = map._container;
        this.graph_layer = graph_layer;
        this.snapObserver = snapObserver;
        this.cameleon = this.graph_layer._cameleon;
        this.options = options;

        this.graph = null;

        // markers
        this.markersFactory = this.getMarkers();

        // Init a fresh state
        this.reset();

        this.layerToId = function layerToId(layer) {
            return graph_layer.getPk(layer);
        };

        this.idToLayer = function(id) {
            return graph_layer.getLayer(id);
        };
        
        
        /*
         * Draggable via steps
         * 
         * The following piece of code was also taken from formfield.js
         * It place is here, but needs refactoring to become elegant.
         */
        this.drawOnMouseMove = null;

        this.on('disabled', function() {
            this.drawOnMouseMove && this.map.off('mousemove', this.drawOnMouseMove);
        }, this);

        // Draggable marker initialisation and step creation
        var draggable_marker = null;
        var self = this;
        (function() {
            function dragstart(e) {
                var next_step_idx = self.draggable_marker.group_layer.step_idx + 1;
                self.addViaStep(self.draggable_marker, next_step_idx);
            }
            function dragend(e) {
                self.draggable_marker.off('dragstart', dragstart);
                self.draggable_marker.off('dragend', dragend);
                init();
            }
            function init() {
                self.draggable_marker = self.markersFactory.drag(new L.LatLng(0, 0), null, true);

                self.draggable_marker.on('dragstart', dragstart);
                self.draggable_marker.on('dragend', dragend);
                self.map.removeLayer(self.draggable_marker);
            }

            init();
        })();

        this.on('computed_paths', this.onComputedPaths, this);
    },

    setGraph: function (graph) {
        this.graph = graph;
    },

    setState: function(state, autocompute) {
        autocompute = autocompute === undefined ? true : autocompute;
        var self = this;

        // Ensure we got a fresh start
        this.disable();
        this.reset();
        this.enable();

        if (window.DEBUG) {
            console.log('setState('+JSON.stringify({start:{pk:state.start_layer.properties.pk,
                                                           latlng:state.start_ll.toString()},
                                                    end:  {pk:state.end_layer.properties.pk,
                                                           latlng:state.end_ll.toString()}})+')');
        }
        this._onClick({latlng: state.start_ll, layer:state.start_layer});
        this._onClick({latlng: state.end_ll, layer:state.end_layer});

        state.via_markers && $.each(state.via_markers, function(idx, via_marker) {
            if (window.DEBUG) {
                console.log('Add via marker (' + JSON.stringify({pk: via_marker.layer.properties.pk,
                                                                 latlng: via_marker.marker.getLatLng().toString()}) + ')');
            }
            self.addViaStep(via_marker.marker, idx + 1);
            self.forceMarkerToLayer(via_marker.marker, via_marker.layer);
        });
    },

    // Reset the whole state
    reset: function() {
        var self = this;

        // remove all markers from PointOnPolyline objects
        this.steps && $.each(this.steps, function(i, pop) {
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
            marker.on('unsnap', function () {
                this.showPathGeom(null);
            }, this);
            this.marker_source = marker;
        } else {
            this._container.style.cursor = '';
            marker = this.markersFactory.dest(latlng)
            marker.on('unsnap', function () {
                this.showPathGeom(null);
            }, this);
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
        var closest = L.GeomUtils.closest(self.map, marker, [ layer ], snapdistance);
        marker.editing.updateClosest(marker, closest);
    },

    createStep: function(marker, idx) {
        var self = this;

        var pop = new Caminae.TopologyHelper.PointOnPolyline(marker);
        this.steps.splice(idx, 0, pop);  // Insert pop at position idx

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
            throw "StepIndexError";
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
        if (!this.graph)
            return false;

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
            var computed_paths = Caminae.compute_path(this.graph, this.steps)
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
    },

    restoreTopology: function (topo) {

        /*
         * Topo is a list of sub-topologies.
         *
         *  X--+--+---O-------+----O--+---+--X
         *  
         * Each sub-topoogy is a way between markers. The first marker
         * of the first sub-topology is the beginning, the last of the last is the end.
         * All others are intermediary points.
         */
        var self = this;


        // Only first and last positions
        if (topo.length == 1 && topo[0].paths.length == 1) {
            // There is only one path, both positions values are relevant
            // and each one represents a marker
            var topo = topo[0]
              , paths = topo.paths
              , positions = topo.positions;

            var first_pos = positions[0][0];
            var last_pos = positions[0][1];

            var start_layer = this.idToLayer(paths[0]);
            var end_layer = this.idToLayer(paths[paths.length - 1]);

            var start_ll = L.GeomUtils.getLatLngFromPos(this.map, start_layer, [ first_pos ])[0];
            var end_ll = L.GeomUtils.getLatLngFromPos(this.map, end_layer, [ last_pos ])[0];

            var state = {
                start_ll: start_ll,
                end_ll: end_ll,
                start_layer: start_layer,
                end_layer: end_layer
            };
            this.setState(state);
        }
        else {
            var start_layer_ll = {}
              , end_layer_ll = {}
              , via_markers = [];

            var pos2latlng = function (pos, layer) {
                var used_pos = pos[0];
                if (pos[0] == 0.0 && pos[1] != 1.0)
                    used_pos = pos[1];
                if (pos[0] == 1.0 && pos[1] != 0.0)
                    used_pos = pos[1];
                if (pos[0] != 1.0 && pos[1] == 0.0)
                    used_pos = pos[0];
                if (pos[0] != 0.0 && pos[1] == 1.0)
                    used_pos = pos[0];
                console.log("Chose " + used_pos + " for " + pos);
                var ll = L.GeomUtils.getLatLngFromPos(self.map, layer, [ used_pos ]);
                if (ll.length < 1) {
                    console.error('getLatLngFromPos()');
                    return null;
                }
                return ll[0];
            };

            for (var i=0; i<topo.length; i++) {
                var subtopo = topo[i]
                  , firsttopo = i==0
                  , lasttopo = i==topo.length-1;

                var paths = subtopo.paths
                  , positions = subtopo.positions || {}
                  , lastpath = paths.length-1;

                // Safety check.
                if (!('0' in positions)) positions['0'] = [0.0, 1.0];
                if (!(lastpath in positions)) positions[lastpath] = [0.0, 1.0];

                var firstlayer = self.idToLayer(paths[0])
                  , lastlayer = self.idToLayer(paths[lastpath]);

                if (firsttopo) {
                    start_layer_ll.layer = firstlayer;
                    start_layer_ll.ll = pos2latlng(positions['0'], firstlayer);
                }
                if (lasttopo) {
                    end_layer_ll.layer = lastlayer;
                    end_layer_ll.ll = pos2latlng(positions[lastpath], lastlayer);
                }
                else {
                    var layer = lastlayer
                      , ll = pos2latlng(positions[lastpath], layer);
                    // Add a via marker
                    via_markers.push({
                        layer: layer,
                        marker: self.markersFactory.drag(ll, null, true)
                    });
                }
            }

            var state = {
                    start_ll: start_layer_ll.ll,
                    end_ll: end_layer_ll.ll,
                    start_layer: start_layer_ll.layer,
                    end_layer: end_layer_ll.layer,
                    via_markers: via_markers
                };

            // Restore state as if a user clicks.
            this.setState(state);
        }
    },

    showPathGeom: function (layer) {
        // This piece of code was moved from formfield.js, its place is here,
        // not around control instantiation. Of course this is not very elegant.
        var self = this;
        if (!this.markPath)
            this.markPath = (function() {
                var current_path_layer = null;
                return {
                    'updateGeom': function(new_path_layer) {
                        var prev_path_layer = current_path_layer;
                        current_path_layer = new_path_layer;

                        if (prev_path_layer) {
                            self.map.removeLayer(prev_path_layer);
                            self.cameleon.deactivate('dijkstra_computed', prev_path_layer);
                        }

                        if (new_path_layer) {
                            self.map.addLayer(new_path_layer);
                            self.cameleon.activate('dijkstra_computed', new_path_layer);
                        }
                    }
                }
            })();
        this.markPath.updateGeom(layer);
    },

    getMarkers: function() {
        var self = this;
        
        var map = this.map, 
            snapObserver = this.snapObserver;
        
        // snapObserver and map are required to setup snappable markers
        // returns marker with an on('snap' possibility ?
        var dragging = false;
        function setDragging() { dragging = true; };
        function unsetDragging() { dragging = false; };
        function isDragging() { return dragging; };
        function activate(marker) {
            marker.dragging.enable();
            marker.editing.enable();
            marker.on('dragstart', setDragging);
            marker.on('dragend', unsetDragging);
        }
        function deactivate(marker) {
            marker.dragging.disable();
            marker.editing.disable();
            marker.off('dragstart', setDragging);
            marker.off('dragend', unsetDragging);
        }

        var markersFactory = {
            isDragging: isDragging,
            makeSnappable: function(marker) {
                marker.editing = new L.Handler.MarkerSnapping(map, marker);
                snapObserver.add(marker);
                marker.activate_cbs.push(activate);
                marker.deactivate_cbs.push(deactivate);

                marker.activate();
            },
            generic: function (latlng, layer, classname, snappable) {
                snappable = snappable === undefined ? true : snappable;
                
                var marker = new L.ActivableMarker(latlng, {
                    'draggable': true, 
                    'icon': new L.Icon({
                        iconUrl: self.options.iconUrl,
                        shadowUrl: self.options.shadowUrl,
                        iconSize: new L.Point(25, 41),
                        iconAnchor: new L.Point(13, 41),
                        popupAnchor: new L.Point(1, -34),
                        shadowSize: new L.Point(41, 41)
                    })
                });
                map.addLayer(marker);

                $(marker._icon).addClass(classname);

                if (snappable)
                    this.makeSnappable(marker);

                return marker;
            },
            source: function(latlng, layer) {
                return this.generic(latlng, layer, 'marker-source');
            },
            dest: function(latlng, layer) {
                return this.generic(latlng, layer, 'marker-target');
            },
            via: function(latlng, layer, snappable) {
                return this.generic(latlng, layer, 'marker-via', snappable);
            },
            drag: function(latlng, layer, snappable) {
                var marker = new L.ActivableMarker(latlng, {
                    'draggable': true,
                    'icon': new L.Icon({
                        iconUrl: self.options.iconDragUrl,
                        iconSize: new L.Point(18, 18)
                    })
                });

                map.addLayer(marker);
                if (snappable)
                    this.makeSnappable(marker);

                return marker;
            }
        };

        return markersFactory;
    },

    onComputedPaths: function(data) {
        var self = this;
        var topology = Caminae.TopologyHelper.buildTopologyFromComputedPath(this.idToLayer, data);
        
        this.showPathGeom(topology.layer);
        this.fire('computed_topology', {topology:topology.serialized});

        // ## ONCE ##
        this.drawOnMouseMove && this.map.off('mousemove', this.drawOnMouseMove);

        var dragTimer = new Date();
        this.drawOnMouseMove = function(a) {
            var date = new Date();
            if ((date - dragTimer) < 25) {
                return;
            }
            if (self.markersFactory.isDragging()) {
                return;
            }

            dragTimer = date;


            for (var i = 0; i < self.steps.length; i++) {
                // Compare point rather than ll
                var marker_ll = self.steps[i].marker.getLatLng();
                var marker_p = self.map.latLngToLayerPoint(marker_ll);

                if (marker_p.distanceTo(a.layerPoint) < 10) {
                    self.map.removeLayer(self.draggable_marker);
                    return;
                }
            }

            var MIN_DIST = 30;

            var layerPoint = a.layerPoint
              , min_dist = Number.MAX_VALUE
              , closest_point = null
              , matching_group_layer = null;

            topology.layer && topology.layer.eachLayer(function(group_layer) {
                group_layer.eachLayer(function(layer) {
                    var p = layer.closestLayerPoint(layerPoint);
                    if (p && p.distance < min_dist && p.distance < MIN_DIST) {
                        min_dist = p.distance;
                        closest_point = p;
                        matching_group_layer = group_layer;
                    }
                });
            });

            if (closest_point) {
                self.draggable_marker.setLatLng(self.map.layerPointToLatLng(closest_point));
                self.draggable_marker.addTo(self.map);
                self.draggable_marker.group_layer = matching_group_layer;
            } else {
                self.draggable_marker && self.map.removeLayer(self.draggable_marker);
            }
        };

        this.map.on('mousemove', this.drawOnMouseMove);
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
         *  Returns list of paths, and null if not found.
         */

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
