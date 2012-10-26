L.ObjectsLayer = L.GeoJSON.extend({
    COLOR: 'blue',
    HIGHLIGHT: 'red',
    SELECT: '#FF0061',
    WEIGHT: 2,
    OPACITY: 0.8,
    
    includes: L.Mixin.Events,

    initialize: function (geojson, options) {
        var self = this;

        // Hold the definition of all layers - immutable
        this._objects = {};
        // Hold the currently added layers (subset of _objects)
        this._current_objects = {};

        this._cameleon = L.Util.Cameleon.createDefaultCameleon();
        this.registerStyle('normal', 10, {'color': this.COLOR, 'weight': this.WEIGHT, 'opacity': this.OPACITY})
            .registerStyle('highlight', 30, {'color': this.HIGHLIGHT, 'weight': 5, 'opacity': 1})
            .registerStyle('select', 20, {'color': this.SELECT, 'weight': 5, 'opacity': 1});

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
        options.indexing = options.indexing !== undefined ? options.indexing : true;
        options.highlight = options.highlight || typeof(options.objectUrl) != 'undefined';
        this._onEachFeature = options.onEachFeature;
        options.onEachFeature = L.Util.bind(onFeatureParse, this);
        this._pointToLayer = options.pointToLayer;
        options.pointToLayer = L.Util.bind(pointToLayer, this);

        this.layer_events = {
            'highlight_mouseover': function(e) {
                self.highlight(e.layer.properties.pk);
            },
            'highlight_mouseout': function(e) {
                self.highlight(e.layer.properties.pk, false);
            },
            'detail_dblclick': function(e) {
                window.location = self.options.objectUrl(e.layer.properties, e.layer);
            }
        };


        // Highlight on mouse over
        if (options.highlight) {
            this.on('mouseover', this.layer_events.highlight_mouseover);
            this.on('mouseout', this.layer_events.highlight_mouseout);
        }

        // Optionnaly make them clickable
        if (options.objectUrl) {
            this.on('dblclick', this.layer_events.detail_dblclick);
        }

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
        else {
            bounds = new L.LatLngBounds(layer.getLatLng(), layer.getLatLng());
        }
        this.rtree.insert(this._rtbounds(bounds), layer);
    },

    onRemove: function (map) {
        this.spin(false, map);
        L.GeoJSON.prototype.onRemove.call(this, map);
    },

    spin: function (state, map) {
        var _map = map || this._map;
        
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
            if (_map._spinning == 0) {
                // end spinning !
                if (_map._spinner) {
                    _map._spinner.stop();
                    _map._spinner = null;
                }
            }
        }
    },

    load: function (url) {
        var jsonLoad = function (data) {
            var features = jQuery.grep(data.features, function(obj, i) {
                return obj.geometry != null;
            });
            data.features = features;
            this.addData(data);
            this.spin(false);
            this.fire('load');
        };
        var jsonError = function () {
            this.spin(false);
            console.error("Could not load url '" + url + "'");
            if (this._map) $(this._map._container).addClass('map-error');
        };
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

    registerStyle: function (name, priority, style) {
        return this._cameleon.registerStyle(name, priority, style);
    },

    highlight: function (pk, on) {
        var on = on === undefined ? true : on,
            layer = this.getLayer(pk);
        if (!layer) return;
        this._cameleon[on ? 'activate': 'deactivate']('highlight', layer);
    },

    select: function(pk, on) {
        var on = on === undefined ? true : on,
            layer = this.getLayer(pk);
        if (!layer) return;
        this._cameleon[on ? 'activate': 'deactivate']('select', layer);
    }
});


// Simply store a layer, apply a color and restore the previous color
L.Util.Cameleon = (function() {
    // Cameleon wrap a layer in a style
    // layerToId is used to convert a layer to a key
    function HashStore(layerToHashable) {
        var self = this;
        var wrappedLayer = {};
        function create(layer, fn_creation) {
            return wrappedLayer[layerToHashable(layer)] = fn_creation(layer);
        };
        this.get = function(layer) {
            return wrappedLayer[layerToHashable(layer)]
        };
        this.getOrCreate = function(layer, fn_creation) {
            return self.get(layer) || create(layer, fn_creation);
        };
        this.pop = function(layer) {
            var ret = self.get(layer)
            if (ret)
                delete wrappedLayer[layerToHashable(layer)];
            return ret;
        };
    }
    function InLayerStore() {
        // property: _skin
        var self = this;
        function create(layer, fn_creation) {
            return layer._skin = fn_creation(layer);
        };
        this.get = function(layer) {
            return layer._skin;
        };
        this.getOrCreate = function(layer, fn_creation) {
            return self.get(layer) || create(layer, fn_creation);
        };
        this.pop = function(layer) {
            var ret = self.get(layer)
            if (ret)
                delete layer._skin;
            return ret;
        };
    }

    var createCameleon = function(layerToSkin) {
        var available_styles = {};
        var hasStyle = function(applied_styles, style_name) {
            return style_name in applied_styles;
        };
        var addStyle = function(applied_styles, style) {
            var has_style = hasStyle(applied_styles, style.name)
            if (! has_style)
                applied_styles[style.name] = style;
            return !has_style;
        };
        var removeStyle = function(applied_styles, style) {
            var has_style = hasStyle(applied_styles, style.name)
            if (has_style)
                delete applied_styles[style.name]
            return has_style;
        };

        // var applied_styles = {};
        function initLayerSkin(layer) {
            return {
                'applied_styles': {},
                'initial_style': $.extend({}, layer.options)
            };
        };

        var computeStyle = function(skin) {
            var initial_style = skin.initial_style
              , applied_styles = skin.applied_styles;

            var styles = [initial_style].concat(getAscendingStyles(applied_styles));
            return $.extend.apply($.extend, [{}].concat(styles));
        }

        var setNewStyle = function(layer, skin) {
            var style = computeStyle(skin);
            layer.setStyle(style);
        };

        var getAscendingStyles = function(applied_styles) {
            var l = [];
            $.each(applied_styles, function(k, v) { l[v.priority] = v.style });
            return l;
            // applied_styles.sort(function(a, b) { return a.priority > b.priority });
        };

        return {
            'registerStyle': function(name, priority, style) {
                if (! (name in available_styles))
                    available_styles[name] = {'name': name, 'priority': priority, 'style': style};
                else
                    console.warn('Style ' + name + ' already registered.');

                return this;
            },
            // How do activate/deactivate multiple style (bulk) efficiently?
            // Here we use a lazy parameter that does not compute new style.
            // Yet look for the layer multiple time
            'activate': function(style_name, layer, lazy) {
                var style = available_styles[style_name];
                if (!style) return false;

                var skin = layerToSkin.getOrCreate(layer, initLayerSkin)
                var added = addStyle(skin.applied_styles, style);
                if (! added) return false;

                if (!lazy)
                    setNewStyle(layer, skin);
            },
            'deactivate': function(style_name, layer, lazy) {
                var style = available_styles[style_name];
                if (!style) return false;

                var skin = layerToSkin.get(layer);
                if (!skin) return false;

                var removed = removeStyle(skin.applied_styles, style);
                if (!removed) return false;

                if (!lazy)
                    setNewStyle(layer, skin);
            },
            'applyCurrentStyle': function(layer) {
                var skin = layerToSkin.get(layer);
                if (!skin) return false;
                setNewStyle(layer, skin);
            },
            'hasStyle': function(style_name, layer) {
                var skin = layerToCameleon.get(layer)
                if (!skin) return false;

                return hasStyle(skin.applied_styles, style_name);
            },
            'restoreStyle': function(layer) {
                var skin = layerToCameleon.get(layer)
                if (!skin) return false;

                skin.applied_styles = []
                setNewStyle(layer, skin);
            }
        };
    };

    function createDefaultCameleon() {
        return createCameleon(new InLayerStore())
    }

    return {
        'createDefaultCameleon': createDefaultCameleon
    };
})();
