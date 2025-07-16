window.addEventListener('entity:map', (event) => {
    const { map } = event.detail;
    let loaded_site = false;
    let loaded_course = false;

    ['site', 'course'].forEach((modelname) => {
        const layername = `${modelname}_layer`;
        const layerUrl = window.SETTINGS.urls[layername];
        const style = window.SETTINGS.map.styles[modelname] || {};

        // Show site and course layers in application maps
        const objectsLayer = new MaplibreObjectsLayer(null, {
            style,
            modelname: modelname,
            readonly: false
        });

        // if (event.detail.modelname !== modelname) {
        //     map.layerscontrol.addOverlay(objectsLayer, tr(modelname.charAt(0).toUpperCase() + modelname.slice(1)), tr(modelname.charAt(0).toUpperCase() + modelname.slice(1)));
        // }

        // map.getMap().on('layeradd', (e) => {
        //     const options = e.layer.options || { 'modelname': 'None' };
        //     if (!loaded_site && modelname === 'site') {
        //         if (options.modelname === modelname && options.modelname !== event.detail.modelname) {
        //             e.layer.load(layerUrl);
        //             loaded_site = true;
        //         }
        //     } else if (!loaded_course && modelname === 'course') {
        //         if (options.modelname === modelname && options.modelname !== event.detail.modelname) {
        //             e.layer.load(layerUrl);
        //             loaded_course = true;
        //         }
        //     }
        // });
    });

})