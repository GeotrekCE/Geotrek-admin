L.ObjectsLayer = L.GeoJSON.extend({
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

    includes: L.Mixin.Events,

    initialize: function (geojson, options) {
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


        // Highlight on mouse over, using global events
        if (this.options.highlight) {
            this.on('mouseover', function(e) {
                var pk = this.getPk(e.layer);
                $(window).trigger('entity:mouseover', {pk: pk, modelname: options.modelname});
            }, this);
            this.on('mouseout', function(e) {
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
            this.on('click', function(e) {
                window.location = this.options.objectUrl(e.layer.properties, e.layer);
            }, this);
        }

        var dataurl = null;
        if (typeof(geojson) == 'string') {
            dataurl = geojson;
            geojson = null;
        }
        L.GeoJSON.prototype.initialize.call(this, geojson, this.options);

        // Fire Leaflet.Spin events
        this.on('loaded loading', function (e) {
            this.fire('data:' + e.type);
        }, this);

        if (dataurl) {
            this.load(dataurl);
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

    load: function (url) {
        console.log("load", url)
        var jsonLoad = function (data) {
            var features = jQuery.grep(data.features, function(obj, i) {
                return obj.geometry !== null;
            });
            data.features = features;
            this.addData(data);
            this.loading = false;
            this.fire('loaded');
        };
        var jsonError = function () {
            this.loading = false;
            this.fire('loaded');
            console.error("Could not load url '" + url + "'");
            if (this._map) $(this._map._container).addClass('map-error');
        };
        this.loading = true;
        this.fire('loading');
        $.getJSON(url, L.Util.bind(jsonLoad, this))
         .error(L.Util.bind(jsonError, this));
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
        var self = this,
            new_objects = {},
            already_added_layer,
            to_add_layer;

        // Gather all layer to see in new objects
        // Remove them from _current_objects if they are already shown
        // This way _current_objects will only contain layer to be removed
        $.each(pks, function(idx, to_add_pk) {
            already_added_layer = self._current_objects[to_add_pk];
            if (already_added_layer) {
                new_objects[to_add_pk] = already_added_layer;
                delete self._current_objects[to_add_pk];
            } else {
                to_add_layer = new_objects[to_add_pk] = self._objects[to_add_pk];
                // list can be ready before map, on first load
                if (to_add_layer) self.addLayer(to_add_layer);
            }
        });

        // Remove all remaining layers
        $.each(self._current_objects, function(pk, layer) {
            self.removeLayer(layer);
        });

        self._current_objects = new_objects;
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
            this.resetStyle(layer);
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