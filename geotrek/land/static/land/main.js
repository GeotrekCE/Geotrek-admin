$(window).on('entity:map', function (e, data) {

    var map = data.map;
    var loaded_land = false;
    var loaded_physical = false;
    var loaded_competence = false;
    var loaded_signagemanagement = false;
    var loaded_workmanagement = false;
    var colorspools = L.Util.extend({}, window.SETTINGS.map.colorspool);
    $.each([[tr('Land type'), 'land'], [tr('Physical type'), 'physical'], [tr('Competence'), 'competence'],
            [tr('Signage management'), 'signagemanagement'],[tr('Work management'), 'workmanagement']], function (i, modelname) {
        var style = L.Util.extend({clickable: false},
                                  window.SETTINGS.map.styles[modelname[1]] || {});
        var layer = new L.ObjectsLayer(null, {
            modelname: modelname[1],
            style: style,
            onEachFeature: initLandLayer(modelname),
        });
        var colorspool = colorspools[modelname[1]];
        var nameHTML = '';
        for (var j=0; j<4; j++) {
            nameHTML += ('<span style="color: '+ colorspool[j] + ';">|</span>');
        }
        nameHTML += ('&nbsp;' + modelname[0]);
        map.layerscontrol.addOverlay(layer, nameHTML, tr('Land edges'));
    });
    map.on('layeradd', function(e){
        var options = e.layer.options || {'modelname': 'None'};
        if (! loaded_land){
            if (options.modelname == 'land'){
                e.layer.load(window.SETTINGS.urls.landedge_layer);
                loaded_land = true;
            }
        }
        if (! loaded_physical){
            if (options.modelname == 'physical'){
                e.layer.load(window.SETTINGS.urls.physicaledge_layer);
                loaded_physical = true;
            }
        }
        if (! loaded_competence){
            if (options.modelname == 'competence'){
                e.layer.load(window.SETTINGS.urls.competenceedge_layer);
                loaded_competence = true;
            }
        }
        if (! loaded_signagemanagement){
            if (options.modelname == 'signagemanagement'){
                e.layer.load(window.SETTINGS.urls.signagemanagementedge_layer);
                loaded_signagemanagement = true;
            }
        }
        if (! loaded_workmanagement){
            if (options.modelname == 'workmanagement'){
                e.layer.load(window.SETTINGS.urls.workmanagementedge_layer);
                loaded_workmanagement = true;
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
            var colorspool = colorspools[layergroup[1]],
                color = colorspool[idx % colorspool.length];
            layer.setStyle({color: color});

            // Add label in the middle of the line
            if (data.properties.name) {
                MapEntity.showLineLabel(layer, {
                    color: color,
                    text: data.properties.name,
                    title: layergroup[0],
                    className: 'landlabel ' + layergroup[1] + ' ' + idx
                });
            }
        };
    }
});
