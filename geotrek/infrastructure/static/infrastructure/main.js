//
// Infrastructure
//

$(window).on('entity:map', function (e, data) {
    var modelname = 'infrastructure';
    var layername = `${modelname}_layer`;
	var url = window.SETTINGS.urls[layername];
    var loaded_infrastructure = false;
    var map = data.map;

    // Show infrastructure layer in application maps
    var style = L.Util.extend({ clickable: false },
        window.SETTINGS.map.styles[modelname] || {});
	var layer = new L.ObjectsLayer(null, {
		modelname: modelname,
		style: style,
	});

    if (data.modelname != modelname){
	    map.layerscontrol.addOverlay(layer, tr('Infrastructure'), tr('Infrastructure'));
    };

    map.on('layeradd', function (e) {
        var options = e.layer.options || { 'modelname': 'None' };
        if (! loaded_infrastructure) {
            if (options.modelname == modelname && options.modelname != data.modelname) {
                e.layer.load(url);
                loaded_infrastructure = true;
            }
        }
    });
});
