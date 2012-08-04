if (!Caminae) var Caminae = {};


Caminae.ObjectsLayer = L.GeoJSON.extend({
    COLOR: 'blue',
    HIGHLIGHT: 'red',
    WEIGHT: 2,
    OPACITY: 0.8,
    
    includes: L.Mixin.Events,

    initialize: function (geojson, options) {
        // Hold the definition of all layers - immutable
        this._objects = {};
        // Hold the currently added layers (subset of _objects)
        this._current_objects = {};
        this.spinner = null;

        var onFeatureParse = function (geojson, layer) {
            this._mapObjects(geojson, layer);
            if (this._onEachFeature) this._onEachFeature(geojson, layer);
        };
        if (!options) options = {};
        this._onEachFeature = options.onEachFeature;
        options.onEachFeature = L.Util.bind(onFeatureParse, this);
        
        if (!options.style) {
            options.style = function (geojson) {
                return { 
                    // TODO: fucking JS
                    //'color': Caminae.ObjectsLayer.COLOR,
                    //'opacity': Caminae.ObjectsLayer.OPACITY,
                    //'weight': Caminae.ObjectsLayer.WEIGHT,
                    'weight': 2
                }
            };
        }

        var dataurl = null;
        if (typeof(geojson) == 'string') {
            dataurl = geojson;
            geojson = null;
        }
        L.GeoJSON.prototype.initialize.call(this, geojson, options);

        if (dataurl) {
            this.load(dataurl);
        }
    },

    _mapObjects: function (geojson, layer) {
        var pk = geojson.properties.pk
        this._objects[pk] = this._current_objects[pk] = layer;

        layer.on('mouseover', L.Util.bind(function (e) {
            this.highlight(pk);
        }, this));
        layer.on('mouseout', L.Util.bind(function (e) {
            this.highlight(pk, false);
        }, this));
        
        // Optionnaly make them clickable
        if (this.options.objectUrl) {
            layer.on('click', L.Util.bind(function (e) {
                window.location = this.options.objectUrl(geojson, layer);
            }, this));
        }
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

    highlight: function (pk, on) {
        var off = false;
        if (arguments.length == 2)
            off = !on;
        var l = this.getLayer(pk);
        if (l) l.setStyle({
            'opacity': off ? 0.8 : 1.0,
            'color': off ? 'blue' : 'red',
            'weight': off ? 2 : 5,
        });
    },
});


Caminae.getWKT = function(layer) {
    coord2str = function (obj) {
        if(obj.lng) return obj.lng + ' ' + obj.lat + ' 0.0';
        var n, wkt = [];
        for (n in obj) {
            wkt.push(coord2str(obj[n]));
        }
        return ("(" + String(wkt) + ")");
    };
    var coords = '()';
    if(layer.getLatLng) {
        coords = coord2str(layer.getLatLng());
    }
    else if (layer.getLatLngs) {
        coords = coord2str(layer.getLatLngs());
    }
    var wkt = '';
    if (layer instanceof L.Marker) wkt += 'POINT'+coords;
    else if (layer instanceof L.Polygon) wkt += 'POLYGON'+coords;
    else if (layer instanceof L.MultiPolygon) wkt += 'MULTIPOLYGON'+coords;
    else if (layer instanceof L.Polyline) wkt += 'LINESTRING'+coords;
    else if (layer instanceof L.MultiPolyline) wkt += 'MULTILINESTRING'+coords;
    else {
        wkt += 'GEOMETRY'+coords;
    }
    return wkt;
};
