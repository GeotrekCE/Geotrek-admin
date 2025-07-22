//
// Sensitivity
//

$(window).on('entity:map', function (e, data) {
    var modelname = 'sensitivearea';
    var layername = `${modelname}_layer`;
    var url = window.SETTINGS.urls[layername];
    var loaded_sensitivearea = false;
    var map = data.map;

    // Show sensitiveare layer in application maps
    var style = L.Util.extend({clickable: false},
        window.SETTINGS.map.styles[modelname] || {})

    var layer = new L.ObjectsLayer(null, {
        modelname: modelname,
        style: style,
    });

    if (data.modelname != modelname) {
        map.layerscontrol.addOverlay(layer, tr('sensitivearea'), tr('Sensitivity'));
    };

    map.on('layeradd', function (e) {
        var options = e.layer.options || {'modelname': 'None'};
        if (!loaded_sensitivearea) {
            if (options.modelname == modelname && options.modelname != data.modelname) {
                e.layer.load(url);
                loaded_sensitivearea = true;
            }
        }
    });
});
