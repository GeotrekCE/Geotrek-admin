if (! FormField); var FormField = {};

FormField.makeModule = function(module, module_settings) {
    function getDefaultIconOpts() {
        return {
            iconUrl: module_settings.init.iconUrl,
            shadowUrl: module_settings.init.shadowUrl,
            iconSize: new L.Point(25, 41),
            iconAnchor: new L.Point(13, 41),
            popupAnchor: new L.Point(1, -34),
            shadowSize: new L.Point(41, 41)
        };
    };

    module.enableDrawing = function(map, drawncallback, startovercallback) {
        var drawControl = new L.Control.Draw({
            position: 'topright',
            polygon: module_settings.enableDrawing.is_polygon,
            rectangle: false,
            circle: false,
            marker: module_settings.enableDrawing.is_marker,
            polyline: module_settings.enableDrawing.is_polyline && {
                shapeOptions: {
                    color: '#35FF00',
                    opacity: 0.8,
                    weight: 3
                }
            }
        });
        map.addControl(drawControl);
        map.drawControl = drawControl;

        // Delete current on first clic (start drawing)
        map.on('click', function (e) {
            // Delete current on clic if drawing
            for (var handlertype in map.drawControl.handlers) {
                if (map.drawControl.handlers[handlertype].enabled()) {
                    startovercallback();
                    return;
                }
            }
        });

        // Listen to all events of creation, Leaflet.Draw naming inconsistency
        var draw_types = {
            'polyline': 'poly',
            'point': 'marker',
            'polygon': 'polygon',
        };
        for (var geomtype in draw_types) {
            var draw_type = draw_types[geomtype];
            map.on('draw:' + draw_type + '-created', L.Util.bind(function (e) {
                console.log('Drawn ' + this.type);
                var drawn = e[this.type];  // Leaflet.Draw naming inconsistency
                drawncallback(drawn);
            }, {type: draw_type}));
        }
    };


    module.enablePathSnapping = function(map, modelname, objectsLayer) {
        var snapObserver = null;
        // Snapping is always on paths layer. But only if model is not path,
        // since snapping will then be on objects layer.
        // Allows to save loading twice the same layer.
        if (modelname != 'path') {
            var pathsLayer = new MapEntity.ObjectsLayer(null, {
                style: {weight: 2, clickable: true, color: module_settings.colors.paths},
            });
            map.addLayer(pathsLayer);
            snapObserver = new MapEntity.SnapObserver(map, pathsLayer);
            // Start ajax loading at last
            pathsLayer.load(module_settings.enablePathSnapping.pathsLayer_url);
        }
        else {
            snapObserver = new MapEntity.SnapObserver(map, objectsLayer);
        }
        return snapObserver;
    };


    // Returns the pk of the mapentity object if it exists
    // FIXME: $('form') => fails if there are more than one form
    module.getObjectPk = function() {
        // On creation, this should be null
        return $('form input[name="pk"]').val() || null;
    };

    module.addObjectsLayer = function(map, modelname) {
        var object_pk = module.getObjectPk();

        var exclude_current_object = null;
        if (object_pk) {
            exclude_current_object = function (geojson) {
                if (geojson.properties && geojson.properties.pk)
                    return geojson.properties.pk != object_pk;
            }
        }

        // Start loading all objects, readonly
        var color = modelname == 'path' ? module_settings.colors.paths : module_settings.colors.others;
        var objectsLayer = new MapEntity.ObjectsLayer(null, {
            style: {weight: 2, clickable: true, 'color': color},
                filter: exclude_current_object
            }),
            url = module_settings.addObjectsLayer.getUrl(modelname);
        map.addLayer(objectsLayer);
        objectsLayer.load(url);
        return objectsLayer;
    };

    module.getMarkers = function(map, snapObserver) {
        // snapObserver and map are required to setup snappable markers
        // returns marker with an on('snap' possibility ?
        var dragging = false;
        function setDragging() { dragging = true; };
        function unsetDragging() { dragging = false; };
        function isDragging() { return dragging; };

        var markersFactory = {
            isDragging: isDragging,
            makeSnappable: function(marker) {
                marker.editing = new MapEntity.MarkerSnapping(map, marker);
                marker.editing.enable();
                snapObserver.add(marker);
                marker.on('dragstart', setDragging);
                marker.on('dragend', unsetDragging);
            },
            generic: function (latlng, layer, classname, snappable) {
                snappable = snappable === undefined ? true : snappable;

                var marker = new L.Marker(latlng, {'draggable': true, 'icon': new L.Icon(getDefaultIconOpts())});
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
                // FIXME: static
                var defaultIconOptions = getDefaultIconOpts();
                var icon = new L.Icon({
                    iconUrl: defaultIconOptions.iconUrl.replace('marker-trans.png', 'osrm_markers/marker-drag.png');
                    iconSize: new L.Point(18, 18)
                });

                var marker = new L.Marker(latlng, {'draggable': true, 'icon': icon });

                map.addLayer(marker);
                if (snappable)
                    this.makeSnappable(marker);

                return marker;
            }
        };

        return markersFactory;
    };

    module.enableMultipath = function(map, objectsLayer, layerStore, onStartOver, snapObserver) {
        var markersFactory = module.getMarkers(map, snapObserver);

        objectsLayer.on('load', function() {
            $.getJSON(module_settings.enableMultipath.path_json_graph_url, function(graph) {

                var dijkstra = {
                    'compute_path': Caminae.compute_path,
                    'graph': graph
                };

                var multipath_control = new L.Control.Multipath(map, objectsLayer, dijkstra, markersFactory)
                  , multipath_handler = multipath_control.multipath_handler
                  , cameleon = multipath_handler.cameleon
                ;

                var markPath = (function() {
                    var current_path_layer = null;
                    return {
                        'updateGeom': function(new_path_layer) {
                            var prev_path_layer = current_path_layer;
                            current_path_layer = new_path_layer;

                            if (prev_path_layer) {
                                map.removeLayer(prev_path_layer);
                                cameleon.deactivate('dijkstra_computed', prev_path_layer);
                            }

                            if (new_path_layer) {
                                map.addLayer(new_path_layer);
                                cameleon.activate('dijkstra_computed', new_path_layer);
                            }
                        }
                    }
                })();

                var drawOnMouseMove = null;

                onStartOver.on('startover', function() {
                    markPath.updateGeom(null);
                    multipath_handler.unmarkAll();

                    drawOnMouseMove && map.off('mousemove', drawOnMouseMove);
                });
                multipath_handler.on('unsnap', function () {
                    markPath.updateGeom(null);
                });
                // Delete previous geom
                multipath_handler.on('enabled', function() {
                    onStartOver.fire('startover');
                });


                // Draggable marker initialisation and step creation
                var draggable_marker = null;
                (function() {
                    function dragstart(e) {
                        var next_step_idx = draggable_marker.group_layer.step_idx + 1;
                        multipath_handler.addViaStep(draggable_marker, next_step_idx);
                    }
                    function dragend(e) {
                        draggable_marker.off('dragstart', dragstart);
                        draggable_marker.off('dragend', dragend);
                        init();
                    }
                    function init() {
                        draggable_marker = markersFactory.drag(new L.LatLng(0, 0), null, true);

                        draggable_marker.on('dragstart', dragstart);
                        draggable_marker.on('dragend', dragend);
                        map.removeLayer(draggable_marker);
                    }

                    init();
                })();

                multipath_handler.on('computed_paths', function(data) {
                    var computed_paths = data['computed_paths']
                      , new_edges = data['new_edges'];

                    var cpath, data = [], topo;
                    for (var i = 0; i < computed_paths.length; i++ ) {
                        cpath = computed_paths[i];
                        topo = createTopology(cpath, cpath.from_pop, cpath.to_pop, new_edges[i])
                        topo.from_pop = cpath.from_pop;
                        topo.to_pop = cpath.to_pop;
                        data.push(topo);
                    }

                    var group_layers = $.map(data, function(topo, idx) {
                        var polylines = $.map(topo.array_lls, function(lls) {
                            return new L.Polyline(lls);
                        });
                        // var group_layer = new L.FeatureGroup(polylines);
                        // var group_layer = new L.MultiPolyline(polylines);
                        var group_layer = new L.FeatureGroup(polylines);

                        group_layer.from_pop = topo.from_pop;
                        group_layer.to_pop = topo.to_pop;
                        group_layer.step_idx = idx;

                        return group_layer;
                    });

                    var super_layer = new L.FeatureGroup(group_layers);
                    markPath.updateGeom(super_layer);

                    // ## ONCE ##
                    drawOnMouseMove && map.off('mousemove', drawOnMouseMove);

                    var dragTimer = new Date();
                    drawOnMouseMove = function(a) {
                        var date = new Date();
                        if ((date - dragTimer) < 25) {
                            return;
                        }
                        if (markersFactory.isDragging()) {
                            return;
                        }

                        dragTimer = date;


                        for (var i = 0; i < multipath_handler.steps.length; i++) {
                            // Compare point rather than ll
                            var marker_ll = multipath_handler.steps[i].marker.getLatLng();
                            var marker_p = map.latLngToLayerPoint(marker_ll);

                            if (marker_p.distanceTo(a.layerPoint) < 10) {
                                map.removeLayer(draggable_marker);
                                return;
                            }
                        }

                        var MIN_DIST = 30;

                        var layerPoint = a.layerPoint
                          , min_dist = Number.MAX_VALUE
                          , closest_point = null
                          , matching_group_layer = null;

                        super_layer.eachLayer(function(group_layer) {
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
                            draggable_marker.setLatLng(map.layerPointToLatLng(closest_point));
                            draggable_marker.addTo(map);
                            draggable_marker.group_layer = matching_group_layer;
                        } else {
                            map.removeLayer(draggable_marker);
                        }
                    };

                    map.on('mousemove', drawOnMouseMove);

                    // assemble topologies
                    var positions = data[0].topology.positions
                      , paths = data[0].topology.paths;

                    for (var k = 1; k < data.length; k++) {
                        var data_topology = data[k].topology;
                        // substract one as we delete first position
                        var offset = paths.length - 1;

                        // avoid the first one
                        paths = paths.concat(data_topology.paths.slice(1));

                        delete data_topology.positions[0]
                        $.each(data_topology.positions, function(k, v) {
                            positions[parseInt(k) + offset] = v;
                        });
                    }

                    var topology = {
                        offset: 0,  // TODO: input for offset
                        positions: positions,
                        paths: paths
                    };
                    layerStore.storeLayerGeomInField(topology);
                });

                function createTopology(computed_path, from_pop, to_pop, new_edges) {
                    var ll_start = from_pop.ll
                      , ll_end = to_pop.ll;

                    var paths = $.map(new_edges, function(edge) { return edge.id; });
                    var layers = $.map(new_edges, function(edge) { return objectsLayer.getLayer(edge.id); });

                    var polyline_start = layers[0];
                    var polyline_end = layers[layers.length -1];

                    var percentageDistance = MapEntity.Utils.getPercentageDistanceFromPolyline;

                    var start = percentageDistance(ll_start, polyline_start)
                      , end = percentageDistance(ll_end, polyline_end);

                    if (!start || !end)
                        return;  // TODO: clean-up before give-up ?

                    var new_topology = Caminae.TopologyHelper.buildTopologyGeom(layers, ll_start, ll_end, start, end);

                    if (new_topology.is_single_path) {
                        if (paths.length > 1) {
                            // Only get the first one
                            paths = paths.slice(0, 1);
                        }
                    }

                    var sorted_positions = {};
                    $.each(new_topology.positions, function(k, v) {
                        sorted_positions[k] = v.sort()
                    });

                    var topology = {
                        offset: 0,  // TODO: input for offset
                        positions: sorted_positions,
                        paths: paths
                    };

                    return {
                        topology: topology
                      , array_lls: new_topology.latlngs
                    };
                }

                map.addControl(multipath_control);

                var initialTopology = layerStore.getSerialized();

                // We should check if the form has an error or not...
                // core.models#TopologyMixin.serialize
                if (initialTopology) {
                    // This topology should contain postgres calculated value (start/end point as latln)
                    var topo =  JSON.parse(initialTopology)
                      , paths = topo.paths
                      , positions = topo.positions;

                    // Only first and last positions
                    if (paths.length == 1) {
                        // There is only one path, both positions values are relevant
                        // and each one represents a marker
                        var first_pos = positions[0][0];
                        var last_pos = positions[0][1];

                        var start_layer = objectsLayer.getLayer(paths[0]);
                        var end_layer = objectsLayer.getLayer(paths[paths.length - 1]);

                        var start_ll = MapEntity.Utils.getLatLngFromPos(map, start_layer, [ first_pos ])[0];
                        var end_ll = MapEntity.Utils.getLatLngFromPos(map, end_layer, [ last_pos ])[0];

                        var state = {
                            start_ll: start_ll,
                            end_ll: end_ll,
                            start_layer: start_layer,
                            end_layer: end_layer
                        };
                        multipath_handler.setState(state);

                    } else {

                        var layer_ll_s = [];
                        $.each(positions, function(k, pos) {
                            // default value: this is not supposed to be a marker ?!
                            if (pos[0] == 0 && pos[1] == 1)
                                return;

                            var path_idx = parseInt(k);
                            var layer = objectsLayer.getLayer(paths[path_idx]);
                            // Look for the relevant value:
                            // 0 is the default in first_position, get the other value
                            var used_pos = pos[0] == 0 ? pos[1] : pos[0];

                            var ll = MapEntity.Utils.getLatLngFromPos(map, layer, [ used_pos ])[0];

                            layer_ll_s.push({
                                layer: layer,
                                ll: ll
                            });
                        });

                        var start_layer_ll = layer_ll_s.shift();
                        var end_layer_ll = layer_ll_s.pop();

                        var via_markers = $.map(layer_ll_s, function(layer_ll) {
                            return {
                                layer: layer_ll.layer,
                                marker: markersFactory.drag(layer_ll.ll, null, true)
                            };
                        });

                        var state = {
                            start_ll: start_layer_ll.ll,
                            end_ll: end_layer_ll.ll,
                            start_layer: start_layer_ll.layer,
                            end_layer: end_layer_ll.layer,
                            via_markers: via_markers
                        };

                        multipath_handler.setState(state);
                    }
                }

            });
        });
    };

    module.enableTopologyPoint = function (map, drawncallback, onStartOver) {
        var control = new L.Control.TopologyPoint(map);
            handler = control.topologyhandler;
        map.addControl(control);
        
        // Delete current on first clic (start drawing)
        map.on('click', function (e) {
            if (handler.enabled()) {
                onStartOver.fire('startover');
                return;
            }
        });

        handler.on('added', function (e) { drawncallback(e.marker) });
    };
    
    module.init = function(map, bounds, fitToBounds) {
        fitToBounds = fitToBounds === undefined ? true : fitToBounds;

        map.removeControl(map.attributionControl);

        map.addControl(new L.Control.Measurement());

        /*** <Map bounds and reset> ***/

        var initialBounds = bounds,
            objectBounds = module_settings.init.objectBounds,
            currentBounds = objectBounds || initialBounds;

        var getBounds = function () {
            return currentBounds;
        };

        if (fitToBounds) {
            map.fitBounds(currentBounds);
        }

        map.addControl(new L.Control.ResetView(getBounds));
        map.addControl(new L.Control.Scale());

        // Show other objects of same type
        var modelname = $('form input[name="model"]').val(),
            objectsLayer = module.addObjectsLayer(map, modelname);

        // Enable snapping ? Multipath need path snapping too !
        var path_snapping = module_settings.init.pathsnapping || module_settings.init.multipath,
            snapObserver = null;
        MapEntity.MarkerSnapping.prototype.SNAP_DISTANCE = module_settings.enablePathSnapping.SNAP_DISTANCE;

        if (path_snapping) {
            snapObserver = module.enablePathSnapping(map, modelname, objectsLayer);
        }

        var layerStore = MapEntity.makeGeoFieldProxy($(module_settings.init.layerStoreElemSelector));
        layerStore.setTopologyMode(module_settings.init.multipath || module_settings.init.topologypoint);

        /*** <objectLayer> ***/

        function _edit_handler(map, layer) {
            var edit_handler = L.Handler.PolyEdit;
            if (path_snapping) {
                edit_handler = L.Handler.SnappedEdit;
                if (layer instanceof L.Marker) {
                    edit_handler =  MapEntity.MarkerSnapping;
                }
            }
            return new edit_handler(map, layer);
        };

        function onNewLayer(new_layer) {
            if (new_layer instanceof L.Marker) {
                currentBounds = map.getBounds(); // A point has no bounds, take map bounds
                // Set custom icon, using CSS instead of JS
                new_layer.setIcon(new L.Icon(getDefaultIconOpts()));
                $(new_layer._icon).addClass('marker-add');
                
            }
            else {
                currentBounds = new_layer.getBounds();
            }
            new_layer.editing = _edit_handler(map, new_layer);
            new_layer.editing.enable();
            new_layer.on('move edit', function (e) {
                layerStore.storeLayerGeomInField(e.target);
            });
            layerStore.storeLayerGeomInField(new_layer);
            if (snapObserver) snapObserver.add(new_layer);
        }

        var geojson = module_settings.init.geojson;  // If no field, will be null.
        if (geojson) {
            var objectLayer = new L.GeoJSON(geojson, {
                style: {weight: 5, opacity: 1, clickable: true},
                onEachFeature: function (feature, layer) {
                    onNewLayer(layer);
                }
            });
            map.addLayer(objectLayer);
        }
        else {
            // If no geojson is provided, we may be editing a topology
            var topology = $(module_settings.init.layerStoreElemSelector).val();
            if (topology) {
                var point = JSON.parse(topology);
                // Point topology
                if (point.lat && point.lng) {
                    var existing = new L.Marker(new L.LatLng(point.lat, point.lng)).addTo(map)
                    onNewLayer(existing);
                }
                else {
                    //TODO : line topology !
                }
            }
        }

        /*** </objectLayer> ***/

        /*** <drawing> ***/

        var onDrawn = function (drawn_layer) {
            map.addLayer(drawn_layer);
            onNewLayer(drawn_layer);
        };

        var onStartOver = L.Util.extend({}, L.Mixin.Events);
        onStartOver.on('startover', removeLayerFromLayerStore);

        function removeLayerFromLayerStore() {
            var old_layer = layerStore.getLayer();
            if (old_layer) {
                map.removeLayer(old_layer);
                if (snapObserver) snapObserver.remove(old_layer);
                currentBounds = initialBounds;
                layerStore.storeLayerGeomInField(null);
            }
        };
        
        if (module_settings.init.enableDrawing) {
            module.enableDrawing(map, onDrawn, removeLayerFromLayerStore);
        }

        if (module_settings.init.multipath) {
            module.enableMultipath(map, snapObserver.guidesLayer(), layerStore, onStartOver, snapObserver);
        }
        
        if (module_settings.init.topologypoint) {
            module.enableTopologyPoint(map, onDrawn, onStartOver);
        }
    };

    return module;
};
