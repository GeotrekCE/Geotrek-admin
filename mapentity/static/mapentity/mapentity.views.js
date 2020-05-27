$(window).on('entity:view:list', function (e, data) {
    /*
     * Datatables
     * .......................
     */
    MapEntity.mainDatatable = JQDataTable.init(
        $('#objects-list'),
        $('#mainfilter').attr("action"),
        {
            // Hide pk column
            aoColumnDefs: [ { "bVisible": false, "aTargets": [ 0 ] } ],
            aaData: [],
            iDeferLoading: 0,
            iDisplayLength: 15,  // This height is override by the expandDatatableHeight method in mapentity.helpers.js
            bLengthChange: false,
            bInfo: false,
        }
    );

    // Adjust vertically
    expandDatatableHeight(MapEntity.mainDatatable);
    $(window).resize(function (e) {
        expandDatatableHeight(MapEntity.mainDatatable);
    });


    // Show tooltips on left menu
    $('#entitylist a').tooltip({'placement': 'right'});

    // Trigger a call to the format url
    $('#list-download-toolbar button').on('click', function () {
        var can_export = $('#list-download-toolbar .btn-group.disabled').length === 0;
        var format = $(this).attr('name');

        var format_url = window.SETTINGS.urls.format_list.replace(new RegExp('modelname', 'g'), data.modelname);
        var url = format_url + '?' +
                  $('#mainfilter').serialize() + '&format=' + format;

        if (can_export)
            document.location = url;

        return false;
    });

    // Hardcore Datatables customizations
    $('li.next a').html($('li.next a').html().replace('Next', ''));
    $('li.prev a').html($('li.prev a').html().replace('Previous', ''));
    $('#objects-list_filter input').attr('placeHolder', tr("Search"));
    $('#objects-list_filter label').contents().filter(function() {return this.nodeType === 3;/*Node.TEXT_NODE*/}).remove();

});


$(window).on('entity:view:detail', function (e, data) {
    //
    // Throw event when record is hovered
    // (used in Leaflet.ObjectLayer and below)
    $('.hoverable').hoverIntent(
        function on() {
            var modelname = $(this).data('modelname');
            var pk = $(this).data('pk');
            $(window).trigger('entity:mouseover', {pk: pk, modelname: modelname});
        },
        function off() {
            var modelname = $(this).data('modelname');
            var pk = $(this).data('pk');
            $(window).trigger('entity:mouseout', {pk: pk, modelname: modelname});
        }
    );

    //
    // Highlight (e.g. table rows) when record is hovered
    $(window).on('entity:mouseover', function (e, data) {
        var modelname = data.modelname;
        var pk = data.pk;
        var $item = $("[data-modelname='" + modelname + "'][data-pk='" + pk + "']");
        $item.addClass('hover');
    });
    $(window).on('entity:mouseout', function (e, data) {
        var modelname = data.modelname;
        var pk = data.pk;
        var $item = $("[data-modelname='" + modelname + "'][data-pk='" + pk + "']");
        $item.removeClass('hover');
    });
});
