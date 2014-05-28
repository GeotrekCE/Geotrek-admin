$(window).on('entity:map', function (e, data) {
    var map = data.map;

    // Show the path layer only if model is not path, and if we are not
    // in an editing widget
    if (!/add|update/.test(data.view) && (data.view == 'detail' || data.modelname != 'path')) {
        var paths = new L.ObjectsLayer(null, {
            indexing: false,
            style: L.Util.extend(window.SETTINGS.map.styles.path, { clickable:false })
        });
        paths.load(window.SETTINGS.urls.path_layer);
        map.layerscontrol.addOverlay(paths, tr('Paths'));
        paths.addTo(map);
        paths.on('data:loaded', function (e) {
            paths.showExtremities(window.SETTINGS.map.paths_line_marker);
        });
    }
});

$(window).on('entity:view:list', function () {
    // Move all topology-filters to separate tab
    $('#mainfilter .topology-filter').parent('p')
                                     .detach().appendTo('#mainfilter > .right');
});
