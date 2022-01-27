//
// Trekking
//

$(window).on('entity:map', function (e, data) {

    var map = data.map;
    var trekkingLayers = [
        { url: window.SETTINGS.urls.trek_layer, name: tr('Treks'), id: 'trek' },
        { url: window.SETTINGS.urls.poi_layer, name: tr('POI'), id: 'poi' },
        { url: window.SETTINGS.urls.service_layer, name: tr('Services'), id: 'service' },
    ]
    trekkingLayers.map(function (el) {
        el.isActive = false;
        return el;
    })

    // Show tourism layer in application maps
    $.each(trekkingLayers, function (i, trekkingLayer) {
        var layer = new L.ObjectsLayer(null, {
            modelname: trekkingLayer.id,
            style: L.Util.extend(window.SETTINGS.map.styles[trekkingLayer.id] || {}, {clickable:false}),
        });
        if (data.modelname != trekkingLayer.id){
            map.layerscontrol.addOverlay(layer, tr(trekkingLayer.name), tr('Trekking'));
        };
        map.on('layeradd', function(e){
            var options = e.layer.options || {'modelname': 'None'};
            if (! trekkingLayer.isActive){
                if (options.modelname == trekkingLayer.id && options.modelname != data.modelname){
                    e.layer.load(trekkingLayer.url);
                    trekkingLayer.isActive = true;
                }
            }
        });
    });
});
