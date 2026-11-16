/*
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

function refresh_selector_with_areas($select, areas, selected) {
    $select.empty();
    for (var i in areas) {
        area_dict = areas[i]
        var area_id = Object.keys(area_dict)[0];
        var area_name = area_dict[area_id];
        $('<option/>')
            .text(area_name)
            .attr('value', area_id)
            .prop('selected', selected.indexOf(area_id) >= 0)
            .appendTo($select);
    }
    $select.trigger('chosen:updated');
}

$(window).on('entity:view:filter', function () {
    // Dynamic area filters
    $('#id_area_type').change(function () {
        // Parse area data
        var types = JSON.parse($('#restricted_areas_by_type').text());
        var all_restricted_areas = JSON.parse($('#all_restricted_areas').text());
        // Change forms dynamically on selection
        var area_types = $('#id_area_type').val();
        var selected_areas = {}
        if (area_types && area_types.length > 0) {
            // If area type(s) are selected, load corresponding areas from these type(s) in selector
            for (var i = 0; i < area_types.length; i++) {
                area_type = area_types[i]
                $.extend(selected_areas, types[area_type]['areas']);
            }
            var $select = $('#id_area');
            var selected = $select.val() || [];
            refresh_selector_with_areas($select, selected_areas, selected);
        } else {
            // If no area types are selected, load all possible areas in selector
            var $select = $('#id_area');
            var selected = $select.val() || [];
            refresh_selector_with_areas($select, all_restricted_areas, selected);
        }
    });
});
*/
