L.SingleObjectLayer = L.GeoJSON.extend({
    options: {
        styles: {
            'default': {'color': 'blue', 'weight': 2, 'opacity': 0.8},
            highlight: {'color': 'red', 'weight': 5, 'opacity': 1},
            select: {'color': 'red', 'weight': 7, 'opacity': 1}
        },
        pointToLayer: function (geojson, latlng) {
            return new L.CircleMarker(latlng);
        }
    },

    includes: L.Evented.prototype,
});

L.ObjectsLayer = L.GeoJSONTileLayer.extend({
    options: {
        indexing: true,
        highlight: true,
        objectUrl: null,
        styles: {
            'default': {'color': 'blue', 'weight': 2, 'opacity': 0.8},
            highlight: {'color': 'red', 'weight': 5, 'opacity': 1},
            select: {'color': 'red', 'weight': 7, 'opacity': 1}
        }
    },

    includes: L.Evented.prototype,

    initialize: function (url, options) {
        // Pointers to all layers by pk - immutable
        this._objects = {};
        // Hold the currently visible layers (subset of _objects)
        this._current_objects = {};
        this.loading = false;

        options = L.Util.extend({}, options);

        var onFeatureParse = function (geojson, layer) {
            this._mapObjects(geojson, layer);
            if (this._onEachFeature) {
                this._onEachFeature(geojson, layer);
            }
        };
        var pointToLayer = function (geojson, latlng) {
            if (this._pointToLayer) return this._pointToLayer(geojson, latlng);
            if (geojson.geometry.type === "Point" && geojson.properties.radius) {
                return new L.Circle(latlng, geojson.properties.radius);
            }
            return new L.CircleMarker(latlng);
        };
        this._onEachFeature = options.onEachFeature;
        options.onEachFeature = L.Util.bind(onFeatureParse, this);
        this._pointToLayer = options.pointToLayer;
        options.pointToLayer = L.Util.bind(pointToLayer, this);

        options.style = options.style || L.Util.extend({}, this.options.styles['default']);
        L.Util.setOptions(this, options);
        this.options.styles = L.Util.extend({}, this.options.styles);
        this.options.styles['default'] = L.Util.extend({}, this.options.style);
        this.options.updateWhenZooming = false;  // Better perfs

        L.GeoJSONTileLayer.prototype.initialize.call(this, url, this.options);

        // Highlight on mouse over, using global events
        if (this.options.highlight) {
            this.layer.on('mouseover', function(e) {
                var pk = this.getPk(e.layer);
                $(window).trigger('entity:mouseover', {pk: pk, modelname: options.modelname});
            }, this);
            this.layer.on('mouseout', function(e) {
                var pk = this.getPk(e.layer);
                $(window).trigger('entity:mouseout', {pk: pk, modelname: options.modelname});
            }, this);
        }
        // Listen to external events, such as those fired from this layer, and
        // from DOM (in detail pages, see ``hoverable`` CSS selector)
        $(window).on('entity:mouseover', L.Util.bind(function (e, data) {
            if (data.modelname == options.modelname) {
                this.highlight(data.pk, true);
            }
        }, this));
        $(window).on('entity:mouseout', L.Util.bind(function (e, data) {
            if (data.modelname == options.modelname) {
                this.highlight(data.pk, false);
            }
        }, this));

        // Optionnaly make them clickable
        if (this.options.objectUrl) {
            this.layer.on('click', function(e) {
                window.location = this.options.objectUrl(e.layer.feature.id);
            }, this);
        }
    },

    _mapObjects: function (geojson, layer) {
        var pk = this.getPk(geojson);
        this._objects[pk] = this._current_objects[pk] = layer;
        layer.properties = geojson.properties;
        this.indexLayer(layer);

        // Fix highlighting of multi-part geometries:
        // Propagate GeoJSON properties to sub-layers
        if (typeof layer.eachLayer == 'function') {
            layer.eachLayer(function (l) {
                l.properties = geojson.properties;
            });
        }
    },

    getLayer: function (pk) {
        return this._objects[pk];
    },

    getPk: function(layer) {
        // pk (primary-key) in properties
        if (layer.properties && layer.properties.pk)
            return layer.properties.pk;
        // id of geojson feature
        if (layer.id !== undefined)
            return layer.id;
        // leaflet internal layer id
        return L.Util.stamp(layer);
    },

    // Show all layers matching the pks
    updateFromPks: function(pks) {
        console.log("Should filter map features again");
    },

    getCurrentLayers: function () {
        /*
        Return layers currently on map.
        This differs from this._objects, which contains all layers
        loaded from initial GeoJSON data.
        */
        return this._current_objects;
    },

    jumpTo: function (pk) {
        var layer = this.getLayer(pk);
        if (!layer) return;
        this._map.fitBounds(layer.getBounds());
    },

    highlight: function (pk, on) {
        var layer = this.getLayer(pk);
        on = on === undefined ? true : on;
        if (!layer) return;

        if (on) {
            layer.setStyle(this.options.styles.highlight);
            this.fire('highlight', {layer: layer});
        }
        else {
            this.layer.resetStyle(layer);
        }
    },

    select: function(pk, on) {
        var layer = this.getLayer(pk);
        on = on === undefined ? true : on;
        if (!layer) return;

        if (on) {
            layer._defaultStyle = this.options.styles.select;
            layer.setStyle(layer._defaultStyle);
            this.fire('select', {layer: layer});
        }
        else {
            layer._defaultStyle = this.options.styles['default'];
            layer.setStyle(layer._defaultStyle);
        }
    }
});


L.ObjectsLayer.include(L.LayerIndexMixin);