L.Handler.MarkerSnapping = L.Handler.extend({
    SNAP_DISTANCE: 15,  // snap on marker move
    TOLERANCE: 0.00005, // snap existing object

    initialize: function (map, marker) {
        L.Handler.prototype.initialize.call(this, map);
        this._markers = []
        
        // Get necessary distance around mouse in lat/lng from distance in pixels
        this._buffer = this._map.layerPointToLatLng(new L.Point(0,0)).lat - 
                       this._map.layerPointToLatLng(new L.Point(this.SNAP_DISTANCE,0)).lat;

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
        if (this._markers.indexOf(marker) == -1)
            this._markers.push(marker);

        marker.on('move', this._snapMarker, this);
    },

    unsnapMarker: function (marker) {
        marker.off('move', this._snapMarker);
    },

    setGuidesLayer: function (guides) {
        this._guides = guides;
    },

    _snapMarker: function(e) {
        var marker = e.target,
            snaplist = this._guides.searchBuffer(marker.getLatLng(), this._buffer),
            closest = L.GeomUtils.closest(this._map, marker, snaplist, this.SNAP_DISTANCE);
        this.updateClosest(marker, closest);
    },

    updateClosest: function (marker, closest) {
        var chosen = closest[0],
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
    }
});


L.Handler.SnappedEdit = L.Handler.PolyEdit.extend({

    initialize: function (map, poly, options) {
        L.Handler.PolyEdit.prototype.initialize.call(this, poly, options);
        this._snapper = new L.Handler.MarkerSnapping(map);
    },

    setGuidesLayer: function (guides) {
        this._snapper.setGuidesLayer(guides);
    },

    _createMarker: function (latlng, index) {
        var marker = L.Handler.PolyEdit.prototype._createMarker.call(this, latlng, index);
        this._snapper.snapMarker(marker);
        return marker;
    },
});


L.SnapObserver = L.Class.extend({
    initialize: function (map, guidesLayer) {
        this._map = map;
        this._guidesLayer = guidesLayer;
        this._editionLayers = [];
    },
    guidesLayer: function () {
        return this._guidesLayer;
    },
    add: function (editionLayer) {
        if (editionLayer.eachLayer) {
            editionLayer.eachLayer(function (l) {
                this.add(l);
            }, this);
        }
        else {
            this._editionLayers.push(editionLayer);
            editionLayer.editing.setGuidesLayer(this._guidesLayer);
        }
    },
    remove: function (editionLayer) {
        //TODO
    },
});
