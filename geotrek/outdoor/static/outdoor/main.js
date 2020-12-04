$(window).on('entity:map', function (e, data) {

    var map = data.map;
    var loaded_site = false;
    // Show outdoor layers in application maps
    $.each(['site'], function (i, modelname) {
        var layer = new L.ObjectsLayer(null, {
            modelname: modelname,
            style: L.Util.extend(window.SETTINGS.map.styles[modelname] || {}, {clickable:false}),
        });
        if (data.modelname != modelname) {
            map.layerscontrol.addOverlay(layer, tr(modelname), tr('Outdoor'));
        };
        map.on('layeradd', function(e) {
            var options = e.layer.options || {'modelname': 'None'};
            if (! loaded_site) {
                if (options.modelname == 'site' && options.modelname != data.modelname) {
                    e.layer.load(window.SETTINGS.urls.site_layer);
                    loaded_site = true;
                }
            }
    	});
    });
});
