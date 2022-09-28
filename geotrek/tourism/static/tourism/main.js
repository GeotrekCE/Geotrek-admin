//
// Touristic Content
//

$(window).on('entity:map', function (e, data) {

    var map = data.map;
    var loaded_event = false;
    var loaded_touristic = false;
    // Show tourism layer in application maps
    $.each(['touristiccontent', 'touristicevent'], function (i, modelname) {
        var layer = new L.ObjectsLayer(null, {
            modelname: modelname,
            style: L.Util.extend(window.SETTINGS.map.styles[modelname] || {}, {clickable:false}),
        });
        if (data.modelname != modelname){
            map.layerscontrol.addOverlay(layer, tr(modelname), tr('Tourism'));
        };
        map.on('layeradd', function(e){
            var options = e.layer.options || {'modelname': 'None'};
            if (! loaded_event){
                if (options.modelname == 'touristicevent' && options.modelname != data.modelname){
                    e.layer.load(window.SETTINGS.urls.touristicevent_layer);
                    loaded_event = true;
                }
            }
            if (! loaded_touristic){
                if (options.modelname == 'touristiccontent' && options.modelname != data.modelname){
                    e.layer.load(window.SETTINGS.urls.touristiccontent_layer);
                    loaded_touristic = true;
                }
        }
    });
    });
});


$(window).on('entity:view:list', function (e, data) {

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
        $('#div_id_participant_number').prop("hidden", !$('#id_bookable').is(":checked"));
        $('#id_bookable').change(function() {
            $('#div_id_participant_number').prop("hidden", !this.checked);
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
