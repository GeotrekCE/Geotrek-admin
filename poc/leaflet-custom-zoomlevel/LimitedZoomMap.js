/*
 * L.Map is the central class of the API - it is used to create a map.
 */

L.LimitedZoomMap = L.Map.extend({

    options: {
        validZoomLevels: null,
    },


    // constructor
    initialize: function (id, options) { // (HTMLElement or String, Object)
        // Parameter sanitization
        if (options && options.validZoomLevels) {
            if (typeof options.validZoomLevels == "object") {
                options.validZoomLevels.sort(function(a, b) {return a-b;});
                // Also check consistency with minZoom/maxZoom ?
            } else {
                delete options['validZoomLevels']
            }
        }
        return L.Map.prototype.initialize.call(this, id, options);
    },

    _limitZoom: function (zoom) {
        if (this.options.validZoomLevels) {
            var cursor;
            if (zoom > this.getZoom()) {
                for (cursor=0; cursor<this.options.validZoomLevels.length-1; cursor++) {
                    if (this.options.validZoomLevels[cursor] > zoom) break;
                }
            } else {
                for (cursor=this.options.validZoomLevels.length-1; cursor>0; cursor--) {
                    if (this.options.validZoomLevels[cursor] < zoom) break;
                }
            }
        }
        return L.Map.prototype._limitZoom.call(this, this.options.validZoomLevels[cursor]);
    }
});
