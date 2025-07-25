window.addEventListener("entity:map", function (event) {
    const map = window.MapEntity.currentMap.map;

    const modelname = 'infrastructure';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];

    const nameHTML = tr('Infrastructure');
    const category = tr('Infrastructure');
    const primaryKey = generateUniqueId();

    const style = window.SETTINGS.map.styles[modelname] ?? window.SETTINGS.map.styles['autres'];

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