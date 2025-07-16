
window.addEventListener("entity:map", function (event) {
    const { map } = event.detail;
    const modelname = 'infrastructure';
    const layername = `${modelname}_layer`;

    const layerUrl = window.SETTINGS.urls[layername];
    let loaded_infrastructure = false;

    const style = window.SETTINGS.map.styles[modelname] || {};
    const objectsLayer = new MaplibreObjectsLayer(null, {
            style,
            modelname: modelname,
            readonly: false
    });

    // if (data.modelname != modelname){
	//     map.layerscontrol.addOverlay(layer, tr('Intervention'), tr('Maintenance'));
    // }

    // map.getMap().on('layeradd', function (e) {
    //     const options = e.layer.options || { 'modelname': 'None' };
    //     if (! loaded_infrastructure) {
    //         if(options.modelname === modelname && options.modelname !== event.detail.modelname) {
    //             e.layer.load(url);
    //             objectsLayer.load(layerUrl);
    //             loaded_infrastructure = true;
    //         }
    //     }
    // });

})