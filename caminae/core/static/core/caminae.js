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

    _rtbounds: function (bounds) {
        return {x: bounds.getSouthWest().lng,
                y: bounds.getSouthWest().lat,
                w: bounds.getSouthEast().lng - bounds.getSouthWest().lng,
                h: bounds.getNorthWest().lat - bounds.getSouthWest().lat};
    },

    _mapObjects: function (geojson, layer) {
        var pk = geojson.properties.pk
        this._objects[pk] = this._current_objects[pk] = layer;
        
        // Spatial indexing
        var bounds = null;
        if (layer.getBounds) {
            bounds = layer.getBounds();
        }
        else {
            bounds = new L.LatLngBounds(layer.getLatLng(), layer.getLatLng());
        }
        this.rtree.insert(this._rtbounds(bounds), layer);

        // Highlight on mouse over
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


Caminae.getWKT = function(layer) {
    coord2str = function (obj) {
        if(obj.lng) return '(' + obj.lng + ' ' + obj.lat + ' 0.0)';
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


Caminae.MarkerSnapping = L.Handler.extend({
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
        this._snapper = new Caminae.MarkerSnapping(map);
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


Caminae.SnapObserver = L.Class.extend({
    MIN_SNAP_ZOOM: 12,
    
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


Caminae.makeGeoFieldProxy = function($field, layer) {
    // Proxy to field storing WKT. It also stores the matching layer.
    var _current_layer = layer || null;

    return {
        storeLayerGeomInField: function(layer) {
            var old_layer = _current_layer;
            _current_layer = layer;

            var wkt = layer ? Caminae.getWKT(layer) : '';
            $field.val(wkt);

            return old_layer;
        },
        getLayer: function () {
            return _current_layer;
        }
    };
};
