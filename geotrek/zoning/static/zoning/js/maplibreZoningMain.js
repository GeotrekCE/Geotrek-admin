window.addEventListener('entity:map', () => {
    const map = window.MapEntity.currentMap.map;
    const colorspools = window.SETTINGS.map.colorspool || {};

    // Regroupement des couches de terrain (districts, villes + zones restreintes)
    let landLayers = [
        { url: window.SETTINGS.urls.district_layer, name: gettext("Districts"), id: 'district' },
        { url: window.SETTINGS.urls.city_layer, name: gettext("Cities"), id: 'city' },
        ...window.SETTINGS.map['restricted_area_types']
    ].map((layer, index) => {
        layer.isActive = false;
        return layer;
    });

    landLayers.forEach((landLayer, i) => {
        const style = window.SETTINGS.map.styles[landLayer.id] ?? window.SETTINGS.map.styles['autres'];
        // Couleur personnalisée par colorspool
        const pool = colorspools[landLayer.id];
        if (pool) {
            const color = pool[(i < 2 ? i : i - 2) % pool.length];
            style.color = color;
        }

        const nameHTML = `<span style="color: ${style.color};">&#x2B24;</span>&nbsp;${landLayer.name}`;
        const category = tr('Zoning');
        let primaryKey = generateUniqueId();

        const layer = new MaplibreObjectsLayer(null, {
            modelname: landLayer.name,
            style: style,
            readonly: true,
            nameHTML: nameHTML,
            category: category,
            primaryKey: primaryKey,
            dataUrl: landLayer.url,
            isLazy: true
        });

        layer.initialize(map.getMap());
        layer.registerLazyLayer(landLayer.name, category, nameHTML, primaryKey, landLayer.url);

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