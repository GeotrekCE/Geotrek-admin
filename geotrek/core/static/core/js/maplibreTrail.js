window.addEventListener("entity:map", () => {
    const map = window.MapEntity.currentMap.map;
    const modelname = 'trail';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];

    const nameHTML = tr('Trails');
    const category = tr('Trail');
    const primaryKey = generateUniqueId();
    const style = window.SETTINGS.map.styles['path'] ?? window.SETTINGS.map.styles['autres'];

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
    objectsLayer.registerLazyLayer(modelname,category,nameHTML, primaryKey, layerUrl);
});