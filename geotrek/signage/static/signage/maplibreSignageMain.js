//
// Signage
//

window.addEventListener('entity:map', (event) => {
    const { map } = event.detail;
    const modelname = 'signage';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];
    let loadedSignage = false;

    // Show signage layer in application maps
    const style = window.SETTINGS.map.styles[modelname] || {};
    const objectsLayer = new MaplibreObjectsLayer(null, {
        style,
        modelname: modelname,
        readonly: false
    });

    // if (event.detail.modelname !== modelname) {
    //     map.layerscontrol.addOverlay(objectsLayer, tr('Signages'), tr('Signage'));
    // }

    // map.getMap().on('layeradd', (e) => {
    //     const options = e.layer.options || { 'modelname': 'None' };
    //     if (!loadedSignage) {
    //         if (options.modelname === modelname && options.modelname !== event.detail.modelname) {
    //             e.layer.load(layerUrl);
    //             objectsLayer.load(layerUrl);
    //             loadedSignage = true;
    //         }
    //     }
    // });
});