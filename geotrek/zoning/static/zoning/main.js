$(window).on('entity:map', function (e, data) {

    var map = data.map;

    var landLayers = [{url: window.SETTINGS.urls.district_layer, name: tr("Districts"), id: 'district'},
                      {url: window.SETTINGS.urls.city_layer, name: tr("Cities"), id: 'city'}];

    landLayers = landLayers.concat(window.SETTINGS.map['restricted_area_types']);
    landLayers.map(function(el) {
        el.isActive = false;
        return el;
    })

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
                modelname: landLayer.name,
                style: style,
        });
        var nameHTML = '<span style="color: '+ style['color'] + ';">&#x2B24;</span>&nbsp;' + landLayer.name;
        map.layerscontrol.addOverlay(layer, nameHTML, tr('Zoning'));
    };

    map.on('layeradd', function(e){
        var options = e.layer.options || {'modelname': 'None'};
        for (var i=0; i<landLayers.length; i++) {
            if (! landLayers[i].isActive){
                if (options.modelname == landLayers[i].name){
                    e.layer.load(landLayers[i].url);
                    landLayers[i].isActive = true;
                }
            }
        }
    });
});