window.addEventListener('entity:map', () => {
    const map = window.MapEntity.currentMap.map;

    ['site', 'course'].forEach((modelname) => {
        const layername = `${modelname}_layer`;
        const layerUrl = window.SETTINGS.urls[layername];
        let style = window.SETTINGS.map.styles[modelname] ?? window.SETTINGS.map.styles['autres'];
        const nameHTML = tr(modelname);
        const category = tr('Outdoor');
        let primaryKey = generateUniqueId();

        // Show site and course layers in application maps
        const objectsLayer = new MaplibreObjectsLayer(null, {
            style: style,
            modelname: modelname,
            readonly: false,
            nameHTML: nameHTML,
            category: category,
            primaryKey: primaryKey,
            dataUrl: layerUrl,
            isLazy: true
        });

        objectsLayer.initialize(map.getMap());
        objectsLayer.registerLazyLayer(modelname, category, nameHTML, primaryKey, layerUrl);

    });
});