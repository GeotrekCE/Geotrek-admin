window.addEventListener("entity:map", (e) => {
    const {map} = e.detail;
    const modelname = 'dive';
    const layername = `${modelname}_layer`;
    const style = window.SETTINGS.map.styles[modelname] || {};
    const layerUrl = window.SETTINGS.urls[layername];

    const objectsLayer = new MaplibreObjectsLayer(null, {
            style,
            modelname: modelname,
            readonly: false
    });

    // if (data.modelname != modelname){
	//     map.layerscontrol.addOverlay(layer, tr('Diving'), tr('Diving'));
    // };

     // Charger les objets depuis le backend
    // map.getMap().on('layeradd', function (e) {
    //     let options = e.layer.options || { 'modelname': 'None' };
    //     if (! loaded_dive) {
    //         if(options.modelname === modelname && options.modelname !== e.detail.modelname) {
    //             e.layer.load(layerUrl);
    //             objectsLayer.load(layerUrl);
    //             loaded_dive = true;
    //         }
    //     }
    // });

})