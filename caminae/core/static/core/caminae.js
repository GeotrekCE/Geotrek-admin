if (!Caminae) var Caminae = {};


Caminae.ObjectsLayer = L.GeoJSON.extend({
    includes: L.Mixin.Events,

    initialize: function (geojson, options) {
        // Hold the definition of all layers - immutable
        this._objects = {};
        // Hold the currently added layers (subset of _objects)
        this._current_objects = {};
        this.spinner = null;

        var onEachFeature = function (geojson, layer) {
            this._onEachFeature(geojson, layer);
            if (this._onEachFeatureExtra) this._onEachFeatureExtra(geojson, layer);
        };
        if (!options) options = {};
        this._onEachFeatureExtra = options.onEachFeature;
        options.onEachFeature = L.Util.bind(onEachFeature, this);

        var url = null;
        if (typeof(geojson) == 'string') {
            url = geojson;
            geojson = null;
        }
        L.GeoJSON.prototype.initialize.call(this, geojson, options);

        if (url) {
            this.load(url);
        }
    },

    _onEachFeature: function (geojson, layer) {
        var pk = geojson.properties.pk
        this._objects[pk] = this._current_objects[pk] = layer;
    },

    load: function (url) {
        var jsonLoad = function (data) {
            this.addData(data);
            this.fire('load');
            if (this.spinner) this.spinner.stop();
        };
        if (this._map) this.spinner = new Spinner().spin(this._map._container);
        $.getJSON(url, L.Util.bind(jsonLoad, this));
    },

    getLayer: function (pk) {
        return this._objects[pk];
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
                self.addLayer(to_add_layer);
            }
        });

        // Remove all remaining layer
        $.each(self._current_objects, function(pk, layer) {
            self.removeLayer(layer);
        });

        self._current_objects = new_objects;
    },

    highlight: function (pk) {
        var l = this.getLayer(pk);
        l.setStyle({'color': 'red'});
    },

    layerToWKT: function(layer) {
        coord2str = function (obj) {
            if(obj.lng) return obj.lng + ' ' + obj.lat + ' 0.0';
            var n, wkt = [];
            for (n in obj) {
                wkt.push(coord2str(obj[n]));
            }
            return ("(" + String(wkt) + ")");
        };
        var wkt = '';
        if(layer.getLatLng) wkt += 'POINT'+coord2str(layer.getLatLng());
        if(layer.getLatLngs) {
            var coords = coord2str(layer.getLatLngs());
            if (layer instanceof L.Polygon) wkt += 'POLYGON'+coords;
            else if (layer instanceof L.MultiPolygon) wkt += 'MULTIPOLYGON'+coords;
            else if (layer instanceof L.Polyline) wkt += 'LINESTRING'+coords;
            else if (layer instanceof L.MultiPolyline) wkt += 'MULTILINESTRING'+coords;
            else {
                wkt += 'LINESTRING'+coords;
            }
        }
        return wkt;
    },
    
    getWKT: function () {
        var wkt = [];
        this.eachLayer(function(layer) {wkt.push(this.layerToWKT(layer));}, this);
        return String(wkt);
    }
});
