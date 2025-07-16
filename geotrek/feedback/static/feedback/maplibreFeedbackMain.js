//
// Feedback / reports
//

window.addEventListener('entity:map', function (event) {
    const { map } = event.detail;
    const modelname = 'report';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];
    let loadedFeedback = false;

    // Show report layer in application maps
    const style =  window.SETTINGS.map.styles[modelname] || {};
    const objectsLayer = new MaplibreObjectsLayer(null, {
        style,
        modelname: modelname,
        readonly: false
    });

    // if (event.detail.modelname !== modelname) {
    //     map.layerscontrol.addOverlay(objectsLayer, tr('Report'), tr('Feedback'));
    // }

    // map.getMap().on('layeradd', function (e) {
    //     const options = e.layer.options || { 'modelname': 'None' };
    //     if (!loadedFeedback) {
    //         if (options.modelname === modelname && options.modelname !== event.detail.modelname) {
    //             e.layer.load(layerUrl);
    //             objectsLayer.load(layerUrl);
    //             loadedFeedback = true;
    //         }
    //     }
    // });
})