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
            var pathsLayer = new L.ObjectsLayer(null, {
                style: {weight: 2, clickable: true, color: window.SETTINGS.map.colors.paths},
            });
            map.addLayer(pathsLayer);
            snapObserver = new L.SnapObserver(map, pathsLayer);
            // Start ajax loading at last
            pathsLayer.load(module_settings.enablePathSnapping.pathsLayer_url, true);
        }
        else {
            snapObserver = new L.SnapObserver(map, objectsLayer);
        }
        if (window.DEBUG) {
            snapObserver.guidesLayer().on('click', function (e) {
            L.circleMarker(
                $(e.layer.getLatLngs()).first()[0],
                {fillColor: 'green', radius:5, color: 'green', opacity:1}
            ).addTo(map);
            L.circleMarker(
                $(e.layer.getLatLngs()).last()[0],
                {fillColor: 'red', radius:5, color: 'red', opacity:1}
            ).addTo(map);
            });
        }
        return snapObserver;
    };


    // Returns the pk of the mapentity object if it exists
    // FIXME: $('form') => fails if there are more than one form
    module.getObjectPk = function() {
        // On creation, this should be null
        return $('form input[name="pk"]').val() || null;
    };

    module.getModelName = function() {
        // Expect failure if null
        var m = $('form input[name="model"]').val() || null;
        if (!m)
            throw "No model name in form";
        return m;
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
        var color = modelname == 'path' ? window.SETTINGS.map.colors.paths : window.SETTINGS.map.colors.others;
        var objectsLayer = new L.ObjectsLayer(null, {
            style: {weight: 2, clickable: true, 'color': color},
                filter: exclude_current_object
            }),
            url = module_settings.addObjectsLayer.getUrl(modelname);
        map.addLayer(objectsLayer);
        objectsLayer.load(url);
        return objectsLayer;
    };

    module.enableMultipath = function(map, snapObserver, layerStore, onStartOver) {
        var objectsLayer = snapObserver.guidesLayer();

        var multipath_control = new L.Control.Multipath(map, objectsLayer, snapObserver, {
            handler: {
                'iconUrl': module_settings.init.iconUrl,
                'shadowUrl': module_settings.init.shadowUrl,
                'iconDragUrl': module_settings.init.iconDragUrl,
            }
        }),
        multipath_handler = multipath_control.handler;
        // Add control to the map
        map.addControl(multipath_control);

        onStartOver.on('startover', function(obj) {
            // If startover is not trigger by multipath, delete the geom
            // Thus, when multipath is called several times, the geom is not deleted
            // and may be updated
            if (obj.handler !== 'multipath') {
                multipath_handler.showPathGeom(null);
            }
            if (obj.handler == 'topologypoint') {
                // Disable multipath
                multipath_handler.reset();
                if (multipath_handler.enabled()) multipath_control.toggle();
            }
        });

        // Delete previous geom
        multipath_handler.on('enabled', function() {
            onStartOver.fire('startover', {'handler': 'multipath'});
        });

        multipath_handler.on('computed_topology', function (e) {
            layerStore.storeLayerGeomInField(e.topology);
        });
        
        objectsLayer.on('load', function() {
            $.getJSON(module_settings.enableMultipath.path_json_graph_url, function (graph) {
                // Load graph
                multipath_control.setGraph(graph);

                // We should check if the form has an error or not...
                // core.models#Topology.serialize
                var initialTopology = layerStore.getSerialized();
                if (initialTopology) {
                    if (window.DEBUG) console.log("Deserialize topology: " + initialTopology)
                    var topo =  JSON.parse(initialTopology);
                    // If it is multipath, restore
                    if (!topo.lat && !topo.lng) {
                        multipath_handler.restoreTopology(topo);
                    }
                }
            })
            .error(function (jqXHR, textStatus, errorThrown) {
                $(map._container).addClass('map-error');
                console.error("Could not load url '" + module_settings.enableMultipath.path_json_graph_url + "': " + textStatus);
                console.error(errorThrown);
            });
        });
        
        return multipath_control;
    };

    module.enableTopologyPoint = function (map, layerStore, drawncallback, onStartOver) {
        var control = new L.Control.TopologyPoint(map);
        map.addControl(control);
        
        // Delete current on first clic (start drawing)
        control.handler.on('enabled', function (e) {
            onStartOver.fire('startover', {'handler': 'topologypoint'});
        });

        control.handler.on('added', function (e) { 
            drawncallback(e.marker);
        });
        
        var initialTopology = layerStore.getSerialized();
        if (initialTopology) {
            var point =  JSON.parse(initialTopology);
            // If it is multipath, restore
            if (point.lat && point.lng) {
                drawncallback(L.marker(new L.LatLng(point.lat, point.lng)));
            }
        }
        
        return control;
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

        // Show other objects of same type
        var modelname = module.getModelName(),
            objectsLayer = module.addObjectsLayer(map, modelname);

        // Enable snapping ? Multipath need path snapping too !
        var path_snapping = module_settings.init.pathsnapping || module_settings.init.multipath,
            snapObserver = null;

        if (path_snapping) {
            L.Handler.MarkerSnapping.prototype.SNAP_DISTANCE = window.SETTINGS.map.snap_distance;
            snapObserver = module.enablePathSnapping(map, modelname, objectsLayer);
        }

        var layerStore = MapEntity.makeGeoFieldProxy($(module_settings.init.layerStoreElemSelector));
        layerStore.setTopologyMode(module_settings.init.multipath || module_settings.init.topologypoint);

        /*** <objectLayer> ***/

        function _edit_handler(map, layer) {
            var edit_handler=null;
            if (path_snapping) {
                edit_handler = L.Handler.SnappedEdit;
                if (layer instanceof L.Marker) {
                    edit_handler =  L.Handler.MarkerSnapping;
                }
            }
            else {
                edit_handler = L.Handler.PolyEdit;
                if (layer instanceof L.Marker) {
                    layer.dragging = new L.Handler.MarkerDrag(layer);
                    layer.dragging.enable();
                }
            }
            if (edit_handler) {
                layer.editing = new edit_handler(map, layer);
                layer.editing.enable();
            }
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
            _edit_handler(map, new_layer);
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
            });
            map.addLayer(objectLayer);
            objectLayer.eachLayer(function (layer) {
                onNewLayer(layer);
            });
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

        // This will make sure that we can't activate a control, while the
        // other is being used.
        var exclusive = new L.Control.ExclusiveActivation();

        if (module_settings.init.multipath) {
            var control = module.enableMultipath(map, snapObserver, layerStore, onStartOver);
            exclusive.add(control);
        }
        
        if (module_settings.init.topologypoint) {
            var control = module.enableTopologyPoint(map, layerStore, onDrawn, onStartOver);
            exclusive.add(control);
        }
    };

    return module;
};
