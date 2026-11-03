$(window).on('entity:map', function (e, data) {

    var map = data.map;

    var landLayers = [
        { url: window.SETTINGS.urls.district_layer, name: tr("Districts"), id: 'district' },
        { url: window.SETTINGS.urls.city_layer, name: tr("Cities"), id: 'city' },
        { url: window.SETTINGS.urls.vigilancearea_layer, name: tr("Vigilance areas"), id: 'vigilancearea' }
    ];

    landLayers = landLayers.concat(
        window.SETTINGS.map['restricted_area_types']
    );

    $.each(landLayers, function (i, landLayer) {
        landLayer.isActive = false;

        var style = L.Util.extend(
            { clickable: true },
            window.SETTINGS.map.styles[landLayer.id] || {}
        );
        var colorspools = L.Util.extend(
            {},
            window.SETTINGS.map.colorspool
        );
        var colorspool = colorspools[landLayer.id];

        if (colorspool) {
            var color = colorspool[(i < 2 ? i : i - 2) % colorspool.length];
            style['color'] = color;
        }

        var layer = new L.ObjectsLayer(null, {
            indexing: false,
            modelname: landLayer.id,
            style: style,
        });

        if (data.modelname != landLayer.id) {
            var nameHTML = '<span style="color: ' +
                style['color'] +
                ';">&#x2B24;</span>&nbsp;' +
                landLayer.name;

            map.layerscontrol.addOverlay(
                layer,
                nameHTML,
                tr('Zoning')
            );
        }

        map.on('layeradd', function (e) {

            var options = e.layer.options || {
                'modelname': 'None'
            };

            if (!landLayer.isActive) {

                if (
                    options.modelname == landLayer.id &&
                    options.modelname != data.modelname
                ) {
                    e.layer.load(landLayer.url);
                    landLayer.isActive = true;
                }
            }
        });
    });
});