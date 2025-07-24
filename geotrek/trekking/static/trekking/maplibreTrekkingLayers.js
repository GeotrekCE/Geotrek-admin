//
// Trekking
//

window.addEventListener("entity:map", function (event) {
    const map = window.MapEntity.currentMap.map;

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
        const nameHTML = tr(trekkingLayer.name);
        const category = tr('Trekking');

        const style = {
            color: 'blue',
            weight: 2,
            opacity: 0.5,
            fillColor: '#FF0000',
            fillOpacity: 0.1
        };

        let primaryKey = generateUniqueId();

        const layer = new MaplibreObjectsLayer(null, {
            modelname: trekkingLayer.name,
            style: style,
            readonly: true,
            nameHTML: nameHTML,
            category: category,
            primaryKey: primaryKey,
            dataUrl: trekkingLayer.url,
            isLazy: true
        });

        layer.initialize(map.getMap());
        layer.registerLazyLayer(trekkingLayer.name, category, nameHTML, primaryKey, trekkingLayer.url);
    });
});
