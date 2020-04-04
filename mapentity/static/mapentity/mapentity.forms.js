if (!window.MapEntity) window.MapEntity = {};

MapEntity.GeometryField = L.GeometryField.extend({

    initialize: function () {
        L.GeometryField.prototype.initialize.apply(this, arguments);
        this._initialBounds = null;
        this._resetBounds = null;
    },

    _controlDrawOptions: function () {
        // Set drawn shapes style
        var options = L.GeometryField.prototype._controlDrawOptions.call(this);
        if (options.draw.polyline === true) {
            options.draw.polyline = {shapeOptions: window.SETTINGS.map.styles.draw};
        }
        options.edit = options.edit || {};
        options.edit.edit = options.edit.edit || {};
        options.edit.edit.selectedPathOptions = L.Util.extend({dashArray: '10 10'},
                                                              window.SETTINGS.map.styles.draw);
        return options;
    },

    load: function () {
        var geometry = L.GeometryField.prototype.load.apply(this, arguments);
        // On creation, geometry is null. And marker don't have setStyle()
        if (geometry && typeof(geometry.setStyle) == 'function') {
            var style = L.Util.extend({clickable: true}, window.SETTINGS.map.styles.draw);
            geometry.setStyle(style);
        }
        return geometry;
    },

    addTo: function (map) {
        this._addExtraControls(map);
        L.GeometryField.prototype.addTo.call(this, map);
        this._addExtraLayers(map);
    },

    _addExtraControls: function (map) {
        if (map.attributionControl._map) {
            map.removeControl(map.attributionControl);
        }
        map.addControl(new L.Control.ResetView(this._getResetBounds.bind(this)));

        /*
         * Allow to load files locally.
         */
        var pointToLayer = function (feature, latlng) {
                return L.circleMarker(latlng, {style: window.SETTINGS.map.styles.filelayer})
                        .setRadius(window.SETTINGS.map.styles.filelayer.radius);
            },
            onEachFeature = function (feature, layer) {
                if (feature.properties.name) {
                    layer.bindLabel(feature.properties.name);
                }
            },
            filecontrol = L.Control.fileLayerLoad({
                fitBounds: true,
                layerOptions: {style: window.SETTINGS.map.styles.filelayer,
                               pointToLayer: pointToLayer,
                               onEachFeature: onEachFeature}
            });
        map.filecontrol = filecontrol;
        map.addControl(filecontrol);
    },

    _addExtraLayers: function (map) {
        // Layer with objects of same type
        var objectsLayer = this.buildObjectsLayer();

        // TODO remember state
        // see https://github.com/makinacorpus/Geotrek/issues/1108
        map.addLayer(objectsLayer);

        var style = objectsLayer.options.style;
        var objectsname = $('body').data('objectsname');
        var nameHTML = '<span style="color: '+ style['color'] + ';">&#x25A3;</span>&nbsp;' + objectsname;
        map.layerscontrol.addOverlay(objectsLayer, nameHTML, tr("Objects"))

        var url = this.modelLayerUrl();
        objectsLayer.load(url);
    },

    modelLayerUrl: function (modelname) {
        modelname = modelname || this.getModelName();
        return window.SETTINGS.urls.layer
                     .replace(new RegExp('modelname', 'g'), modelname);
    },

    buildObjectsLayer: function () {
        var object_pk = this.getInstancePk();
        var exclude_current_object = null;
        if (object_pk) {
            exclude_current_object = function (geojson) {
                if (geojson.properties && geojson.properties.pk)
                    return geojson.properties.pk != object_pk;
            };
        }

        // Start loading all objects, readonly
        var style = L.Util.extend({weight: 4, clickable: true},
                                  window.SETTINGS.map.styles.others);
        var objectsLayer = new L.ObjectsLayer(null, {
            style: style,
            modelname: this.getModelName(),
            filter: exclude_current_object,
            onEachFeature: function (geojson, layer) {
                if (geojson.properties.name) layer.bindLabel(geojson.properties.name);
            }
        });
        objectsLayer.on('loaded', function() {
            // Make sure it stays below other layers
            objectsLayer.bringToBack();
        });
        return objectsLayer;
    },

    _setView: function () {
        var setView = true;
        var geometry = this.store.load();
        if (!geometry || typeof(geometry.getBounds) != 'function') {
            if (MapEntity.Context.restoreLatestMapView(this._map, ['detail', 'list'])) {
                setView = false;
            }
        }
        if (setView) {
            L.GeometryField.prototype._setView.call(this);
        }

        this._initialBounds = this._map.getBounds();
        this._resetBounds = this._initialBounds;
    },

    _getResetBounds: function () {
        return this._resetBounds;
    },

    onCreated: function (e) {
        L.GeometryField.prototype.onCreated.call(this, e);
        if (!this.options.is_point || this.drawnItems.getLayers().length > 0) {
            this._resetBounds = this.drawnItems.getBounds();
        }
    },

    onDeleted: function (e) {
        L.GeometryField.prototype.onDeleted.call(this, e);
        this._resetBounds = this._initialBounds;
    },

    getModelName: function () {
        return $('body').data('modelname');
    },

    getInstancePk: function (e) {
        // On creation, this should be null
        return $('body').data('pk') || null;
    },

});
