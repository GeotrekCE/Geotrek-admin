//
// Feedback / reports
//

window.addEventListener('entity:map', function (event) {
    const { map } = event.detail;
    const modelname = 'report';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];

    const nameHTML = tr('Report');
    const category = tr('Feedback');

    const style = {
        color: 'blue',
        weight: 2,
        opacity: 0.5,
        fillColor: '#FF0000',
        fillOpacity: 0.1
    };

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