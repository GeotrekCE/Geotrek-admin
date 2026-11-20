window.addEventListener('entity:map', () => {
    const map = window.MapEntity.currentMap.map;
    const colorspools = window.SETTINGS.map.colorspool || {};

    // Regroupement des couches de terrain (districts, villes + zones restreintes)
    let landLayers = [
        { url: window.SETTINGS.urls.district_layer, name: gettext("Districts"), id: 'district' },
        { url: window.SETTINGS.urls.city_layer, name: gettext("Cities"), id: 'city' },
        ...window.SETTINGS.map['restricted_area_types']
    ].map((layer, index) => {
        layer.isActive = false;
        return layer;
    });

    landLayers.forEach((landLayer, i) => {
        const style = window.SETTINGS.map.styles[landLayer.id] ?? window.SETTINGS.map.styles['others'];
        // Couleur personnalisée par colorspool
        const pool = colorspools[landLayer.id];
        if (pool) {
            const color = pool[(i < 2 ? i : i - 2) % pool.length];
            style.color = color;
        }

        const nameHTML = `<span style="color: ${style.color};">&#x2B24;</span>&nbsp;${landLayer.name}`;
        const category = tr('Zoning');
        let primaryKey = generateUniqueId();

        const layer = new MaplibreObjectsLayer(null, {
            modelname: landLayer.name,
            style: style,
            readonly: true,
            nameHTML: nameHTML,
            category: category,
            primaryKey: primaryKey,
            dataUrl: landLayer.url,
            isLazy: true
        });

        layer.initialize(map.getMap());
        layer.registerLazyLayer(landLayer.name, category, nameHTML, primaryKey, landLayer.url);

    });
});
