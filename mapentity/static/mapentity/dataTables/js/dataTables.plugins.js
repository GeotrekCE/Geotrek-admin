$.fn.dataTableExt.oApi.fnGetHiddenNodes = function ( oSettings )
{
    /* Note the use of a DataTables 'private' function thought the 'oApi' object */
    var anNodes = this.oApi._fnGetTrNodes( oSettings );
    var anDisplay = $('tbody tr', oSettings.nTable);
      
    /* Remove nodes which are being displayed */
    for ( var i=0 ; i<anDisplay.length ; i++ )
    {
        var iIndex = jQuery.inArray( anDisplay[i], anNodes );
        if ( iIndex != -1 )
        {
            anNodes.splice( iIndex, 1 );
        }
    }
      
    /* Fire back the array to the caller */
    return anNodes;
};



jQuery.fn.dataTableExt.oApi.fnGetColumnData = function ( oSettings, iColumn, bUnique, bFiltered, bIgnoreEmpty ) {
    // check that we have a column id
    if ( typeof iColumn == "undefined" ) return [];
      
    // by default we only wany unique data
    if ( typeof bUnique == "undefined" ) bUnique = true;
      
    // by default we do want to only look at filtered data
    if ( typeof bFiltered == "undefined" ) bFiltered = true;
      
    // by default we do not wany to include empty values
    if ( typeof bIgnoreEmpty == "undefined" ) bIgnoreEmpty = true;
      
    // list of rows which we're going to loop through
    var aiRows;
      
    // use only filtered rows
    if (bFiltered == true) aiRows = oSettings.aiDisplay;
    // use all rows
    else aiRows = oSettings.aiDisplayMaster; // all row numbers
  
    // set up data array   
    var asResultData = new Array();
      
    for (var i=0,c=aiRows.length; i<c; i++) {
        iRow = aiRows[i];
        var sValue = this.fnGetData(iRow, iColumn);
          
        // ignore empty values?
        if (bIgnoreEmpty == true && sValue.length == 0) continue;
  
        // ignore unique values?
        else if (bUnique == true && jQuery.inArray(sValue, asResultData) > -1) continue;
          
        // else push the value onto the result data array
        else asResultData.push(sValue);
    }
      
    return asResultData;
};


$.fn.dataTableExt.oApi.fnReloadAjax = function ( oSettings, sNewSource, sAjaxDataPropWithCbArg, fnCallback, bStandingRedraw )
{
    if ( typeof sNewSource != 'undefined' && sNewSource != null )
    {
        oSettings.sAjaxSource = sNewSource;
    }
    this.oApi._fnProcessingDisplay( oSettings, true );
    var that = this;
    var iStart = oSettings._iDisplayStart;
    var aData = [];

    this.oApi._fnServerParams( oSettings, aData );

    oSettings.fnServerData( oSettings.sAjaxSource, aData, function(json) {
        /* Clear the old information from the table */
        that.oApi._fnClearTable( oSettings );

        /* Got the data - add it to the table */
        var callback_args = {};
        var getObjectDataFn = null;

        if (sAjaxDataPropWithCbArg !== undefined) {
            getObjectDataFn = function(data, type) {
                return sAjaxDataPropWithCbArg(data, type, callback_args);
            };
        } else if (oSettings.sAjaxDataProp !== "") {
            getObjectDataFn = oSettings.sAjaxDataProp;
        }

        var aData = getObjectDataFn ? that.oApi._fnGetObjectDataFn(getObjectDataFn)( json ) : json;

        for ( var i=0 ; i<aData.length ; i++ )
        {
            that.oApi._fnAddData( oSettings, aData[i] );
        }

        oSettings.aiDisplay = oSettings.aiDisplayMaster.slice();
        that.fnDraw();

        if ( typeof bStandingRedraw != 'undefined' && bStandingRedraw === true )
        {
            oSettings._iDisplayStart = iStart;
            that.fnDraw( false );
        }

        that.oApi._fnProcessingDisplay( oSettings, false );

        /* Callback user function - for event handlers etc */
        if ( typeof fnCallback == 'function' && fnCallback != null )
        {
            fnCallback( oSettings, callback_args );
        }
    }, oSettings );
};
