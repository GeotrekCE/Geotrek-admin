if (!Caminae) var Caminae = {};


Caminae.ObjectsLayer = L.GeoJSON.extend({
    includes: L.Mixin.Events,
    
    initialize: function (geojson, options) {
        this._objects = {};
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
        this._objects[geojson.properties.pk] = layer;
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

    highlight: function (pk) {
        var l = this.getLayer(pk);
        l.setStyle({'color': 'red'});
    }
});
