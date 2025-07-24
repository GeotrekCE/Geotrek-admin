//
// Maintenance / interventions
//
window.addEventListener("entity:map", () => {
    const map = window.MapEntity.currentMap.map;
    const modelname = 'intervention';
    const layername = 'intervention_layer';
    const layerUrl = window.SETTINGS.urls[layername];

    const style = {
        color: 'blue',
        weight: 2,
        opacity: 0.5,
        fillColor: '#FF0000',
        fillOpacity: 0.1
    };

    const nameHTML = tr('Intervention');
    const category = tr('Maintenance');
    const primaryKey = generateUniqueId();

    const objectsLayer = new MaplibreObjectsLayer(null, {
        style,
        modelname: modelname,
        readonly: true,
        nameHTML: nameHTML,
        category: category,
        primaryKey: primaryKey,
        dataUrl: layerUrl,
        isLazy: true
    });

    objectsLayer.initialize(map.getMap());
    objectsLayer.registerLazyLayer(modelname, category, nameHTML, primaryKey, layerUrl);
});

// Date picker with placeholder on input
function setDatePickerConfig(idList) {
    $(idList).datepicker({
        autoclose: true,
        language: window.SETTINGS.languages.default,
        format: window.SETTINGS.date_format
    });
}

document.addEventListener('entity:view:add', function (e, data) {
    console.log('entity:view:add', data);
    if (data.modelname === "intervention"){
        setDatePickerConfig('#id_begin_date, #id_end_date');
    };
});

document.addEventListener('entity:view:filter', function (e, data) {
    console.log('entity:view:filter', data);
    if (data.modelname === "intervention"){
        setDatePickerConfig('#id_begin_date_0, #id_begin_date_1, #id_end_date_0, #id_end_date_1');
    };
});

document.addEventListener('entity:view:update', function (e, data) {
    console.log('entity:view:update', data);
    if (data.modelname === "intervention"){
        setDatePickerConfig('#id_begin_date, #id_end_date');
    };
});