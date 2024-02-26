$(window).on('entity:map', function (e, data) {

    var map = data.map;

    var diveLayer = {url: window.SETTINGS.urls["diving_layer"], name: tr('Diving')};
    diveLayer.isActive = false;

    var style = L.Util.extend({clickable: false},
                              window.SETTINGS.map.styles['diving'] || {});
    var layer = new L.ObjectsLayer(null, {
        modelname: diveLayer.name,
        style: style
    });
    map.layerscontrol.addOverlay(layer,  tr('Diving'), tr('Diving'));
    map.on('layeradd', function(e){
        var options = e.layer.options || {'modelname': 'None'};

        if (! diveLayer.isActive){
            if (options.modelname == diveLayer.name){
                e.layer.load(diveLayer.url);
                diveLayer.isActive = true;
            }
        }
    });
});
