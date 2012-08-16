if (! FormField); var FormField = {};

FormField.makeModule = function(module, module_settings) {

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
        MapEntity.SnapObserver.MIN_SNAP_ZOOM = module_settings.enablePathSnapping.MIN_SNAP_ZOOM;
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

    module.enableMultipath = function(map, objectsLayer, layerStore) {
        objectsLayer.on('load', function() {
            $.getJSON(module_settings.enableMultipath.path_json_graph_url, function(graph) {

                var dijkstra = {
                    'compute_path': Caminae.compute_path,
                    'graph': graph
                };

                var multipath_control = new L.Control.Multipath(map, objectsLayer, dijkstra);
                multipath_control.multipath_handler.on('computed_paths', function(data) {
                    var new_edges = data['new_edges'],
                        paths = [];
                    for (var i=0; i<new_edges.length; i++) {
                        paths.push({
                            start: 0.0,  // TODO: until now, always start at 0
                            end: 1.0,
                            path: new_edges[i].id
                        });
                    }
                    var topology = {
                        offset: 0,  // TODO: input for offset
                        paths: paths,
                    };
                    layerStore.storeTopologyInField(topology);
                });

                map.addControl(multipath_control);

            });
        });
    };

    module.init = function(map, bounds) {
        map.removeControl(map.attributionControl);

        /*** <Map bounds and reset> ***/

        var initialBounds = bounds,
            objectBounds = module_settings.init.objectsBounds,
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

        // Enable snapping ?
        var path_snapping = module_settings.init.pathsnapping;
        var snapObserver = null;
        if (path_snapping) {
            snapObserver = module.enablePathSnapping(map, modelname, objectsLayer);
        }

        var layerStore = MapEntity.makeGeoFieldProxy($(module_settings.init.layerStoreElemSelector));

        /*** <objectLayer> ***/

        var geojson = module_settings.init.geojson;  // If no field, will be null.
        var objectLayer = new L.GeoJSON(geojson, {
            style: {weight: 5, opacity: 1, clickable: true},
            onEachFeature: function (feature, layer) {
                onNewLayer(layer);
            }
        });
        map.addLayer(objectLayer);

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
                new_layer.setIcon(new L.Icon({
                    iconUrl: module_settings.init.iconUrl,
                    shadowUrl: module_settings.init.shadowUrl,
                    iconSize: new L.Point(25, 41),
                    iconAnchor: new L.Point(13, 41),
                    popupAnchor: new L.Point(1, -34),
                    shadowSize: new L.Point(41, 41)
                }));
                $(new_layer._icon).addClass('marker-add');
            }
            else {
                currentBounds = new_layer.getBounds();
            }
            new_layer.editing = _edit_handler(map, new_layer);
            new_layer.editing.enable();
            new_layer.on('edit', function (e) {
                layerStore.storeLayerGeomInField(e.target);
            });
            layerStore.storeLayerGeomInField(new_layer);
            if (snapObserver) snapObserver.add(new_layer);
        }

        /*** </objectLayer> ***/

        /*** <drawing> ***/

        module.enableDrawing(map,
            function (drawn_layer) {
                map.addLayer(drawn_layer);
                onNewLayer(drawn_layer);
            },
            function () {
                var old_layer = layerStore.getLayer();
                if (old_layer) {
                    map.removeLayer(old_layer);
                    if (snapObserver) snapObserver.remove(old_layer);
                    currentBounds = initialBounds;
                    layerStore.storeLayerGeomInField(null);
                }
            }
        );

        // TODO: I NEED paths.geojson ; have a function to get it
        var path_layer = snapObserver._guidesLayer; // objectsLayer,

        if (module_settings.init.multipath) {
            // {{ module }}EnableMultipath(map, objectsLayer, layerStore)
            module.enableMultipath(map,
                path_layer,
                layerStore
            );
        }
    };

    return module;
};
