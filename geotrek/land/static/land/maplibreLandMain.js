window.addEventListener("entity:map", (e) => {
    const { map } = e.detail;

    const managementLayers = [
        { url: window.SETTINGS.urls.landedge_layer, name: tr('Land type'), id: 'land' },
        { url: window.SETTINGS.urls.physicaledge_layer, name: tr('Physical type'), id: 'physical' },
        { url: window.SETTINGS.urls.circulationedge_layer, name: tr('Circulation type'), id: 'circulation' },
        { url: window.SETTINGS.urls.competenceedge_layer, name: tr('Competence'), id: 'competence' },
        { url: window.SETTINGS.urls.signagemanagementedge_layer, name: tr('Signage management edges'), id: 'signagemanagement' },
        { url: window.SETTINGS.urls.workmanagementedge_layer, name: tr('Work management edges'), id: 'workmanagement' }
    ];

    const colorspools = window.SETTINGS.map?.colorspool || {};
    const style = {
        color: 'blue',
        weight: 2,
        opacity: 0.5,
        fillColor: '#FF0000',
        fillOpacity: 0.1
    };

    const category = tr('Status');
    const objectsLayers = [];

    for (const managementLayer of managementLayers) {
        let nameHTML = '';
        const colors = colorspools[managementLayer.id] || [];

        // Génère un petit symbole coloré de légende (limité à 4 max)
        for (let j = 0; j < Math.min(colors.length, 4); j++) {
            nameHTML += `<span style="color: ${colors[j]};">|</span>`;
        }

        nameHTML += `&nbsp;${managementLayer.name}`;

        const layer = new MaplibreObjectsLayer(null, {
            modelname: managementLayer.name,
            style: style,
            nameHTML: nameHTML,
            category: category
        });

        layer.initialize(map.getMap());
        layer.load(managementLayer.url);
        managementLayer.isActive = true;

        objectsLayers.push(layer);
    }
});

    // Ajoute dans la légende de la carte
    // map.layerscontrol.addOverlay(layer, nameHTML, category);

    // map.getMap().on('layeradd', (e) => {
    //     const options = e.layer.options || { 'modelname': 'None' };
    //     for (let managementLayer of managementLayers) {
    //         if (!managementLayer.isActive) {
    //             if (options.modelname === managementLayer.name) {
    //                 e.layer.load(managementLayer.url);
    //                 managementLayer.isActive = true;
    //             }
    //         }
    //     }
    // });