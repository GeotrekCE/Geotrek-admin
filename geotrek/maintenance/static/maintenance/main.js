//
// Maintenance / interventions
//

$(window).on('entity:map', function (e, data) {
    var modelname = 'intervention';
    var layername = `${modelname}_layer`;
	var url = window.SETTINGS.urls[layername];
    var loaded_infrastructure = false;
    var map = data.map;

    // Show infrastructure layer in application maps
    var style = L.Util.extend({ clickable: false },
        window.SETTINGS.map.styles[modelname] || {});

    var layer = new L.ObjectsLayer(null, {
        modelname: modelname,
        style: style,
    });

    if (data.modelname != modelname){
	    map.layerscontrol.addOverlay(layer, tr('Intervention'), tr('Maintenance'));
    };

    map.on('layeradd', function (e) {
        var options = e.layer.options || { 'modelname': 'None' };
        if (! loaded_infrastructure) {
            if (options.modelname == modelname && options.modelname != data.modelname) {
                e.layer.load(url);
                loaded_infrastructure = true;
            }
        }
    });
});


// Date picker with placeholder on input
function setDatePickerConfig(idList) {
    $(idList).datepicker({
        autoclose: true,
        language: window.SETTINGS.languages.default,
        format: window.SETTINGS.date_format
    });
}
$(window).on('entity:view:add', function (e, data) {
    if (data.modelname === "intervention"){
        setDatePickerConfig('#id_begin_date, #id_end_date');
    };
});

$(window).on('entity:view:filter', function (e, data) {
    if (data.modelname === "intervention"){
        setDatePickerConfig('#id_begin_date_0, #id_begin_date_1, #id_end_date_0, #id_end_date_1');
    };
});

$(window).on('entity:view:update', function (e, data) {
    if (data.modelname === "intervention"){
        setDatePickerConfig('#id_begin_date, #id_end_date');
    };
});
