(function () {
    //
    // Shows small makers with enumeration letters
    // See https://github.com/makinacorpus/django-mapentity/issues/35
    // (A, B, ...Z, AA, AB, ...)
    //
    // Requires CSS for .enumeration-icon marker icons

    var __addLayer = L.LayerGroup.prototype.addLayer;

    L.LayerGroup.include({

        //
        // Override addLayer() to keep track of group's layers order.
        addLayer: function (layer) {
            if (this.__layerArray === undefined){
                this.__layerArray = [];
            }
            __addLayer.call(this, layer);
            this.__layerArray.push(layer);
        },

        //
        // Helper to iterate layers in order
        enumerateLayers: function (fn, context) {
            var layers = this.__layerArray || [];
            for (var i=0, n=layers.length; i<n; i++) {
                fn.call(context, layers[i], i);
            }
        },

        //
        // Add marker to show enumeration
        showEnumeration: function () {
            if (!this._map)
                return;

            this.enumerateLayers(function (layer, i) {
                var position = null;

                // Layer to position of marker
                if (typeof layer.getLatLng === 'function') {
                    position = layer.getLatLng();
                }
                else if (typeof layer.getLatLngs === 'function') {
                    var latlngs = layer.getLatLngs();
                    position = latlngs[Math.floor(latlngs.length / 2)];
                }

                // Number to alphabet : A, B, ... Y, Z, AA, AB, ...
                var start = 'A'.charCodeAt(0);
                var enumeration = i < 26 ? '' :
                                  String.fromCharCode(start + Math.floor(i/26) - 1);
                enumeration += String.fromCharCode(start + i % 26);

                if (position) {
                    var icon = L.divIcon({
                        className: 'enumeration-icon',
                        html: enumeration
                    });
                    L.marker(position, {
                        clickable: false,
                        icon: icon
                    }).addTo(this._map);
                }
            }, this);
        }
    });
})();