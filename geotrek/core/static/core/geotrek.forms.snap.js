L.FieldStore.LineSnapStore = L.FieldStore.extend({

    _deserialize: function (value) {
        console.debug("Deserialize " + value);
        value = JSON.parse(value);
        value = value['geom'];
        return L.FieldStore.prototype._deserialize.call(this, value);
    },

    _serialize: function (layer) {
        var str = L.FieldStore.prototype._serialize.call(this, layer);

        var edited = layer.getLayers();
        if (edited.length === 0)
            return '';
        layer = edited[0];

        // Store snaplist
        var n = layer.getLatLngs().length,
            snaplist = new Array(n);
        if (layer.editing._poly.snapediting) {
            for (var i=0; i<n; i++) {
                var marker = layer.editing._poly.snapediting._markers[i];
                if (marker.snap && marker.snap.properties && marker.snap.properties.pk)
                    snaplist[i] = marker.snap.properties.pk;
            }
        }

        var serialized = {geom: str,
                          snap: snaplist};
        console.debug("Serialized to " + JSON.stringify(serialized));
        return JSON.stringify(serialized);
    }
});


MapEntity.GeometryField.GeometryFieldSnap = MapEntity.GeometryField.extend({
    options: {
        field_store_class: L.FieldStore.LineSnapStore
    },

    initialize: function (options) {
        MapEntity.GeometryField.prototype.initialize.call(this, options);

        L.Handler.MarkerSnap.mergeOptions({
            snapDistance: window.SETTINGS.map.snap_distance
        });

        this._geometry = null;
        this._guidesLayers = [];
        this._pathsLayer = null;
        this._objectsLayer = null;
    },

    buildObjectsLayer: function () {
        this._objectsLayer = MapEntity.GeometryField.prototype.buildObjectsLayer(arguments);
        this._guidesLayers.push(this._objectsLayer);

        if (this.getModelName() != 'path') {
            // If current model is not path, we should add the path layer
            // as a guide layer.
            this._pathsLayer = this._buildPathsLayer();
            this._guidesLayers.push(this._pathsLayer);
        }

        if (this._geometry) {
            // null if not loaded (e.g. creation form)
            this._initSnap(this._geometry);
        }

        return this._objectsLayer;
    },

    guidesLayers: function () {
        return this._guidesLayers;
    },

    _buildPathsLayer: function (objectsLayer) {
        var pathsLayer = new L.ObjectsLayer(null, {
            style: L.Util.extend(window.SETTINGS.map.styles.path, {clickable: true})
        });
        this._map.addLayer(pathsLayer);
        // Start ajax loading at last
        pathsLayer.load(this.modelLayerUrl('path'), true);

        // Propagate mouseover events, from the Path layer (on top)
        // to the objects layer (below).
        // This fixes bug #680
        (function (){
            // Reference to the object layer hovered before the path is hovered
            var overlapped = null;
            this._objectsLayer.on('mouseover', function (e) {
                overlapped = e.layer;
            });
            // On path hover, propagate events to overlapped layer
            pathsLayer.on('mouseover mouseout', function (e) {
                if (overlapped !== null) {
                    e.layer = overlapped;
                    e.target = overlapped;
                    overlapped.fire(e.type, e);
                }
                if (e.type == 'mouseout') {
                    overlapped = null;
                }
            });
        })();
    },

    _initSnap: function (layer) {
        var handlerClass = null;
        if (layer instanceof L.Marker) {
            handlerClass = L.Handler.MarkerSnap;
        }
        else if (layer instanceof L.Polyline) {
            handlerClass = L.Handler.PolylineSnap;
        }
        else {
            console.warn('Unsupported layer type for snap.');
            return;
        }
        var handler = layer.snapediting = new handlerClass(this._map, layer);
        for (var i=0, n=this._guidesLayers.length; i<n; i++) {
            handler.addGuideLayer(this._guidesLayers[i]);
        }
        handler.enable();

        // Since snapping happens only once the geometry is created.
        // We are out of Leaflet.Draw.
        layer.on('move edit', function (e) {
            this.store.save(this.drawnItems);
        }, this);
    },

    onCreated: function (e) {
        MapEntity.GeometryField.prototype.onCreated.call(this, e);
        this._initSnap(e.layer);
    },

    load: function () {
        this._geometry = MapEntity.GeometryField.prototype.load.call(this);
        return this._geometry;
    }

});
