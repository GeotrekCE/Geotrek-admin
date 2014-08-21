$(window).on('entity:map', function (e, data) {

    var map = data.map;

    // Add management layers
    var managementLayers = [{url: window.SETTINGS.urls.landedge_layer, name: tr('Land type'), id: 'land'},
                            {url: window.SETTINGS.urls.physicaledge_layer, name: tr('Physical type'), id: 'physical'},
                            {url: window.SETTINGS.urls.competenceedge_layer, name: tr('Competence'), id: 'competence'},
                            {url: window.SETTINGS.urls.signagemanagementedge_layer, name: tr('Signage management'), id: 'signagemanagement'},
                            {url: window.SETTINGS.urls.workmanagementedge_layer, name: tr('Work management'), id: 'workmanagement'}];

    // We have a list of colors, each layer has a *color_index*, and will *consume* a color
    // from the list. This way we may not have the same color twice on the map.
    var colorspools = L.Util.extend({}, window.SETTINGS.map.colorspool);

    for (var i=0; i<managementLayers.length; i++) {
        var managementLayer = managementLayers[i];

        var layer = new L.ObjectsLayer(null, {
            indexing: false,
            modelname: managementLayer.id,
            style: L.Util.extend(window.SETTINGS.map.styles[managementLayer.id], {clickable:false}),
            onEachFeature: initLandLayer(managementLayer),
        });
        layer.load(managementLayer.url);

        var colorspool = colorspools[managementLayer.id];
        var nameHTML = '';
        for (var j=0; j<4; j++) {
            nameHTML += ('<span style="color: '+ colorspool[j] + ';">|</span>');
        }
        nameHTML += ('&nbsp;' + managementLayer.name);
        map.layerscontrol.addOverlay(layer, nameHTML, tr('Land edges'));
    }


    function initLandLayer(layergroup) {
        return function (data, layer) {
            var idx = parseInt(data.properties.color_index, 10);
            if (isNaN(idx)) {
                console.warn("No proper 'color_index' properties in GeoJSON properties.");
                idx = 0;
            }
            var colorspool = colorspools[layergroup.id],
                color = colorspool[idx % colorspool.length];
            layer.setStyle({color: color});

            // Add label in the middle of the line
            if (data.properties.name) {
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
