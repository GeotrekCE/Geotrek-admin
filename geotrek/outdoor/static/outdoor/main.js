$(window).on('entity:map', function (e, data) {

    var map = data.map;
    var loaded_site = false;
    var loaded_course = false;
    // Show outdoor layers in application maps
    $.each(['site', 'course'], function (i, modelname) {
        var layer = new L.ObjectsLayer(null, {
            modelname: modelname,
            style: L.Util.extend(window.SETTINGS.map.styles[modelname] || {}, {clickable:false}),
        });
        if (data.modelname != modelname) {
            map.layerscontrol.addOverlay(layer, tr(modelname), tr('Outdoor'));
        };
        map.on('layeradd', function(e) {
            var options = e.layer.options || {'modelname': 'None'};
            if (! loaded_site) {
                if (options.modelname == 'site' && options.modelname != data.modelname) {
                    e.layer.load(window.SETTINGS.urls.site_layer);
                    loaded_site = true;
                }
            }
            if (! loaded_course) {
                if (options.modelname == 'course' && options.modelname != data.modelname) {
                    e.layer.load(window.SETTINGS.urls.course_layer);
                    loaded_course = true;
                }
            }
    	});
    });
});


$(window).on('entity:view:add entity:view:update', function (e, data) {
    if (data.modelname != 'site')
        return;

    // Refresh types by practice
    $('#id_practice').change(function() {
        update_site_types();
    });
    $('#id_practice').trigger('change');
});


function update_site_types() {
    var practices = JSON.parse($('#practices-types').text());
    var practice = $('#id_practice').val();
    var $select = $('#id_type');
    var selected = $select.val() || [];

    var types = practice ? practices[practice]['types'] : {};

    // Hide type field if no values for this practice
    $('#div_id_type').toggle(Object.keys(types).length > 0);

    // Refresh options list for types, depending on practice
    $select.empty();
    $('<option/>')
        .text('---------')
        .attr('value', '')
        .appendTo($select);
    for(var type_id in types) {
        var type_name = types[type_id];
        $('<option/>')
            .text(type_name)
            .attr('value', type_id)
            .prop('selected', selected.indexOf(type_id) >= 0)
            .appendTo($select);
    }
    $select.trigger('chosen:updated');
}
