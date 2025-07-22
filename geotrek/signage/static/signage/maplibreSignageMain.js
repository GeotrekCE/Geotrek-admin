//
// Signage
//

window.addEventListener('entity:map', (event) => {
    const { map } = event.detail;
    const modelname = 'signage';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];

    // Show signage layer in application maps
    const style = {
        color: 'blue',
        weight: 2,
        opacity: 0.5,
        fillColor: '#FF0000',
        fillOpacity: 0.1
    };

    const nameHTML = tr('Signage');
    const category = tr('Signage');

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