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

        // Show control as enabled on activation
        for (var h in map.drawControl.handlers) {
            map.drawControl.handlers[h].on('activated', function () {
                $('.leaflet-control-draw-' + h).parent().addClass('enabled');
            });
        }

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
                
                // Show control as disabled after creation
                for (var h in map.drawControl.handlers) {
                    $('.leaflet-control-draw-' + h).parent().removeClass('enabled');
                }
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
        if (!modelname) {
            throw 'Model name is empty';
        }
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
                marker.editing = new MapEntity.MarkerSnapping(map, marker);
                snapObserver.add(marker);
                marker.activate_cbs.push(activate);
                marker.deactivate_cbs.push(deactivate);

                marker.activate();
            },
            generic: function (latlng, layer, classname, snappable) {
                snappable = snappable === undefined ? true : snappable;

                var marker = new L.ActivableMarker(latlng, {'draggable': true, 'icon': new L.Icon(getDefaultIconOpts())});
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
                    iconUrl: module_settings.init.iconDragUrl,
                    iconSize: new L.Point(18, 18)
                });

                var marker = new L.ActivableMarker(latlng, {'draggable': true, 'icon': icon });

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

            var parseGraph = function (graph) {

                var multipath_control = new L.Control.Multipath(map, objectsLayer, graph, markersFactory)
                  , multipath_handler = multipath_control.multipath_handler
                  , cameleon = multipath_handler.cameleon
                ;

                // TODO: remove drawOnMouseMove
                var drawOnMouseMove = null;

                onStartOver.on('startover', function(obj) {
                    // If startover is not trigger by multipath, delete the geom
                    // Thus, when multipath is called several times, the geom is not deleted
                    // and may be updated
                    if (obj.handler !== 'multipath') {
                        multipath_handler.showPathGeom(null);
                    }
                    if (obj.handler == 'topologypoint') {
                        // Disable multipath
                        if (multipath_handler.enabled()) multipath_control.toggle();
                    }
                });
                multipath_handler.on('unsnap', function () {
                    multipath_handler.showPathGeom(null);
                });
                // Delete previous geom
                multipath_handler.on('enabled', function() {
                    onStartOver.fire('startover', {'handler': 'multipath'});
                });
                multipath_handler.on('disabled', function() {
                    drawOnMouseMove && map.off('mousemove', drawOnMouseMove);
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
                    multipath_handler.showPathGeom(super_layer);

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
                      , paths = data[0].topology.paths
                      , ioffset = paths.length - 1;

                    for (var k = 1; k < data.length; k++) {
                        var data_topology = data[k].topology;
                        
                        // Merge paths of sub computed paths, without its first element
                        paths = paths.concat(data_topology.paths.slice(1));

                        delete data_topology.positions[0]
                        $.each(data_topology.positions, function(key, pos) {
                            positions[parseInt(key) + ioffset] = pos;
                        });
                    }
            
                    // All middle computed paths are constraints points
                    // We want them to have start==end. 
                    var i = 0;
                    for (var key in positions) {
                        if (i > 0 && i < paths.length -1) {
                            var pos = positions[key];
                            /* make sure pos will be [X, X]
                               [0, X] or [X, 1] --> X
                               [0.0, 1.0] --> 0.0
                               [1.0, 1.0] --> 1.0 */
                            var x = -1;
                            if      (pos[0] == 0.0 && pos[1] == 1.0) x = 0.0;
                            else if (pos[0] == 1.0 && pos[1] == 1.0) x = 1.0;
                            else if (pos[1] == 1.0) x = pos[0];
                            else if (pos[0] == 0.0) x = pos[1];
                            positions[key] = [x, x];
                        }
                        i++;
                    }

                    var topology = {
                        offset: 0,  // TODO: input for offset
                        positions: positions,
                        paths: paths
                    };
                    layerStore.storeLayerGeomInField(topology);
                });

                function createTopology(computed_path, from_pop, to_pop, edges) {
                    /**
                     * @param computed_path: cf ``_onComputedPaths`` in ``L.Handler.Multipath``
                     * @param from_pop: start PointOnPolyline
                     * @param to_pop: end PointOnPolyline
                     * @param edges: list of edges (cf JSON graph)
                     */
                    var ll_start = from_pop.ll
                      , ll_end = to_pop.ll;

                    var paths = $.map(edges, function(edge) { return edge.id; });
                    var layers = $.map(edges, function(edge) { return objectsLayer.getLayer(edge.id); });

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
                    var topo =  JSON.parse(initialTopology);
                    // If it is multipath, restore
                    if (topo.paths && !topo.lat && !topo.lng) {
                        multipath_handler.restoreTopology(topo);
                    }
                }
            };
            
            $.getJSON(module_settings.enableMultipath.path_json_graph_url, parseGraph).error(function (jqXHR, textStatus, errorThrown) {
                $(map._container).addClass('map-error');
                console.error("Could not load url '" + module_settings.enableMultipath.path_json_graph_url + "': " + textStatus);
                console.error(errorThrown);
            });
        });
    };

    module.enableTopologyPoint = function (map, drawncallback, onStartOver) {
        var control = new L.Control.TopologyPoint(map)
          , handler = control.topologyhandler;
        map.addControl(control);
        
        // Delete current on first clic (start drawing)
        handler.on('enabled', function (e) {
            onStartOver.fire('startover', {'handler': 'topologypoint'});
        });

        handler.on('added', function (e) { 
            drawncallback(e.marker);
        });
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

        /*** </objectLayer> ***/

        /*** <drawing> ***/

        var onDrawn = function (drawn_layer) {
            map.addLayer(drawn_layer);
            onNewLayer(drawn_layer);
        };

        var removeLayerFromLayerStore = function () {
            var old_layer = layerStore.getLayer();
            if (old_layer) {
                map.removeLayer(old_layer);
                if (snapObserver) snapObserver.remove(old_layer);
                currentBounds = initialBounds;
                layerStore.storeLayerGeomInField(null);
            }
        };

        var onStartOver = L.Util.extend({}, L.Mixin.Events);
        onStartOver.on('startover', removeLayerFromLayerStore);
        
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
