if (!MapEntity) var MapEntity = {};

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
        }
    };
};



