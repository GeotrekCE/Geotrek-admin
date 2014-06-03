MapEntity.pathsLayer = function buildPathLayer(options) {
    var options = options || {};
    options.style = L.Util.extend(options.style || {}, window.SETTINGS.map.styles.path);

    var pathsLayer = new L.ObjectsLayer(null, options);

    // Show paths extremities
    pathsLayer.on('data:loaded', function (e) {
        pathsLayer.showExtremities(window.SETTINGS.map.paths_line_marker);
    });

    // Start ajax loading at last
    pathsLayer.load(window.SETTINGS.urls.path_layer, true);

    return pathsLayer;
};


$(window).on('entity:map', function (e, data) {
    var map = data.map;

    // Show the path layer only if model is not path, and if we are not
    // in an editing widget
    if (!/add|update/.test(data.view) && (data.view == 'detail' || data.modelname != 'path')) {

        var pathsLayer = MapEntity.pathsLayer({
            indexing: false,
            style: { clickable:false }
        });
        pathsLayer.addTo(map);

        map.on('layeradd', function (e) {

            if (!pathsLayer._map) {
                // Paths currently not shown
                return;
            }

            // Bring to back when the last path item is added
            var layers = pathsLayer.getLayers(),
                last = layers[layers.length - 1];
            if (e.layer == last) {
                pathsLayer.bringToBack();
            }
        });

        map.layerscontrol.addOverlay(pathsLayer, tr('Paths'));
    }
});

$(window).on('entity:view:list', function () {
    // Move all topology-filters to separate tab
    $('#mainfilter .topology-filter').parent('p')
                                     .detach().appendTo('#mainfilter > .right');
});
