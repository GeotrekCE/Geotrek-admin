//
// Datasources
//

$(window).on('entity:map', function (e, data) {

    var map = data.map;

    var template = $('#tourism-popup-template').html();

    function locationMarker(source, feature, latlng) {
        var html = L.Util.template('<img width="16" src="{pictogram_url}"/>',
                                   source);

        var icon = L.divIcon({html: html,
                              className: 'tourism-datasource-marker',
                              iconSize: [16, 0]});
        var marker = L.marker(latlng, {icon: icon});

        marker.on('click', function (e) {
            var props = L.Util.extend({title:'', description:'', website: ''},
                                      feature.properties);
                content = L.Util.template(template, props);

            marker.bindPopup(content)
                  .openPopup();
        });
        return marker;
    }

    function locationMarkerFunc(ds) {
        return function (feature, latlng) {
            return locationMarker(ds, feature, latlng);
        };
    }

    $.getJSON(window.SETTINGS.urls.tourism_datasources, function (datasources) {
        for (var i=0; i<datasources.length; i++) {
            var dataSource = datasources[i],
                pointToLayerFunc = locationMarkerFunc(dataSource);

            var is_visible = (!dataSource.targets || dataSource.targets.indexOf(data.appname) > -1);
            if (!is_visible)
                continue;

            var layer = new L.ObjectsLayer(null, {
                indexing: false,
                pointToLayer: pointToLayerFunc
            });
            layer.load(dataSource.geojson_url);
            var nameHTML = '<img style="background-color: lightgray" width="16" src="' + dataSource.pictogram_url + '"/>&nbsp;' + dataSource.title;
            map.layerscontrol.addOverlay(layer, nameHTML, tr('Data sources'));
        }
    });
});


//
// Touristic Content
//

$(window).on('entity:view:add entity:view:update', function (e, data) {

    // Chosen on themes etc...
    $('select[multiple]').chosen({
        no_results_text: tr("No result"),
        placeholder_text_multiple: tr("Choose value(s)")
    });

    if (data.modelname != 'touristiccontent')
        return;

    $('#id_category').change(function() {
        update_types('1');
        update_types('2');
    });
    $('#id_category').trigger('change');


    function update_types(n) {
        var categories = JSON.parse($('#categories-types').text());
        var category = $('#id_category').val();
        var $select = $('#id_type' + n);
        var selected = $select.val() || [];

        var types_values = category ? categories[category]['type' + n + '_values'] : {};
        var type_label = category ? categories[category]['type' + n + '_label'] : '';

        // Refresh type label
        if (type_label)
            $('label[for=id_type' + n + ']').text(type_label);

        // Hide type field if no values for this category
        $('#div_id_type' + n).toggle(Object.keys(types_values).length > 0);

        // Refresh options list for types, depending on category
        $select.empty();
        for(var type_id in types_values) {
            var type_name = types_values[type_id];
            $('<option/>')
                .text(type_name)
                .attr('value', type_id)
                .prop('selected', selected.indexOf(type_id) >= 0)
                .appendTo($select);
        }
        $select.trigger('chosen:updated');
    }
});
