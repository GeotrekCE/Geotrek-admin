$(document).ready(function() {
    // Uncheck review when published
    $('#id_review').click(function() {
        if ($(this).is(':checked'))
            $('[id^=id_published_]').prop('checked', false);
    });
    // Uncheck published when review
    $('[id^=id_published_]').click(function() {
        if ($(this).is(':checked'))
            $('#id_review').prop('checked', false);
    });
});
