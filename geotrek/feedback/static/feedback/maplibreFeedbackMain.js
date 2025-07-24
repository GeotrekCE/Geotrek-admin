//
// Feedback / reports
//

window.addEventListener('entity:map', function () {
    const map = window.MapEntity.currentMap.map;
    const modelname = 'report';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];

    const nameHTML = tr('Report');
    const category = tr('Feedback');
    const primaryKey = generateUniqueId();

    const style = {
        color: 'blue',
        weight: 2,
        opacity: 0.5,
        fillColor: '#FF0000',
        fillOpacity: 0.1
    };

    const objectsLayer = new MaplibreObjectsLayer(null, {
        style,
        modelname: modelname,
        readonly: true,
        nameHTML: nameHTML,
        category: category,
        primaryKey: primaryKey,
        dataUrl: layerUrl,
        isLazy: true
    });

    objectsLayer.initialize(map.getMap());
    objectsLayer.registerLazyLayer(modelname, category, nameHTML, primaryKey, layerUrl);
});