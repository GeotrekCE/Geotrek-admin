$(window).on('entity:map', function (e, data) {

    var map = data.map;

    var landLayers = [
        { url: window.SETTINGS.urls.district_layer, name: tr("Districts"), id: 'district' },
        { url: window.SETTINGS.urls.city_layer, name: tr("Cities"), id: 'city' },
        { url: window.SETTINGS.urls.vigilancearea_layer, name: tr("Vigilance areas"), id: 'vigilancearea', clickable: true }
    ];

    landLayers = landLayers.concat(
        window.SETTINGS.map['restricted_area_types']
    );

    $.each(landLayers, function (i, landLayer) {
        landLayer.isActive = false;

        var style = L.Util.extend(
            {clickable: landLayer.clickable ?? false},
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
        var modelname = landLayer.id;
        if (modelname === "restrictedarea") {
            modelname = landLayer.name
        }

        var layer = new L.ObjectsLayer(null, {
            indexing: false,
            modelname: modelname,
            style: style,
        });

        if (data.modelname != modelname) {
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
                var landLayerModelname = landLayer.id;
                if (landLayerModelname === "restrictedarea") {
                    landLayerModelname = landLayer.name
                }

                if (
                    options.modelname == landLayerModelname &&
                    options.modelname != data.modelname
                ) {
                    e.layer.load(landLayer.url);
                    landLayer.isActive = true;
                }
            }
        });
    });
});