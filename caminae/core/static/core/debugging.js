var DEBUG = {};

DEBUG.multipath = (function() {

    // Make each layer blink, revealing the path
    function blinkPath(map, layers, cb, period) {
        var idx = 0, len = layers.length;
        var current = null;

        (function blink() {
            current && map.removeLayer(current);

            if (idx < len) {
                current = layers[idx];
                map.addLayer(current);
                idx++;
                setTimeout(blink, period || 1000);
            } else {
                cb && cb();
            }

        })();

    }

    return {
        'blinkPath': blinkPath,
    };
})();
