//
// Trekking
//

window.addEventListener("entity:map", function (event) {
    const { map } = event.detail;

    let trekkingLayers = [
        { url: window.SETTINGS.urls.trek_layer, name: tr('Treks'), id: 'trek' },
        { url: window.SETTINGS.urls.poi_layer, name: tr('POI'), id: 'poi' },
        { url: window.SETTINGS.urls.service_layer, name: tr('Services'), id: 'service' },
    ]
    trekkingLayers.map(function (el) {
        el.isActive = false;
        return el;
    })

    // Show tourism layer in application maps
    trekkingLayers.forEach(function (trekkingLayer) {
        const layer = new MaplibreObjectsLayer(null, {
            modelname: trekkingLayer.id,
            style: window.SETTINGS.map.styles[trekkingLayer.id] || {},
        });

        // if (event.detail.modelname !== trekkingLayer.id) {
        //     map.layerscontrol.addOverlay(layer, tr(trekkingLayer.name), tr('Trekking'));
        // }
        //
        // map.getMap().on('layeradd', function (e) {
        //     const options = e.layer.options || {'modelname': 'None'};
        //     if (! trekkingLayer.isActive) {
        //         if (options.modelname === trekkingLayer.id && options.modelname !== event.detail.modelname) {
        //             e.layer.load(trekkingLayer.url);
        //             trekkingLayer.isActive = true;
        //         }
        //     }
        // });
    });
});
