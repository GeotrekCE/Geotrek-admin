
$(window).on('entity:map', function (e, data) {

  if (data.modelname != 'sensitivearea') {
      var map = data.map;

      // Show sensitivity layer in application maps
      var layer = new L.ObjectsLayer(null, {
          modelname: 'sensitivearea',
          style: L.Util.extend(window.SETTINGS.map.styles['sensitivearea'] || {}, {clickable:false}),
      });
      var url = window.SETTINGS.urls['sensitivearea_layer'];
      layer.load(url);
      map.layerscontrol.addOverlay(layer, tr('sensitivearea'), tr('Sensitivity'));
  }
});