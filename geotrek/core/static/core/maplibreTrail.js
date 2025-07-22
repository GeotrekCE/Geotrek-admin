window.addEventListener("entity:map", (e) => {
    const {map} = e.detail;
    const modelname = 'trail';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];

    const nameHTML = tr('Trails');
    const category = tr('Trail');

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