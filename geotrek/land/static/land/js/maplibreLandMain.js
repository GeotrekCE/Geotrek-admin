window.addEventListener("entity:map", () => {
    const map = window.MapEntity.currentMap.map;


    const managementLayers = [
        { url: window.SETTINGS.urls.landedge_layer, name: tr('Land type'), id: 'land' },
        { url: window.SETTINGS.urls.physicaledge_layer, name: tr('Physical type'), id: 'physical' },
        { url: window.SETTINGS.urls.circulationedge_layer, name: tr('Circulation type'), id: 'circulation' },
        { url: window.SETTINGS.urls.competenceedge_layer, name: tr('Competence'), id: 'competence' },
        { url: window.SETTINGS.urls.signagemanagementedge_layer, name: tr('Signage management edges'), id: 'signagemanagement' },
        { url: window.SETTINGS.urls.workmanagementedge_layer, name: tr('Work management edges'), id: 'workmanagement' }
    ];

    const colorspools = window.SETTINGS.map?.colorspool || {};
    const category = tr('Status');

    for (const managementLayer of managementLayers) {
        let nameHTML = '';
        const colors = colorspools[managementLayer.id] || [];

        // Génère un petit symbole coloré de légende (limité à 4 max)
        for (let j = 0; j < Math.min(colors.length, 4); j++) {
            nameHTML += `<span style="color: ${colors[j]};">|</span>`;
        }

        nameHTML += `&nbsp;${managementLayer.name}`;
        let primaryKey = generateUniqueId();

        let style = window.SETTINGS.map.styles[managementLayer.id] ?? window.SETTINGS.map.styles['autres'];
        const layer = new MaplibreObjectsLayer(null, {
            modelname: managementLayer.name,
            style: style,
            nameHTML: nameHTML,
            category: category,
            readonly: true,
            primaryKey: primaryKey,
            dataUrl: managementLayer.url,
            isLazy: true
        });

        layer.initialize(map.getMap());
        layer.registerLazyLayer(managementLayer.name, category, nameHTML, primaryKey, managementLayer.url);
    }
});