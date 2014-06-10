$(window).on('entity:map', function (e, data) {

    var map = data.map;

    // Add land layers
    var landLayers = [{url: window.SETTINGS.urls.district_layer, name: tr("Districts"), id: 'district'},
                      {url: window.SETTINGS.urls.city_layer, name: tr("Cities"), id: 'city'}];

    landLayers = landLayers.concat(window.SETTINGS.map['restricted_area_types']);

    for (var i=0; i<landLayers.length; i++) {
        var landLayer = landLayers[i];
        var layer = new L.ObjectsLayer(null, {
            indexing: false,
            style: L.Util.extend(window.SETTINGS.map.styles[landLayer.id] || {}, { clickable:false })
        });
        layer.load(landLayer.url);
        map.layerscontrol.addOverlay(layer, landLayer.name, tr('Zoning'));
    }
});