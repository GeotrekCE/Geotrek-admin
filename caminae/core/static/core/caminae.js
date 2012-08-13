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
        this.rtree = new RTree();

        var onFeatureParse = function (geojson, layer) {
            this._mapObjects(geojson, layer);
            if (this._onEachFeature) this._onEachFeature(geojson, layer);
        };
        var pointToLayer = function (geojson, latlng) {
            if (this._pointToLayer) return this._pointToLayer(geojson, latlng);
            return new L.CircleMarker(latlng);
        };
        
        if (!options) options = {};
        options.highlight = options.highlight || typeof(options.objectUrl) != 'undefined';
        this._onEachFeature = options.onEachFeature;
        options.onEachFeature = L.Util.bind(onFeatureParse, this);
        this._pointToLayer = options.pointToLayer;
        options.pointToLayer = L.Util.bind(pointToLayer, this);
        
        var self = this;
        if (!options.style) {
            options.style = function (geojson) {
                return { 
                    color: self.COLOR,
                    opacity: self.OPACITY,
                    fillOpacity: self.OPACITY * 0.9,
                    weight: self.WEIGHT
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
        var bounds = null;
        if (layer.getLatLngs) {
            bounds = layer.getBounds();
        }
        else {
            bounds = new L.LatLngBounds(layer.getLatLng(), layer.getLatLng());
        }
        this.rtree.insert(this._rtbounds(bounds), layer);

        // Highlight on mouse over
        if (this.options.highlight) {
            layer.on('mouseover', L.Util.bind(function (e) {
                this.highlight(pk);
            }, this));
            layer.on('mouseout', L.Util.bind(function (e) {
                this.highlight(pk, false);
            }, this));
        }

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

    getPk: function(layer) {
        return layer.properties && layer.properties.pk;
    },

    search: function (bounds) {
        var rtbounds = this._rtbounds(bounds);
        return this.rtree.search(rtbounds) || [];
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

