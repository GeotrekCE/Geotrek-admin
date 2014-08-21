$(window).on('entity:map', function (e, data) {

    var map = data.map;

    // Add land layers
    var landLayers = [{url: window.SETTINGS.urls.district_layer, name: tr("Districts"), id: 'district'},
                      {url: window.SETTINGS.urls.city_layer, name: tr("Cities"), id: 'city'}];

    landLayers = landLayers.concat(window.SETTINGS.map['restricted_area_types']);

    for (var i=0; i<landLayers.length; i++) {
        var landLayer = landLayers[i];
        var style = L.Util.extend({clickable: false},
                                  window.SETTINGS.map.styles[landLayer.id] || {});

        var colorspools = L.Util.extend({}, window.SETTINGS.map.colorspool),
            colorspool = colorspools[landLayer.id];
        if (colorspool) {
            var color = colorspool[i % colorspool.length];
            style['color'] = color;
        }

        var layer = new L.ObjectsLayer(null, {
            indexing: false,
            style: style,
            modelname: landLayer.id,
        });
        layer.load(landLayer.url);

        var nameHTML = '<span style="color: '+ style['color'] + ';">&#x2B24;</span>&nbsp;' + landLayer.name;
        map.layerscontrol.addOverlay(layer, nameHTML, tr('Zoning'));
    }
});