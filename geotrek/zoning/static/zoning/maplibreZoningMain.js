window.addEventListener('entity:map', (event) => {
    const { map } = event.detail;

    let landLayers = [
        { url: window.SETTINGS.urls.district_layer, name: tr("Districts"), id: 'district' },
        { url: window.SETTINGS.urls.city_layer, name: tr("Cities"), id: 'city' }
    ];

    landLayers = landLayers.concat(window.SETTINGS.map['restricted_area_types']);
    landLayers.map(function (el) {
        el.isActive = false;
        return el;
    })

    for (let i = 0; i < landLayers.length; i++) {
        const landLayer = landLayers[i];
        const style = window.SETTINGS.map.styles[landLayer.id] || {};
        const colorspools = window.SETTINGS.map.colorspool || {};
        const colorspool = colorspools[landLayer.id];
        if (colorspool) {
            const color = colorspool[(i < 2 ? i : i - 2) % colorspool.length];
            style['color'] = color;
        }
        // const layer = new MaplibreObjectsLayer(null, {
        //     indexing: false,
        //     modelname: landLayer.name,
        //     style: style,
        // });
        const nameHTML = `${landLayer.name}`;
        // map.layerscontrol.addOverlay(layer, nameHTML, tr('Zoning'));
    }

    // map.getMap().on('layeradd', (e) => {
    //     const options = e.layer.options || { 'modelname': 'None' };
    //     for (let i = 0; i < landLayers.length; i++) {
    //         if (!landLayers[i].isActive) {
    //             if (options.modelname === landLayers[i].name) {
    //                 e.layer.load(landLayers[i].url);
    //                 landLayers[i].isActive = true;
    //             }
    //         }
    //     }
    // });
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