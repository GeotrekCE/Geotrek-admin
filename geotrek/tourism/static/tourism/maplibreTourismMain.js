window.addEventListener('entity:map', (event) => {
    const { map } = event.detail;

    ['touristiccontent', 'touristicevent'].forEach((modelname) => {
        const layername = `${modelname}_layer`;
        const layerUrl = window.SETTINGS.urls[layername];

        const style = {
            color: 'blue',
            weight: 2,
            opacity: 0.5,
            fillColor: '#FF0000',
            fillOpacity: 0.1
        };

        const nameHTML = tr(modelname);
        const category = tr('Tourism');

        // Show touristic content and events layers in application maps
        const objectsLayer = new MaplibreObjectsLayer(null, {
            style,
            modelname: modelname,
            readonly: false,
            nameHTML: nameHTML,
            category: category
        });

        objectsLayer.initialize(map.getMap());
        objectsLayer.load(layerUrl);
    });
});

// if (event.detail.modelname !== modelname) {
        //     map.layerscontrol.addOverlay(objectsLayer, tr(modelname.charAt(0).toUpperCase() + modelname.slice(1)), tr(modelname.charAt(0).toUpperCase() + modelname.slice(1)));
        // }

        // map.getMap().on('layeradd', (e) => {
        //     const options = e.layer.options || { 'modelname': 'None' };
        //     if (!loadedEvent && modelname === 'touristicevent') {
        //         if (options.modelname === modelname && options.modelname !== event.detail.modelname) {
        //             e.layer.load(layerUrl);
        //             loadedEvent = true;
        //         }
        //     } else if (!loadedTouristic && modelname === 'touristiccontent') {
        //         if (options.modelname === modelname && options.modelname !== event.detail.modelname) {
        //             e.layer.load(layerUrl);
        //             loadedTouristic = true;
        //         }
        //     }
        // });

$(window).on('entity:view:filter', function (e, data) {

    // Date picker
    $('#id_before, #id_after').datepicker({
        autoclose: true,
        language: window.SETTINGS.languages.default,
        format: window.SETTINGS.date_format
    });
    // prevent click on datepicker to close the filter popover
    $(document).on('click', '.datepicker, span.month, th.next, th.prev, th.datepicker-switch, span.year, td.day', function (e) {
        e.stopPropagation();
    });

    var $addButton = $("#list-panel .btn-toolbar .btn.btn-success").first();
    var addUrl = $addButton.attr('href');
});

$(window).on('entity:view:add entity:view:update', function (e, data) {
    // Date picker
    $('#id_begin_date, #id_end_date').datepicker({
        autoclose: true,
        language: window.SETTINGS.languages.default,
        format: window.SETTINGS.date_format
    });

    // Chosen on themes etc...
    $('select[multiple]').chosen({
        no_results_text: tr("No result"),
        placeholder_text_multiple: tr("Choose value(s)")
    });

    if(data.modelname == 'touristicevent') {
        $('#div_id_cancellation_reason').prop("hidden", !$('#id_cancelled').is(":checked"));
        $('#id_cancelled').change(function () {
            $('#div_id_cancellation_reason').prop("hidden", !this.checked);
        })
        $('#booking_widget').prop("hidden", !$('#id_bookable').is(":checked"));
        $('#id_bookable').change(function () {
            $('#booking_widget').prop("hidden", !this.checked);
        })
    }

    if (data.modelname != 'touristiccontent')
        return;

    // Refresh types by category
    $('#id_category').change(function() {
        update_touristiccontent_types('1');
        update_touristiccontent_types('2');

        // Hide geometry controls depending on category
        var categories = JSON.parse($('#categories-types').text());
        var category = $(this).val();
        var geometry_type = category ? categories[category]['geometry_type'] : 'any';
        if (geometry_type == 'any') {
            $('.leaflet-draw-toolbar a').show();
        }
        else {
            $('.leaflet-draw-toolbar-top a').hide();
            var controls = {'point': 'marker', 'line': 'polyline', 'polygon': 'polygon'};
            $('.leaflet-draw-toolbar a.leaflet-draw-draw-' + controls[geometry_type]).show();
        }
    });
    $('#id_category').trigger('change');
});

function update_touristiccontent_types(n) {
    var categories = JSON.parse($('#categories-types').text());
    var category = $('#id_category').val();
    var $select = $('#id_type' + n);
    var selected = $select.val() || [];

    var types_values = category ? categories[category]['type' + n + '_values'] : {};
    var type_label = category ? categories[category]['type' + n + '_label'] : '';

    // Refresh type label
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
