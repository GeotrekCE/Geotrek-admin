L.ObjectsLayer = L.GeoJSON.extend({
    options: {
        indexing: true,
        highlight: true,
        objectUrl: null,
        styles: {
            default: {'color': 'blue', 'weight': 2, 'opacity': 0.8},
            highlight: {'color': 'red', 'weight': 5, 'opacity': 1},
            select: {'color': 'red', 'weight': 7, 'opacity': 1},
        }
    },

    includes: L.Mixin.Events,

    initialize: function (geojson, options) {
        // Pointers to all layers by pk - immutable
        this._objects = {};
        // Hold the currently visible layers (subset of _objects)
        this._current_objects = {};
        this.rtree = new RTree();
        this.spinning = false;
        this.loading = false;

        var options = options || {};

        var onFeatureParse = function (geojson, layer) {
            this._mapObjects(geojson, layer);
            if (this._onEachFeature) this._onEachFeature(geojson, layer);
        };
        var pointToLayer = function (geojson, latlng) {
            if (this._pointToLayer) return this._pointToLayer(geojson, latlng);
            return new L.CircleMarker(latlng);
        };
        this._onEachFeature = options.onEachFeature;
        options.onEachFeature = L.Util.bind(onFeatureParse, this);
        this._pointToLayer = options.pointToLayer;
        options.pointToLayer = L.Util.bind(pointToLayer, this);

        options.style = options.style || this.options.styles.default;
        L.Util.setOptions(this, options);
        this.options.styles.default = options.style || this.options.styles.default;

        // Highlight on mouse over
        if (this.options.highlight) {
            this.on('mouseover', function(e) {
                this.highlight(e.layer.properties.pk);
            }, this);
            this.on('mouseout', function(e) {
                this.highlight(e.layer.properties.pk, false);
            }, this);
        }

        // Optionnaly make them clickable
        if (this.options.objectUrl) {
            this.on('dblclick', function(e) {
                window.location = this.options.objectUrl(e.layer.properties, e.layer);
            }, this);
        }

        var dataurl = null;
        if (typeof(geojson) == 'string') {
            dataurl = geojson;
            geojson = null;
        }
        L.GeoJSON.prototype.initialize.call(this, geojson, this.options);

        if (dataurl) {
            this.load(dataurl);
        }
    },

    _rtbounds: function (bounds) {
        return {x: bounds.getSouthWest().lng,
                y: bounds.getSouthWest().lat,
                w: bounds.getSouthEast().lng - bounds.getSouthWest().lng,
                h: bounds.getNorthWest().lat - bounds.getSouthWest().lat};
    },

    _mapObjects: function (geojson, layer) {
        var pk = geojson.properties.pk
        this._objects[pk] = this._current_objects[pk] = layer;
        layer.properties = geojson.properties;
        
        // Spatial indexing
        if (!this.options.indexing)
            return;
        var bounds = null;
        if (layer instanceof L.MultiPolyline) {
            bounds = new L.LatLngBounds();
            for (var i in layer._layers) {
                bounds.extend(layer._layers[i].getBounds());
            }
        }
        else if (layer instanceof L.FeatureGroup) {
            // Leaflet uses project() in Circle's getBounds() method.
            // We cannot call it yet, we are adding the feature to the map.
            // Thus, rewrote that part and switch on Circle.
            bounds = new L.LatLngBounds();
            for (var i in layer._layers) {
                var sublayer = layer._layers[i];
                if (sublayer instanceof L.Circle)
                    bounds.extend(sublayer.getLatLng());
                else
                    bounds.extend(sublayer.getBounds());
            }
        }
        else if (typeof layer.getLatLngs == 'function') {
            bounds = layer.getBounds();
        }
        else if (typeof layer.getLatLng == 'function') {
            bounds = new L.LatLngBounds(layer.getLatLng(), layer.getLatLng());
        }
        if (bounds.getSouthWest() && bounds.getNorthEast())
            this.rtree.insert(this._rtbounds(bounds), layer);
        else
            console.error("No bounds found for layer " + pk);
    },

    onRemove: function (map) {
        this.spin(false, map);
        L.GeoJSON.prototype.onRemove.call(this, map);
    },

    onAdd: function (map) {
        this.spin(this.spinning, map);
        L.GeoJSON.prototype.onAdd.call(this, map);
    },

    spin: function (state, map) {
        var _map = map || this._map;
        this.spinning = state;
        
        if (!_map) return;

        if (state) {
            // start spinning !
            if (!_map._spinner) {
                _map._spinner = new Spinner().spin(_map._container);
                _map._spinning = 0;
            }
            _map._spinning++;
        }
        else {
            _map._spinning--;
            if (_map._spinning <= 0) {
                // end spinning !
                if (_map._spinner) {
                    _map._spinner.stop();
                    _map._spinner = null;
                }
            }
        }
    },

    load: function (url, force) {
        if (!!force && url.indexOf("?") != -1) {
            url += '?_u=' + (new Date().getTime());
        }
        var jsonLoad = function (data) {
            var features = jQuery.grep(data.features, function(obj, i) {
                return obj.geometry != null;
            });
            data.features = features;
            this.addData(data);
            this.loading = false;
            this.spin(false);
            this.fire('load');
        };
        var jsonError = function () {
            this.loading = false;
            this.spin(false);
            console.error("Could not load url '" + url + "'");
            if (this._map) $(this._map._container).addClass('map-error');
        };
        this.loading = true;
        this.spin(true);
        $.getJSON(url, L.Util.bind(jsonLoad, this))
         .error(L.Util.bind(jsonError, this));
    },

    getLayer: function (pk) {
        return this._objects[pk];
    },

    getPk: function(layer) {
        return layer.properties && layer.properties.pk;
    },

    search: function (bounds) {
        var rtbounds = this._rtbounds(bounds);
        return this.rtree.search(rtbounds) || [];
    },

    searchBuffer: function (latlng, radius) {
        var around = L.latLngBounds(L.latLng(latlng.lat - radius,
                                             latlng.lng - radius),
                                    L.latLng(latlng.lat + radius,
                                             latlng.lng + radius));
        return this.search(around);
    },

    // Show all layers matching the pks
    updateFromPks: function(pks) {
        var self = this
          , new_objects = {}
          , already_added_layer
          , to_add_layer
        ;

        // Gather all layer to see in new objects
        // Remove them from _current_objects if they are already shown
        // This way _current_objects will only contain layer to be removed
        $.each(pks, function(idx, to_add_pk) {
            already_added_layer = self._current_objects[to_add_pk];
            if (already_added_layer) {
                new_objects[to_add_pk] = already_added_layer;
                delete self._current_objects[to_add_pk]
            } else {
                to_add_layer = new_objects[to_add_pk] = self._objects[to_add_pk];
                // list can be ready before map, on first load
                if (to_add_layer) self.addLayer(to_add_layer);
            }
        });

        // Remove all remaining layer
        $.each(self._current_objects, function(pk, layer) {
            self.removeLayer(layer);
        });

        self._current_objects = new_objects;
    },

    jumpTo: function (pk) {
        var layer = this.getLayer(pk);
        if (!layer) return;
        this._map.fitBounds(layer.getBounds());
    },

    highlight: function (pk, on) {
        var on = on === undefined ? true : on,
            layer = this.getLayer(pk);
        if (!layer) return;
        
        if (on) {
            layer._defaultStyle = layer._defaultStyle ? layer._defaultStyle : this.options.styles.default;
            layer.setStyle(this.options.styles.highlight);
            // Pop on top
            this._map.removeLayer(layer).addLayer(layer);
        }
        else {
            layer.setStyle(layer._defaultStyle);
        }
    },

    select: function(pk, on) {
        var on = on === undefined ? true : on,
            layer = this.getLayer(pk);
        if (!layer) return;

        if (on) {
            layer._defaultStyle = this.options.styles.select;
            layer.setStyle(layer._defaultStyle);
            // Pop on top
            this._map.removeLayer(layer).addLayer(layer);
        }
        else {
            layer._defaultStyle = this.options.styles.default;
            layer.setStyle(layer._defaultStyle);
        }
    }
});
