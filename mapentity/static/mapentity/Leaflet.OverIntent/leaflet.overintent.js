L.OverIntentInitHook = function () {
    var duration = 500,
        timer = null;

    this.on('mouseover', function (e) {
        if (timer !== null) return;

        timer = setTimeout(L.Util.bind(function () {
            this.fire('mouseintent', {latlng: e.latlng, layer: e.layer});
            timer = null;
        }, this), duration);
    });

    this.on('mouseout', function (e) {
        if (timer !== null) {
            clearTimeout(timer);
            timer = null;
        }
    });
};

L.Marker.addInitHook(L.OverIntentInitHook);
L.Path.addInitHook(L.OverIntentInitHook);
L.FeatureGroup.addInitHook(L.OverIntentInitHook);