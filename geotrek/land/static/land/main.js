$(window).on('entity:map', function (e, data) {

    var map = data.map;

    var managementLayers = [{ url: window.SETTINGS.urls.landedge_layer, name: tr('Land type'), id: 'land' },
    { url: window.SETTINGS.urls.physicaledge_layer, name: tr('Physical type'), id: 'physical' },
    { url: window.SETTINGS.urls.circulationedge_layer, name: tr('Circulation type'), id: 'circulation' },
    { url: window.SETTINGS.urls.competenceedge_layer, name: tr('Competence'), id: 'competence' },
    { url: window.SETTINGS.urls.signagemanagementedge_layer, name: tr('Signage management edges'), id: 'signagemanagement' },
    { url: window.SETTINGS.urls.workmanagementedge_layer, name: tr('Work management edges'), id: 'workmanagement' }];
    managementLayers.map(function (el) {
        el.isActive = false;
        return el;
    })

    var colorspools = L.Util.extend({}, window.SETTINGS.map.colorspool);
    for (var i = 0; i < managementLayers.length; i++) {
        var managementLayer = managementLayers[i];

        var style = L.Util.extend({ clickable: false },
            window.SETTINGS.map.styles[managementLayer.id] || {});
        var layer = new L.ObjectsLayer(null, {
            modelname: managementLayer.name,
            style: style,
            onEachFeature: initLandLayer(managementLayer),
        });
        var colorspool = colorspools[managementLayer.id];
        var nameHTML = '';
        for (var j = 0; j < 4; j++) {
            nameHTML += ('<span style="color: ' + colorspool[j] + ';">|</span>');
        }
        nameHTML += ('&nbsp;' + managementLayer.name);
        map.layerscontrol.addOverlay(layer, nameHTML, tr('Status'));
    };
    map.on('layeradd', function (e) {
        var options = e.layer.options || { 'modelname': 'None' };
        for (var i = 0; i < managementLayers.length; i++) {
            if (!managementLayers[i].isActive) {
                if (options.modelname == managementLayers[i].name) {
                    e.layer.load(managementLayers[i].url);
                    managementLayers[i].isActive = true;
                }
            }
        }
    });

    function initLandLayer(layergroup) {
        return function (data, layer) {
            var idx = parseInt(data.properties.color_index, 10);
            if (isNaN(idx)) {
                console.warn("No proper 'color_index' properties in GeoJSON properties.");
                idx = 0;
            }
            var colorspool = colorspools[layergroup.id],
                color = colorspool[idx % colorspool.length];
            layer.setStyle({ color: color });

            if (window.SETTINGS.showLabels && data.properties.name) {
                // Add label in the middle of the line
                MapEntity.showLineLabel(layer, {
                    color: color,
                    text: data.properties.name,
                    title: layergroup.name,
                    className: 'landlabel ' + layergroup.id + ' ' + idx
                });
            }
        };
    }
});
