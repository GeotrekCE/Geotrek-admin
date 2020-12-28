$(window).on('entity:view:list', function (e, data) {
    /*
     * Datatables
     * .......................
     */
    MapEntity.mainDatatable = JQDataTable.init($('#objects-list'), null /* no load at startup */, {
        // Hide pk column
        aoColumnDefs: [ { "bVisible": false, "aTargets": [ 0 ] } ],
        sDom: "tpf",
        aaData: [],
        iDeferLoading: 0,
        iDisplayLength: 15,  // TODO: this is VERY ANNOYING ! I want to fill height !
        // Enable cache
        fnServerData: function ( sUrl, aoData, fnCallback, oSettings ) {
			oSettings.jqXHR = $.ajax( {
				"url":  sUrl,
				"data": aoData,
				"success": function (json) {
					$(oSettings.oInstance).trigger('xhr', oSettings);
					fnCallback( json );
				},
				"dataType": "json",
				"cache": true,
				"type": oSettings.sServerMethod,
				"error": function (xhr, error, thrown) {
					if ( error == "parsererror" ) {
						oSettings.oApi._fnLog( oSettings, 0, "DataTables warning: JSON data from "+
							"server could not be parsed. This is caused by a JSON formatting error." );
					}
				}
			} );
		}
    });

    // Adjust vertically
    expandDatatableHeight(MapEntity.mainDatatable);
    $(window).resize(function (e) {
        expandDatatableHeight(MapEntity.mainDatatable);
    });


    // Show tooltips on left menu
    $('#entitylist .nav-link').tooltip({ placement: 'right', boundary: 'window' });

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
    $('#objects-list_filter input').attr('placeHolder', tr("Search")).addClass('form-control');
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
