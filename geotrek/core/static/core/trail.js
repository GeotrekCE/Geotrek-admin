$(window).on('entity:map', function (e, data) {
    var modelname = 'trail';
    var layername = `${modelname}_layer`;
	var url = window.SETTINGS.urls[layername];
    var loaded_trail = false;
    var map = data.map;
    var style = L.Util.extend({ clickable: false },
        window.SETTINGS.map.styles[modelname] || {});
    // Show trail layer in application maps
	var layer = new L.ObjectsLayer(null, {
		modelname: modelname,
		style: style,
	});

    if (data.modelname != modelname){
	    map.layerscontrol.addOverlay(layer, tr('Trails'), tr('Trail'));
    };

    map.on('layeradd', function (e) {
        var options = e.layer.options || { 'modelname': 'None' };
        if (! loaded_trail) {
            if (options.modelname == modelname && options.modelname != data.modelname) {
                e.layer.load(url);
                loaded_trail = true;
            }
        }
    });
});
