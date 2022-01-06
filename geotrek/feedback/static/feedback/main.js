$(window).on('entity:view:add entity:view:update', function (e, data) {
    $('#div_id_message_sentinel').prop('hidden', true);
    $('#div_id_message_supervisor').prop('hidden', true);
    $('#div_id_uses_timers').prop('hidden', true);
    $('#id_status').change(function () {
        display_message_fields_on_status_change();
    });
    $('#id_assigned_user').change(function () {
        display_message_fields_on_supervisor_change();
    });
    return;
});

function display_message_fields_on_status_change() {
    var status_ids = JSON.parse($('#status_ids').text());
    var selected = $('#id_status').val() || null;
    do_display = ((status_ids[selected] == "resolved") || (status_ids[selected] == "classified"))
    $('#div_id_message_sentinel').prop('hidden', !do_display);
    // Prevent assigning and classifying at the same time
    if (status_ids[selected] == "classified") {
        $('#id_assigned_user').val("");
        $('#div_id_assigned_user').prop('hidden', true);
        $('#div_id_message_supervisor').prop('hidden', true);
        $('#div_id_uses_timers').prop('hidden', true);
    }
    if (status_ids[selected] == "filed") {
        $('#id_assigned_user').val("");
        $('#div_id_assigned_user').prop('hidden', false);
    }
}

function display_message_fields_on_supervisor_change() {
    var selected = $('#id_assigned_user').val() || null;
    $('#div_id_message_sentinel').prop('hidden', (selected == null));
    $('#div_id_message_supervisor').prop('hidden', (selected == null));
    $('#div_id_uses_timers').prop('hidden', (selected == null));
}

$(window).on('entity:map:list', function (e, data) {
    // Warning, bad code
    var map = data.map;
    map.on('layeradd', function (e) {
        console.log("dedans")
        layers = map._layers
        console.log(layers)
        // For each layer in map,
        // if this layer has a "color" key in its properties, then apply this color to the layer
        Object.keys(layers).forEach((index) => layers[index].properties && layers[index].properties.color && layers[index].setStyle({ color: layers[index].properties.color }))
    })
    // This is used to trigger the event,
    // because we can change colors only when everything was loaded on the map
    var fake_layer = new L.ObjectsLayer(null, {
        modelname: 'ignoreme',
    });
    map.addLayer(fake_layer) // We just need to trigger the event
    map.removeLayer(fake_layer) // We just need to trigger the event
});
