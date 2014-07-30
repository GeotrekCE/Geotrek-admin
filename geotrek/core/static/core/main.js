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

        pathsLayer.on('loaded', function () {
            if (pathsLayer._map)
                pathsLayer.bringToBack();
        });

        map.on('layeradd', function (e) {
            if (e.layer === pathsLayer) {
                if (!e.layer._map) {
                    return;
                }
                if (e.layer.loading) {
                    e.layer.on('loaded', function () {
                        if (!e.layer._map) {
                            return;
                        }
                        e.layer.bringToBack();
                    });
                }
                else {
                    e.layer.bringToBack();
                }
            }
            else {
                if (e.layer instanceof L.ObjectsLayer) {
                    if (e.layer.loading) {
                        e.layer.on('loaded', function () {
                            if (!e.layer._map) {
                                return;
                            }
                            e.layer.bringToFront();
                        });
                    }
                    else {
                        e.layer.bringToFront();
                    }
                }
            }
        });

        var style = pathsLayer.options.style;
        var nameHTML = '<span style="color: '+ style['color'] + ';">&#9473;</span>&nbsp;' + tr('Paths');
        map.layerscontrol.addOverlay(pathsLayer, nameHTML, tr('Objects'));
    }
});

$(window).on('entity:view:list', function () {
    // Move all topology-filters to separate tab
    $('#mainfilter .topology-filter').parent('p')
                                     .detach().appendTo('#mainfilter > .right');
});
