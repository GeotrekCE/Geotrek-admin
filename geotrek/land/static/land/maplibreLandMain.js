document.addEventListener("entity:map", (e) => {
    const { map } = e.detail;
    const managementLayers = [
        { url: window.SETTINGS.urls.landedge_layer, name: tr('Land type'), id: 'land' },
        { url: window.SETTINGS.urls.physicaledge_layer, name: tr('Physical type'), id: 'physical' },
        { url: window.SETTINGS.urls.circulationedge_layer, name: tr('Circulation type'), id: 'circulation' },
        { url: window.SETTINGS.urls.competenceedge_layer, name: tr('Competence'), id: 'competence' },
        { url: window.SETTINGS.urls.signagemanagementedge_layer, name: tr('Signage management edges'), id: 'signagemanagement' },
        { url: window.SETTINGS.urls.workmanagementedge_layer, name: tr('Work management edges'), id: 'workmanagement' }
    ];

    let nameHTML = '';
    let objectsLayers = [];

    for (let managementLayer of managementLayers) {
        let style = window.SETTINGS.map.styles[managementLayer.id] || {};

        let layer = new MaplibreObjectsLayer(null, {
            modelname: managementLayer.name,
            style: style,
        });

        layer.load(managementLayer.url);
        managementLayer.isActive = true;

        objectsLayers.push(layer);
        nameHTML += managementLayer.name;
        // map.layerscontrol.addOverlay(layer, nameHTML, tr('Status'));
    }

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
});
