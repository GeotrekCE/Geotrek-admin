//
// Signage
//

window.addEventListener('entity:map', () => {
    const map = window.MapEntity.currentMap.map;
    const modelname = 'signage';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];

    // Show signage layer in application maps
    const style = window.SETTINGS.map.styles[modelname] ?? window.SETTINGS.map.styles['autres'];

    const nameHTML = tr('Signage');
    const category = tr('Signage');
    const primaryKey = generateUniqueId();

    const objectsLayer = new MaplibreObjectsLayer(null, {
        style: style,
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