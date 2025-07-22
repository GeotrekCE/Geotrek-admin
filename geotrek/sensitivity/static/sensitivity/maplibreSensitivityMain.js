//
// Sensitivity
//

window.addEventListener('entity:map', (event) => {
    const { map } = event.detail;
    const modelname = 'sensitivearea';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];
    // let loaded_sensitivearea = false;

    // Show sensitivearea layer in application maps
    const style = {
        color: 'blue',
        weight: 2,
        opacity: 0.5,
        fillColor: '#FF0000',
        fillOpacity: 0.1
    };

    const nameHTML = tr('sensitivearea');
    const category = tr('Sensitivity');

    const objectsLayer = new MaplibreObjectsLayer(null, {
        style,
        modelname: modelname,
        readonly: false,
        nameHTML: nameHTML,
        category: category
    });

    objectsLayer.initialize(map.getMap());
    objectsLayer.load(layerUrl);
});

// if (event.detail.modelname !== modelname) {
    //     map.layerscontrol.addOverlay(objectsLayer, tr('sensitivearea'), tr('Sensitivity'));
    // }

    // map.getMap().on('layeradd', function (e) {
    //     const options = e.layer.options || { 'modelname': 'None' };
    //     if (!loaded_sensitivearea) {
    //         if (options.modelname === modelname && options.modelname !== e.detail.modelname) {
    //             e.layer.load(layerUrl);
    //             loaded_sensitivearea = true;
    //         }
    //     }
    // });