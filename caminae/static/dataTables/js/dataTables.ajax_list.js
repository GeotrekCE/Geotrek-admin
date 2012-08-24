
var JQDataTable = {};

JQDataTable.init = function($elem, url, options) {
    JQDataTable.apply_patch();

    var default_options = {
            "sDom": "<'row'<'span6'l><'span6'f>r>t<'row'<'span6'i><'span6'p>>",
            "sPaginationType": "bootstrap",
            "oLanguage": {
              "sLengthMenu": "_MENU_ records per page"
            },
            "bProcessing": false,
            "bServerSide": false,
            "sAjaxSource": url
    };

    return $elem.dataTable($.extend(default_options, options));
};

JQDataTable.patched = false;


// Iterate on all visible rows looking for the matching row using is_found.
// Call cb_found or cb_not_found appropriately
// cb_found(row: jquery elem, pagination: boolean, settings)
JQDataTable.goToPage = function(dtable, is_found, cb_found, cb_not_found) {
    var dt_settings = dtable.fnSettings();
    var pagingInfo = dt_settings.oInstance.fnPagingInfo()

    var aiRows = dt_settings.aiDisplay;
    for (var position = 0, c = aiRows.length; position < c; position++) {
        var iRow = aiRows[position];
        if(is_found(dtable.fnGetData(iRow))) {
            var page_idx = Math.floor(position / pagingInfo.iLength);

            // If the page is the current one, call immediatly the callback
            if (page_idx == pagingInfo.iTabIndex) {
                cb($(dtable.fnGetNodes(iRow)), false, oSettings);
            } else {
                dt_settings._iDisplayStart =  page_idx * pagingInfo.iLength;

                if (cb_found) {
                    // There is currently no api to unregister cleanly a callback
                    // (but it's just an array...).
                    // Just ensure this gets called only once..
                    var first = true;
                    dt_settings.oApi._fnCallbackReg(dt_settings, 'aoDrawCallback',
                        function(oSettings) {
                            if(first) {
                                first = false;
                                cb_found($(dtable.fnGetNodes(iRow)), true, oSettings);
                            }
                        },
                        'customGoToPageCb' + new Date().getTime() // ~random unique name
                    );
                }

                dtable.oApi._fnCalculateEnd(dt_settings);
                dtable.oApi._fnDraw(dt_settings);
            }

            // found, return !
            return;
        }
        cb_not_found && cb_not_found();
    }
};





// Set up a bootstrap configuration for jqDataTable
// taken from: http://datatables.net/blog/Twitter_Bootstrap_2
JQDataTable.apply_patch = function() {
    if ( JQDataTable.patched )
        return;
    else
        JQDataTable.patched = true;

    /* Default class modification */
    $.extend($.fn.dataTableExt.oStdClasses, {
      "sWrapper": "dataTables_wrapper form-inline"
    }); /* API method to get paging information */
    $.fn.dataTableExt.oApi.fnPagingInfo = function (oSettings) {
      return {
        "iStart": oSettings._iDisplayStart,
        "iEnd": oSettings.fnDisplayEnd(),
        "iLength": oSettings._iDisplayLength,
        "iTotal": oSettings.fnRecordsTotal(),
        "iFilteredTotal": oSettings.fnRecordsDisplay(),
        "iPage": Math.ceil(oSettings._iDisplayStart / oSettings._iDisplayLength),
        "iTotalPages": Math.ceil(oSettings.fnRecordsDisplay() / oSettings._iDisplayLength)
      };
    } /* Bootstrap style pagination control */
    $.extend($.fn.dataTableExt.oPagination, {
      "bootstrap": {
        "fnInit": function (oSettings, nPaging, fnDraw) {
          var oLang = oSettings.oLanguage.oPaginate;
          var fnClickHandler = function (e) {
              e.preventDefault();
              if (oSettings.oApi._fnPageChange(oSettings, e.data.action)) {
                fnDraw(oSettings);
              }
            };
          $(nPaging).addClass('pagination').append('<ul>' + '<li class="prev disabled"><a href="#">&larr; ' + oLang.sPrevious + '</a></li>' + '<li class="next disabled"><a href="#">' + oLang.sNext + ' &rarr; </a></li>' + '</ul>');
          var els = $('a', nPaging);
          $(els[0]).bind('click.DT', {
            action: "previous"
          }, fnClickHandler);
          $(els[1]).bind('click.DT', {
            action: "next"
          }, fnClickHandler);
        },
        "fnUpdate": function (oSettings, fnDraw) {
          var iListLength = 5;
          var oPaging = oSettings.oInstance.fnPagingInfo();
          var an = oSettings.aanFeatures.p;
          var i, j, sClass, iStart, iEnd, iHalf = Math.floor(iListLength / 2);
          if (oPaging.iTotalPages < iListLength) {
            iStart = 1;
            iEnd = oPaging.iTotalPages;
          } else if (oPaging.iPage <= iHalf) {
            iStart = 1;
            iEnd = iListLength;
          } else if (oPaging.iPage >= (oPaging.iTotalPages - iHalf)) {
            iStart = oPaging.iTotalPages - iListLength + 1;
            iEnd = oPaging.iTotalPages;
          } else {
            iStart = oPaging.iPage - iHalf + 1;
            iEnd = iStart + iListLength - 1;
          }
          for (i = 0, iLen = an.length; i < iLen; i++) {
            // Remove the middle elements
            $('li:gt(0)', an[i]).filter(':not(:last)').remove();
            // Add the new list items and their event handlers
            for (j = iStart; j <= iEnd; j++) {
              sClass = (j == oPaging.iPage + 1) ? 'class="active"' : '';
              $('<li ' + sClass + '><a href="#">' + j + '</a></li>').insertBefore($('li:last', an[i])[0]).bind('click', function (e) {
                e.preventDefault();
                oSettings._iDisplayStart = (parseInt($('a', this).text(), 10) - 1) * oPaging.iLength;
                fnDraw(oSettings);
              });
            }
            // Add / remove disabled classes from the static elements
            if (oPaging.iPage === 0) {
              $('li:first', an[i]).addClass('disabled');
            } else {
              $('li:first', an[i]).removeClass('disabled');
            }
            if (oPaging.iPage === oPaging.iTotalPages - 1 || oPaging.iTotalPages === 0) {
              $('li:last', an[i]).addClass('disabled');
            } else {
              $('li:last', an[i]).removeClass('disabled');
            }
          }
        }
      }
    }); /* Table initialisation */
};
