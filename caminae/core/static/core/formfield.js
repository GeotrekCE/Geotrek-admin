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
                style: {weight: 2, clickable: true},
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


    module.addObjectsLayer = function(map, modelname) {
        // On creation, this should be null
        var object_pk = $('form input[name="pk"]').val() || null;

        var exclude_current_object = null;
        if (object_pk) {
            exclude_current_object = function (geojson) {
                if (geojson.properties && geojson.properties.pk)
                    return geojson.properties.pk != object_pk;
            }
        }

        // Start loading all objects, readonly
        var objectsLayer = new MapEntity.ObjectsLayer(null, {
                style: {weight: 2, clickable: true},
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
        var markerFactory = {
            generic: function (latlng, layer, classname) {
                var marker = new L.Marker(latlng, {'draggable': true, 'icon': new L.Icon(getDefaultIconOpts())});
                map.addLayer(marker);
                $(marker._icon).addClass(classname);
                marker.editing = new MapEntity.MarkerSnapping(map, marker);
                marker.editing.enable();
                snapObserver.add(marker);
                // marker.on('snap', function() {});
                return marker;
            },
            source: function(latlng, layer) {
                return this.generic(latlng, layer, 'marker-source');
            },
            dest: function(latlng, layer) {
                return this.generic(latlng, layer, 'marker-target');
            }
        };

        return markerFactory;
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

                onStartOver.on('startover', function() {
                    markPath.updateGeom(null);
                    multipath_handler.unmarkAll();
                });

                // Delete previous geom
                multipath_handler.on('enabled', function() {
                    onStartOver.fire('startover');
                });


                // Returns true if the first point of the polyline
                // is shared with one of the edge of the polyline
                function getOrder(polyline, next_polyline) {
                    var ll_p = polyline.getLatLngs()[0];

                    var lls = next_polyline.getLatLngs()
                      , ll_a = lls[0]
                      , ll_b = lls[lls.length - 1];

                    return ll_p.equals(ll_a) || ll_p.equals(ll_b);
                }

                function buildTopologyGeom(polylines, ll_start, ll_end, closest_first_idx, closest_end_idx) {
                    var polyline_start = polylines[0]
                      , polyline_end = polylines[polylines.length - 1]
                      , polylines_inner = polylines.slice(1, -1);

                    // Is the first point bound to the next edge or is it the other way ?

                    var lls_tmp, lls_end, latlngs = [];

                    if (getOrder(polyline_start, polylines_inner[0])) {
                        // <--o-c- x---x---x // first point is shared ; include closest
                        lls_tmp = polyline_start.getLatLngs().slice(0, closest_first_idx + 1)
                        lls_tmp.push(ll_start);
                    } else {
                        // -c-o--> x---x---x // first point is not shared ; don't include closest
                        lls_tmp = polyline_start.getLatLngs().slice(closest_first_idx + 1);
                        lls_tmp.unshift(ll_start);
                    }

                    latlngs.push(lls_tmp);

                    $.each(polylines_inner, function(idx, l) {
                        latlngs.push(l.getLatLngs());
                    });

                    if (getOrder(polyline_end, polylines_inner[polylines_inner.length - 1])) {
                        // x---x---x -c-o--> // first point is shared ; include closest
                        lls_tmp = polyline_end.getLatLngs().slice(0, closest_end_idx + 1);
                        lls_tmp.push(ll_end);
                    } else {
                        // x---x---x <--o-c- // first point is not shared ; don't include closest
                        lls_tmp = polyline_end.getLatLngs().slice(closest_end_idx + 1);
                        lls_tmp.unshift(ll_end);
                    }

                    latlngs.push(lls_tmp);

                    return new L.MultiPolyline(latlngs);
                }


                multipath_handler.on('computed_paths', function(data) {
                    var new_edges = data['new_edges']
                      , marker_source = data['marker_source']
                      , marker_dest = data['marker_dest']
                      , ll_start = marker_source.getLatLng()
                      , ll_end = marker_dest.getLatLng();

                    var paths = $.map(new_edges, function(edge) { return edge.id; });
                    var layers = $.map(new_edges, function(edge) { return objectsLayer.getLayer(edge.id); });

                    var polyline_start = layers[0];
                    var polyline_end = layers[layers.length -1];

                    var percentageDistance = MapEntity.Utils.getPercentageDistanceFromPolyline;

                    var start = percentageDistance(ll_start, polyline_start)
                      , end = percentageDistance(ll_end, polyline_end)
                      , start_closest_idx = start.closest
                      , end_closest_idx = end.closest
                    ;

                    var new_topology_geom = buildTopologyGeom(layers, ll_start, ll_end, start_closest_idx, end_closest_idx);
                    markPath.updateGeom(new_topology_geom);

                    // visual check
                    if (false) {
                        // Highlight segments to clearly see start and end
                        cameleon.activate('highlight', polyline_start);
                        cameleon.activate('highlight', polyline_end);
                        // Highligh the start point to see the order of points in the polyline
                        new L.Marker(polyline_start.getLatLngs()[0], {'opacity': 0.5}).addTo(map);
                        new L.Marker(polyline_end.getLatLngs()[0], {'opacity': 0.5}).addTo(map);
                        // Check the chosen point from which the distance was calculated
                        new L.Marker(start.closest).addTo(map);
                        new L.Marker(end.closest).addTo(map);
                    }

                    var topology = {
                        offset: 0,  // TODO: input for offset
                        start: start.distance,
                        end: end.distance,
                        paths: paths,
                        // Won't be on django side but in case there is a form error, will be there !
                        start_point: {lat: ll_start.lat, lng: ll_start.lng },
                        end_point: {lat: ll_end.lat, lng: ll_end.lng }
                    };
                    layerStore.storeLayerGeomInField(topology);
                });

                map.addControl(multipath_control);

                var initialTopology = layerStore.getSerialized();

                // We should check if the form has an error or not...
                // core.models#TopologyMixin.serialize
                if (initialTopology) {
                    // This topology should contain postgres calculated value (start/end point as latln)
                    var topo =  JSON.parse(initialTopology);
                    var state = {
                        start_ll: new L.LatLng(topo.start_point.lat, topo.start_point.lng),
                        end_ll: new L.LatLng(topo.end_point.lat, topo.end_point.lng),
                        start_layer: objectsLayer.getLayer(topo.paths[0]),
                        end_layer: objectsLayer.getLayer(topo.paths[topo.paths.length - 1])
                    };
                    multipath_handler.setState(state);
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
    
    module.init = function(map, bounds) {
        map.removeControl(map.attributionControl);

        /*** <Map bounds and reset> ***/

        var initialBounds = bounds,
            objectBounds = module_settings.init.objectBounds,
            currentBounds = objectBounds || initialBounds;
        getBounds = function () {
            return currentBounds;
        };
        map.addControl(new L.Control.ResetView(getBounds));
        map.fitBounds(currentBounds);
        map.addControl(new L.Control.Scale());

        // Show other objects of same type
        var modelname = $('form input[name="model"]').val(),
            objectsLayer = module.addObjectsLayer(map, modelname);

        // Enable snapping ? Multipath need path snapping too !
        var path_snapping = module_settings.init.pathsnapping || module_settings.init.multipath,
            snapObserver = null;
        MapEntity.MarkerSnapping.prototype.SNAP_DISTANCE = module_settings.enablePathSnapping.SNAP_DISTANCE;
        MapEntity.SnapObserver.prototype.MIN_SNAP_ZOOM = module_settings.enablePathSnapping.MIN_SNAP_ZOOM;

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
            module.enableDrawing(map, onDrawn, onStartOver);
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
