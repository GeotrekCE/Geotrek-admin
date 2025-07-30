MapEntity.pathsLayer = function buildPathLayer(options) {
    let pathsLayerOptions = options || {};
    pathsLayerOptions.style = Object.assign({}, options.style, window.SETTINGS.map.styles.path,);

    const pathsLayer = new MaplibreObjectsLayer(null, options);

    // // Show paths extremities
    // if (window.SETTINGS.showExtremities) {
    //     pathsLayer.on('data:loaded', function (e) {
    //         pathsLayer.showExtremities(window.SETTINGS.map.paths_line_marker);
    //     });
    // }
    return pathsLayer;
};

window.addEventListener('entity:map', (e) => {
    const map = window.MapEntity.currentMap.map;
    let loadedPath = false;

    // Show the path layer only if model is not path, and if we are not
    // in an editing widget or when it's not a topology
    const isFormView = /add|update/.test(window.MapEntity.currentMap.viewname);
    const isNotTopology = /dive|report|touristiccontent|touristicevent|site|course/.test(window.MapEntity.currentMap.modelname);

    if (isNotTopology || (!isFormView && (window.MapEntity.currentMap.viewname === 'detail' || window.MapEntity.currentMap.modelname !== 'path'))) {
        const pathsLayer = MapEntity.pathsLayer({
            modelname: 'path',
            // no_draft: window.MapEntity.currentMap.modelname !== 'path', // no_draft is not used in MaplibreObjectsLayer
        });

        if (window.MapEntity.currentMap.viewname === 'detail') {
            pathsLayer.load(window.SETTINGS.urls.path_layer);
            pathsLayer.addTo(map);
        }

        pathsLayer.on('loaded', () => {
            if (pathsLayer._map) {
                pathsLayer.bringToBack();
            }
        });

        map.on('layeradd', (e) => {
            // Start ajax loading at last
            const url = window.SETTINGS.urls.path_layer;

            const options = e.layer.options || { modelname: 'None' };
            if (!loadedPath) {
                if (options.modelname === 'path' && window.MapEntity.currentMap.viewname !== 'detail') {
                    e.layer.load(`${url}?_no_draft=true`, true);
                    loadedPath = true;
                }
            }

            if (e.layer === pathsLayer) {
                if (!e.layer._map) {
                    return;
                }
                if (e.layer.loading) {
                    e.layer.on('loaded', () => {
                        if (!e.layer._map) return;
                        e.layer.bringToBack();
                    });
                } else {
                    e.layer.bringToBack();
                }
            }
        });
    }
})