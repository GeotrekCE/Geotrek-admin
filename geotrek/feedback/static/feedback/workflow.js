$(window).on('entity:view:add entity:view:update', function (e, data) {
    $('#div_id_current_user').prop('hidden', true);
    $('#div_id_message_sentinel').prop('hidden', true);
    $('#div_id_message_administrators').prop('hidden', true);
    $('#div_id_message_sentinel_predefined').prop('hidden', true);
    $('#div_id_message_supervisor').prop('hidden', true);
    $('#div_id_uses_timers').prop('hidden', true);
    $('#id_status').change(function () {
        display_message_fields_on_status_change();
    });
    $('#id_message_sentinel_predefined').change(function () {
        display_predefined_email_in_email_field();
    });
    return;
});

function display_message_fields_on_status_change() {
    var status_ids_and_colors = JSON.parse($('#status_ids_and_colors').text());
    var workflow_manager = JSON.parse($('#workflow_manager').text());
    var selected = $('#id_status').val() || null;

    let status_is_classified = (status_ids_and_colors[selected]['id'] === "classified");
    let status_is_waiting = (status_ids_and_colors[selected]['id'] === "waiting");
    let status_is_solved = (status_ids_and_colors[selected]['id'] === "solved");
    let status_is_rejected = (status_ids_and_colors[selected]['id'] === "rejected");

    $('#div_id_message_sentinel_predefined').prop('hidden', !(status_is_classified || status_is_waiting || status_is_solved));
    $('#div_id_message_sentinel').prop('hidden', !(status_is_classified || status_is_waiting || status_is_solved));
    $('#div_id_message_administrators').prop('hidden', !(status_is_classified || status_is_waiting || status_is_solved));
    $('#div_id_current_user').prop('hidden', !(status_is_waiting || status_is_solved));
    $('#div_id_message_supervisor').prop('hidden', !(status_is_waiting));
    $('#div_id_uses_timers').prop('hidden', !(status_is_waiting));

    if (status_is_waiting || status_is_classified || status_is_rejected) {
        $('#id_current_user').val(workflow_manager);
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