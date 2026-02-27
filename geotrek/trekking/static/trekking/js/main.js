
$(window).on('entity:view:add entity:view:update', function (e, data) {
    if (data.modelname == 'trek') {

        // Refresh trek cotations by practice on site change
        $('#id_practice').change(function () {
            update_trek_cotations();
        });
        $('#id_practice').trigger('change');
    }
    return;
});


function update_cotations(category) {
    // For each scale rating
    var scales = JSON.parse($('#all-ratings-scales').text());
    for (var scale_id in scales) {
        // Hide form field if scale not in list for this category
        $('#div_id_rating_scale_' + scale_id).prop('hidden', !(scale_id in category['scales']));
        if (!(scale_id in category['scales'])) {
            $('#id_rating_scale_' + scale_id).val('').trigger("chosen:updated");
        }
        $('#id_rating_scale_' + scale_id + '_chosen').width('100%');
    }
}

function hide_all_cotations() {
    // For each scale rating
    var scales = JSON.parse($('#all-ratings-scales').text());
    for (var scale_id in scales) {
        // Hide form fields
        $('#div_id_rating_scale_' + scale_id).prop('hidden', true);
    }
}

function update_trek_cotations() {
    var practices = JSON.parse($('#practices').text());
    var practice = $('#id_practice').val();

    var types = practice ? practices[practice]['types'] : {};

    // Refresh cotation selectors
    if (practice == "") {
        hide_all_cotations();
    } else {
        update_cotations(practices[practice]);
    }
}
