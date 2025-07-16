//
// Sensitivity
//

window.addEventListener('entity:map', (event) => {
    const { map } = event.detail;
    const modelname = 'sensitivearea';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];
    let loaded_sensitivearea = false;

    // Show sensitivearea layer in application maps
    const style =  window.SETTINGS.map.styles[modelname] ;
    const objectsLayer = new MaplibreObjectsLayer(null, {
        style,
        modelname: modelname,
        readonly: false
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
});