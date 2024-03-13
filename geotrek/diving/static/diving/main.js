$(window).on('entity:map', function (e, data) {
    var modelname = 'dive';
    var layername = `${modelname}_layer`;
	var url = window.SETTINGS.urls[layername];
    var loaded_dive = false;
    var map = data.map;
    var style = L.Util.extend({ clickable: false },
        window.SETTINGS.map.styles[modelname] || {});
    // Show dive layer in application maps
	var layer = new L.ObjectsLayer(null, {
		modelname: modelname,
		style: style,
	});

    if (data.modelname != modelname){
	    map.layerscontrol.addOverlay(layer, tr('Diving'), tr('Diving'));
    };

    map.on('layeradd', function (e) {
        var options = e.layer.options || { 'modelname': 'None' };
        if (! loaded_dive) {
            if (options.modelname == modelname && options.modelname != data.modelname) {
                e.layer.load(url);
                loaded_dive = true;
            }
        }
    });
});
