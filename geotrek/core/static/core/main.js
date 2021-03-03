MapEntity.pathsLayer = function buildPathLayer(url, options) {
    var options = options || {};
    options.style = L.Util.extend(options.style || {}, window.SETTINGS.map.styles.path);

    var pathsLayer = new L.ObjectsLayer(url, options);

    // Show paths extremities
    if (window.SETTINGS.showExtremities) {
        pathsLayer.on('data:loaded', function (e) {
            pathsLayer.showExtremities(window.SETTINGS.map.paths_line_marker);
        });
    }
    return pathsLayer;
};

$(window).on('entity:map', function (e, data) {
    var map = data.map;
    var loaded_path = false;
    // Show the path layer only if model is not path, and if we are not
    // in an editing widget
    var is_form_view = /add|update/.test(data.viewname);

    if (!is_form_view && (data.viewname == 'detail' || data.modelname != 'path')) {
        var pathsLayer = MapEntity.pathsLayer(window.SETTINGS.urls.tile.replace(new RegExp('modelname', 'g'), 'path'), {
            indexing: false,
            style: { clickable: false },
            modelname: 'path',
            no_draft: data.modelname != 'path',
        });

        if (data.viewname == 'detail'){
            pathsLayer.addTo(map);
        };
        pathsLayer.on('loaded', function () {
            if (pathsLayer._map)
                pathsLayer.bringToBack();
        });

        var style = pathsLayer.options.style;
        var nameHTML = '<span style="color: '+ style['color'] + ';">&#9473;</span>&nbsp;' + tr('Paths');
        map.layerscontrol.addOverlay(pathsLayer, nameHTML, tr('Objects'));

        //
        // Print apparence of paths
        $(window).on('detailmap:ready', function (e, data) {
            if ((data.modelname != 'path') &&
                (data.context && data.context.print)) {
                var specified = window.SETTINGS.map.styles.print.path;
                pathsLayer.setStyle(L.Util.extend(pathsLayer.options.style, specified));
            }
        });
    }
});

$(window).on('detailmap:ready', function (e, data) {
    var map = data.map,
        layer = data.layer,
        DETAIL_STYLE = window.SETTINGS.map.styles.detail;

    if (data.context && data.context.print) {
        var specified = window.SETTINGS.map.styles.print[data.modelname];
        DETAIL_STYLE = L.Util.extend(DETAIL_STYLE, specified || {});
    }

    // Show start and end
    layer.eachLayer(function (layer) {
        if (layer instanceof L.Polygon)
            return;
        if (typeof layer.getLatLngs != 'function')  // points
            return;

        // Show start and end markers (similar to edition)
        var imagePath = window.SETTINGS.urls.static + "core/images/";
        L.marker(layer.getLatLngs()[0], {
            clickable: false,
            icon: new L.Icon.Default({
                imagePath: imagePath,
                iconUrl: "marker-source.png",
                iconRetinaUrl: "marker-source-2x.png"
            })
        }).addTo(map);
        L.marker(layer.getLatLngs().slice(-1)[0], {
            clickable: false,
            icon: new L.Icon.Default({
                imagePath: imagePath,
                iconUrl: "marker-target.png",
                iconRetinaUrl: "marker-target-2x.png"
            })
        }).addTo(map);

        // Also add line orientation
        layer.setText('>     ', {repeat: true,
                                 offset: DETAIL_STYLE.weight,
                                 attributes: {'fill': DETAIL_STYLE.arrowColor,
                                              'font-size': DETAIL_STYLE.arrowSize}});
    });
});