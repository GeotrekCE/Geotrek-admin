$(window).on('entity:map', function (e, data) {

    var map = data.map;
    var loaded_district = false;
    var loaded_city = false;

    $.each([[tr("Districts"), 'district'], [tr("Cities"), 'city']], function (i, modelname, name) {
        var style = L.Util.extend({clickable: false},
                                  window.SETTINGS.map.styles[modelname[1]] || {});
        var nameHTML = '<span style="color: '+ style['color'] + ';">&#x2B24;</span>&nbsp;' + modelname[0];
        var layer = new L.ObjectsLayer(null, {
                indexing: false,
                modelname: modelname[1],
                style: style,
        });
        map.layerscontrol.addOverlay(layer, nameHTML, tr('Zoning'));

        map.on('layeradd', function(e){
            var options = e.layer.options || {'modelname': 'None'};
            if (! loaded_district){
                if (options.modelname == 'district'){
                    e.layer.load(window.SETTINGS.urls.district_layer);
                    loaded_district = true;
                }
            }
            if (! loaded_city){
                if (options.modelname == 'city'){
                    e.layer.load(window.SETTINGS.urls.city_layer);
                    loaded_city = true;
                }
            }
        });
    });
});