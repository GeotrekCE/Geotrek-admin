(function (factory, window) {
  if (typeof define === 'function' && define.amd) {
    define(['leaflet'], function (L) {
      factory(L);
    });
  } else if (typeof module === 'object' && module.exports) {
    module.exports = function (L) {
      if (L === undefined && typeof window !== 'undefined') {
        L = require('leaflet');
      }
      factory(L);
      return L;
    };
  } else if (typeof window !== 'undefined' && window.L) {
    factory(window.L);
  }
}(function overIntentFactory(L) {
  L.OverIntentInitHook = function () {
    var timer = null;

    this.on('mouseover', function (e) {
      var duration;
      if (timer !== null) return;

      duration = this.options.intentDuration || 300;

      timer = setTimeout(L.Util.bind(function () {
        this.fire('mouseintent', {
          latlng: e.latlng,
          layer: e.layer
        });
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
}, window));
