$(window).on('entity:view:add entity:view:update', function (e, data) {
    $('#div_id_message_sentinel').prop('hidden', true);
    $('#div_id_message_administrators').prop('hidden', true);
    $('#div_id_message_sentinel_predefined').prop('hidden', true);
    $('#div_id_message_supervisor').prop('hidden', true);
    $('#div_id_uses_timers').prop('hidden', true);
    $('#id_status').change(function () {
        display_message_fields_on_status_change();
    });
    $('#id_current_user').change(function () {
        display_message_fields_on_supervisor_change();
    });
    $('#div_id_message_sentinel_predefined').change(function () {
        display_predefined_email_in_email_field();
    });
    return;
});

function display_message_fields_on_status_change() {
    var status_ids_and_colors = JSON.parse($('#status_ids_and_colors').text());
    var workflow_manager = JSON.parse($('#workflow_manager').text());
    var selected = $('#id_status').val() || null;
    do_display = ((status_ids_and_colors[selected]['id'] == "solved") || (status_ids_and_colors[selected]['id'] == "classified") || (status_ids_and_colors[selected]['id'] == "waiting"))
    $('#div_id_message_sentinel').prop('hidden', !do_display);
    $('#div_id_message_administrators').prop('hidden', !do_display);
    $('#div_id_message_sentinel_predefined').prop('hidden', !do_display);
    do_display_timer = (status_ids_and_colors[selected]['id'] == "waiting")
    $('#div_id_uses_timers').prop('hidden', !do_display_timer);
    // Prevent assigning and classifying at the same time - or rejecting and assigning
    if ((status_ids_and_colors[selected]['id'] == "classified") || (status_ids_and_colors[selected]['id'] == "rejected")) {
        $('#id_current_user').val(workflow_manager);
        $('#div_id_current_user').prop('hidden', true);
        $('#div_id_message_supervisor').prop('hidden', true);
        $('#div_id_uses_timers').prop('hidden', true);
    }
    if (status_ids_and_colors[selected]['id'] == "filed") {
        $('#id_current_user').val(workflow_manager);
        $('#div_id_current_user').prop('hidden', false);
    }
}

function display_message_fields_on_supervisor_change() {
    var selected = $('#id_current_user').val() || null;
    var workflow_manager = JSON.parse($('#workflow_manager').text());
    $('#div_id_message_sentinel').prop('hidden', (selected == workflow_manager));
    $('#div_id_message_administrators').prop('hidden', (selected == workflow_manager));
    $('#div_id_message_sentinel_predefined').prop('hidden', (selected == workflow_manager));
    $('#div_id_message_supervisor').prop('hidden', (selected == workflow_manager));
    $('#div_id_uses_timers').prop('hidden', (selected == workflow_manager));
    $('#div_id_status').prop('hidden', (selected != workflow_manager));
    if (selected == workflow_manager) {
        $('#id_message_supervisor').val("");
        $('#id_message_sentinel').val("");
        $('#id_message_administrators').val("");
    }
}

function display_predefined_email_in_email_field() {
    var predefined_emails = JSON.parse($('#predefined_emails').text());
    var resolved_intervention_info = JSON.parse($('#resolved_intervention_info').text());
    var selected = $('#id_message_sentinel_predefined').val() || null;
    if (selected == null) {
        $('#id_message_sentinel').val("");
        $('#id_message_administrators').val("");
    } else {
        text = predefined_emails[selected]["text"];
        text = text.replace(/##supervisor##/g, resolved_intervention_info["username"]);
        text = text.replace(/##intervention_end_date##/g, resolved_intervention_info["end_date"]);
        $('#id_message_sentinel').val(text);
        $('#id_message_administrators').val(text);
    }
}
