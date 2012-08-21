if (!MapEntity) var MapEntity = {};


MapEntity.ObjectsLayer = L.GeoJSON.extend({
    COLOR: 'blue',
    HIGHLIGHT: 'red',
    WEIGHT: 2,
    OPACITY: 0.8,
    
    includes: L.Mixin.Events,

    initialize: function (geojson, options) {
        var self = this;

        // Hold the definition of all layers - immutable
        this._objects = {};
        // Hold the currently added layers (subset of _objects)
        this._current_objects = {};

        this._cameleon = MapEntity.Cameleon.createDefaultCameleon();

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
        var bounds = null;
        if (layer instanceof L.MultiPolyline) {
            bounds = new L.LatLngBounds();
            for (var i in layer._layers) {
                bounds.extend(layer._layers[i].getBounds());
            }
        }
        else if (layer.getLatLngs) {
            bounds = layer.getBounds();
        }
        else {
            bounds = new L.LatLngBounds(layer.getLatLng(), layer.getLatLng());
        }
        this.rtree.insert(this._rtbounds(bounds), layer);
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
        var on = on === undefined ? true : on;
        this._cameleon[on ? 'activate': 'deactivate']('highlight', this.getLayer(pk));
    },
    select: function(pk, on) {
        var on = on === undefined ? true : on;
        this._cameleon[on ? 'activate': 'deactivate']('select', this.getLayer(pk));
    }
});


MapEntity.getWKT = function(layer) {
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
        coords = '(' + coord2str(layer.getLatLng()) + ')';
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


L.Control.Information = L.Control.extend({
    options: {
        position: 'bottomright',
    },

    onAdd: function (map) {
        this._container = L.DomUtil.create('div', 'leaflet-control-attribution');
        L.DomEvent.disableClickPropagation(this._container);

        map.on('layeradd', this._onLayerAdd, this)
           .on('layerremove', this._onLayerRemove, this);

        return this._container;
    },

    onRemove: function (map) {
        map.off('layeradd', this._onLayerAdd)
           .off('layerremove', this._onLayerRemove);

    },

    _onLayerAdd: function (e) {
        e.layer.on('info', L.Util.bind(function (ei) {
            this._container.innerHTML = ei.info;
        }, this));
    },

    _onLayerRemove: function (e) {
        e.layer.off('info');
    }
});


MapEntity.MarkerSnapping = L.Handler.extend({
    SNAP_DISTANCE: 15,  // snap on marker move
    TOLERANCE: 0.00005, // snap existing object

    initialize: function (map, marker) {
        L.Handler.prototype.initialize.call(this, map);
        this._snaplist = [];
        this._markers = []
        if (marker) {
            // new markers should be draggable !
            if (!marker.dragging) marker.dragging = new L.Handler.MarkerDrag(marker);
            marker.dragging.enable();
            this.snapMarker(marker);
        }
    },

    enable: function () {
        this.disable();
        for (var i=0; i<this._markers.length; i++) {
            this.snapMarker(this._markers[i]);
        }
    },

    disable: function () {
        for (var i=0; i<this._markers.length; i++) {
            this.unsnapMarker(this._markers[i]);
        }
    },

    snapMarker: function (marker) {
        var i=0;
        for (; i<this._markers.length; i++) {
            if (this._markers[i] == marker) break;
        }
        if (i==this._markers.length) this._markers.push(marker);
        marker.on('move', this._snapMarker, this);
    },

    unsnapMarker: function (marker) {
        marker.off('move', this._snapMarker);
    },

    setSnapList: function (l) {
        l = l || [];
        this._snaplist = l;
        for (var i=0; i<this._markers.length; i++) {
            var marker = this._markers[i];
            // Mark as snap if any object of snaplist is already snapped !
            var closest = this._closest(marker),
                chosen = closest[0],
                point = closest[1];
            if (point &&
                (Math.abs(point.lat - marker.getLatLng().lat) < this.TOLERANCE)  &&
                (Math.abs(point.lng - marker.getLatLng().lng) < this.TOLERANCE)) {
                $(marker._icon).addClass('marker-snapped');
            }
        }
    },

    distance: function (latlng1, latlng2) {
        return this._map.latLngToLayerPoint(latlng1).distanceTo(this._map.latLngToLayerPoint(latlng2));
    },

    distanceSegment: function (latlng, latlngA, latlngB) {
        var p = this._map.latLngToLayerPoint(latlng),
           p1 = this._map.latLngToLayerPoint(latlngA),
           p2 = this._map.latLngToLayerPoint(latlngB);
        return L.LineUtil.pointToSegmentDistance(p, p1, p2);
    },

    latlngOnSegment: function (latlng, latlngA, latlngB) {
        var p = this._map.latLngToLayerPoint(latlng),
           p1 = this._map.latLngToLayerPoint(latlngA),
           p2 = this._map.latLngToLayerPoint(latlngB);
           closest = L.LineUtil.closestPointOnSegment(p, p1, p2);
        return this._map.layerPointToLatLng(closest);
    },

    _closest: function (marker) {
        var mindist = Number.MAX_VALUE,
             chosen = null,
             point = null;
        var n = this._snaplist.length;
        // /!\ Careful with size of this list, iterated at every marker move!
        if (n>1000) console.warn("Snap list is very big : " + n + " objects!");

        // Iterate the whole snaplist
        for (var i = 0; i < n ; i++) {
            var object = this._snaplist[i],
                ll = null,
                distance = Number.MAX_VALUE;
            if (object.getLatLng) {
                // Single dimension, snap on points
                ll = object.getLatLng();
                distance = this.distance(marker.getLatLng(), ll);
            }
            else {
                // Iterate on line segments
                var lls = object.getLatLngs(),
                    segmentmindist = Number.MAX_VALUE;
                // Keep the closest point of all segments
                for (var j = 0; j < lls.length - 1; j++) {
                    var p1 = lls[j],
                        p2 = lls[j+1],
                        d = this.distanceSegment(marker.getLatLng(), p1, p2);
                    if (d < segmentmindist) {
                        segmentmindist = d;
                        ll = this.latlngOnSegment(marker.getLatLng(), p1, p2);
                        distance = d;
                    }
                }
            }
            // Keep the closest point of all objects
            if (distance < this.SNAP_DISTANCE && distance < mindist) {
                mindist = distance;
                chosen = object;
                point = ll;
            }
        }
        return [chosen, point];
    },

    _snapMarker: function (e) {
        var marker = e.target
        var closest = this._closest(marker),
            chosen = closest[0],
            point = closest[1];
        if (chosen) {
            marker.setLatLng(point);
            if (marker.snap != chosen) {
                marker.snap = chosen;
                $(marker._icon).addClass('marker-snapped');
                marker.fire('snap', {object:chosen, location: point});
            }
        }
        else {
            if (marker.snap) {
                $(marker._icon).removeClass('marker-snapped');
                marker.fire('unsnap', {object:marker.snap});
            }
            marker.snap = null;
        }
    },
});


L.Handler.SnappedEdit = L.Handler.PolyEdit.extend({

    initialize: function (map, poly, options) {
        L.Handler.PolyEdit.prototype.initialize.call(this, poly, options);
        this._snapper = new MapEntity.MarkerSnapping(map);
    },

    setSnapList: function (l) {
        this._snapper.setSnapList(l);
    },

    _createMarker: function (latlng, index) {
        var marker = L.Handler.PolyEdit.prototype._createMarker.call(this, latlng, index);
        this._snapper.snapMarker(marker);
        return marker;
    },
});


MapEntity.SnapObserver = L.Class.extend({
    MIN_SNAP_ZOOM: 7,

    initialize: function (map, guidesLayer) {
        this._map = map;
        this._guidesLayer = guidesLayer;
        this._editionLayers = [];

        guidesLayer.on('load', this._refresh, this);
        map.on('viewreset moveend', this._refresh, this);
    },
    add: function (editionLayer) {
        if (editionLayer.eachLayer) {
            editionLayer.eachLayer(function (l) {
                this.add(l);
            }, this);
        }
        else {
            this._editionLayers.push(editionLayer);
            editionLayer.editing.setSnapList(this.snapList());

        }
    },
    remove: function (editionLayer) {
        //TODO
    },
    snapList: function () {
        if (this._map.getZoom() > this.MIN_SNAP_ZOOM) {
            return this._guidesLayer.search(this._map.getBounds());
        }
        console.log('No snapping at zoom level ' + this._map.getZoom());
        return [];
    },
    _refresh: function () {
        for (var i=0; i < this._editionLayers.length; i++) {
            var editionLayer = this._editionLayers[i];
            editionLayer.editing.setSnapList(this.snapList());
        }
    }
});


MapEntity.makeGeoFieldProxy = function($field, layer) {
    // Proxy to field storing WKT. It also stores the matching layer.
    var _current_layer = layer || null;

    return {
        storeLayerGeomInField: function(layer) {
            var old_layer = _current_layer;
            _current_layer = layer;

            var wkt = layer ? MapEntity.getWKT(layer) : '';
            $field.val(wkt);

            return old_layer;
        },
        getLayer: function () {
            return _current_layer;
        },
        storeTopologyInField: function (topology) {
            var old_layer = _current_layer;
            _current_layer = topology;

            $field.val(JSON.stringify(topology));

            return old_layer;
        },
    };
};

MapEntity.resetForm = function resetForm($form) {
    $form.find('input:text, input:password, input:file, select, textarea').val('');
    $form.find('input:radio, input:checkbox')
         .removeAttr('checked').removeAttr('selected');
}

MapEntity.showNumberSearchResults = function (nb) {
    if (arguments.length > 0) {
        localStorage.setItem('list-search-results', nb);
    }
    else {
        nb = localStorage.getItem('list-search-results') || '?';
    }
    $('#nbresults').text(nb);
}


// Simply store a layer, apply a color and restore the previous color
MapEntity.Cameleon = (function() {
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
            $.each(applied_styles, function(k, v) { l[v.weight] = v.style });
            return l;
            // applied_styles.sort(function(a, b) { return a.weight > b.weight });
        };

        return {
            'registerStyle': function(name, weight, style) {
                if (! (name in available_styles))
                    available_styles[name] = {'name': name, 'weight': weight, 'style': style};

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

    // Ahem... to have consistent result we should have unique weight or check on the name also
    function createDefaultCameleon() {
        return createCameleon(new InLayerStore())
            .registerStyle('normal', 0, {'color': 'blue', 'weight': 2, 'opacity': 0.8})
            .registerStyle('highlight', 30, {'color': 'red', 'weight': 5, 'opacity': 1})
            .registerStyle('select', 20, {'color': 'red', 'weight': 5, 'opacity': 1})
            //
            .registerStyle('dijkstra_from', 10, {'color': 'yellow', 'weight': 5, 'opacity': 1})
            .registerStyle('dijkstra_to', 11, {'color': 'yellow', 'weight': 5, 'opacity': 1})
            .registerStyle('dijkstra_step', 9, {'color': 'yellow', 'weight': 5, 'opacity': 1})
            .registerStyle('dijkstra_computed', 8, {'color': 'yellow', 'weight': 5, 'opacity': 1})
        ;
    }

    return {
        'createDefaultCameleon': createDefaultCameleon
    };
})();
