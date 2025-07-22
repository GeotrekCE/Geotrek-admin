window.addEventListener("entity:map", function (event) {
    const { map } = event.detail;

    const modelname = 'infrastructure';
    const layername = `${modelname}_layer`;
    const layerUrl = window.SETTINGS.urls[layername];

    const nameHTML = tr('Infrastructure');
    const category = tr('Infrastructure');

    const style = {
        color: 'blue',
        weight: 2,
        opacity: 0.5,
        fillColor: '#FF0000',
        fillOpacity: 0.1
    };

    const objectsLayer = new MaplibreObjectsLayer(null, {
        style: style,
        modelname: modelname,
        readonly: false,
        nameHTML: nameHTML,
        category: category
    });

    objectsLayer.initialize(map.getMap());
    objectsLayer.load(layerUrl);
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