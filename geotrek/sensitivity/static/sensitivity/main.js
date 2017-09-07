//
// Sensitive areas
//

$(window).on('entity:view:list', function (e, data) {

    // Tooltips on categories in list view
    if (data.modelname != 'sensitivearea')
        return;
    $('.categories-filter a').tooltip();

    var $addButton = $("#list-panel .btn-toolbar .btn.btn-success").first();
    var addUrl = $addButton.attr('href');

    // Refresh list filter when click on a category button
    $('.categories-filter a').click(function () {
        var $this = $(this);

        // Show current in orange
        $('.categories-filter a').removeClass('btn-warning');
        $this.addClass('btn-warning');

        var category = $this.data('category');
        if (category) {
            // Category chosen
            $('select#id_category').val(category)
                                   .addClass('filter-set');
            $addButton.attr('href', addUrl + '?category=' + category);
        }
        else {
            // All chosen.
            $("select#id_category option").prop("selected", false);
            $('select#id_category').removeClass('filter-set');
            $addButton.attr('href', addUrl);
        }

        // Simulate form submission
        $('#mainfilter a#filter').click();
    });
});
