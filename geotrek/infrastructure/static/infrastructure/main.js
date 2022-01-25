//
// Infrastructure
//

$(window).on('entity:map', function (e, data) {
    var map = data.map;
    loaded_infrastructure = false;

    // Show infrastructure layer in application maps
	var layer = new L.ObjectsLayer(null, {
		modelname: 'infrastructure',
		style: L.Util.extend(window.SETTINGS.map.styles['infrastructure'] || {}, { clickable:false }),
	});
	var url = window.SETTINGS.urls['infrastructure_layer'];

    if (data.modelname != layer.modelname){
	    map.layerscontrol.addOverlay(layer, tr('Infrastructure'), tr('Infrastructure'));
    };

    map.on('layeradd', function (e) {
        var options = e.layer.options || { 'modelname': 'None' };
        if (! loaded_infrastructure) {
            if (options.modelname == 'infrastructure' && options.modelname != data.modelname) {
                e.layer.load(url);
                loaded_infrastructure = true;
            }
        }
    });
});
