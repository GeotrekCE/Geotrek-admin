/*
 * Spatial index of layer objects using RTree.js
 * https://github.com/imbcmdth/RTree
 */


// Backport of Leaflet 0.5
if (typeof L.LatLngBounds.prototype.isValid != 'function') {
    L.LatLngBounds.prototype.isValid = function () {
        return !!(this._southWest && this._northEast);
    };
}


L.LayerIndexMixin = {

    search: function (bounds) {
        var rtbounds = this._rtbounds(bounds);
        return this._rtree ? this._rtree.search(rtbounds) : [];
    },

    searchBuffer: function (latlng, radius) {
        /* Caution: radius is in degrees */
        var around = L.latLngBounds([latlng.lat - radius,
                                     latlng.lng - radius],
                                    [latlng.lat + radius,
                                     latlng.lng + radius]);
        return this.search(around);
    },

    indexLayer: function (layer) {
        if (this.options.indexing !== undefined && !this.options.indexing)
            return;

        var bounds = this._layerBounds(layer);

        if (!this._rtree) this._rtree = new RTree();
        this._rtree.insert(this._rtbounds(bounds), layer);
    },

    unindexLayer: function (bounds, layer) {
        /* If layer is not provided, does wide-area remove */
        this._rtree.remove(this._rtbounds(bounds), layer);
    },

    _layerBounds: function (layer) {
        // Introspects layer and returns its bounds.
        var bounds = null;
        if (layer instanceof L.LayerGroup) {
            // Leaflet uses project() in Circle's getBounds() method.
            // It will fail it if the layer is not yet on the map.
            // Thus, rewrite that part and add switch for Circles,
            // ignoring their radius in pixels.
            bounds = new L.LatLngBounds();
            layer.eachLayer(function (sublayer) {
                if (sublayer instanceof L.Circle || sublayer instanceof L.Marker)
                    bounds.extend(sublayer.getLatLng());
                else if (sublayer instanceof L.LayerGroup)
                    bounds.extend(this._layerBounds(sublayer));
                else
                    bounds.extend(sublayer.getBounds());
            }, this);
        }
        else if (typeof layer.getLatLng == 'function') {
            bounds = new L.LatLngBounds(layer.getLatLng(), layer.getLatLng());
        }
        else if (typeof layer.getBounds == 'function') {
            bounds = layer.getBounds();
        }

        if (!(bounds && bounds.isValid()))
            throw "Unable to get layer bounds";

        return bounds;
    },

    _rtbounds: function (bounds) {
        return {x: bounds.getSouthWest().lng,
                y: bounds.getSouthWest().lat,
                w: bounds.getSouthEast().lng - bounds.getSouthWest().lng,
                h: bounds.getNorthWest().lat - bounds.getSouthWest().lat};
    },
};
