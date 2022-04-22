function getUrl(properties, layer) {
    return window.SETTINGS.urls.detail.replace(new RegExp('modelname', 'g'), data.modelname)
        .replace('0', properties.pk);
}

function bindHover() {
    // Maintain hovering over table hilights objects in map
    MapEntity.mainDatatable.rows().eq(0).each(function (index) {
        var row = MapEntity.mainDatatable.row(index);
        // Unbind MapEntity hover
        $(row.node()).unbind('mouseenter mouseleave');
        // Re-bind to highlight no matter which layer the object is in
        $(row.node()).hover(
            function () {
                window.objectsLayers.forEach(layer => {
                    layer.highlight(row.data().id);
                });
            },
            function () {
                window.objectsLayers.forEach(layer => {
                    layer.highlight(row.data().id, false);
                });
            }
        );
    });
}


function ChangeColors(e, data) {
    if (data.modelname != 'report')
        return;
    var map = data.map;
    var dt = MapEntity.mainDatatable;

    var objectsLayers = [];

    // For each report status
    var status_ids_and_colors = JSON.parse($('#status_ids_and_colors').text());
    for (var status in status_ids_and_colors) {
        status_id = status_ids_and_colors[status]["id"]
        status_color = status_ids_and_colors[status]["color"]
        // Use this status' color...
        L.Util.extend(
            window.SETTINGS.map.styles["report-" + status_id] = { 'weight': 5, 'color': status_color, 'opacity': 0.9, fillOpacity: 0.9 },
        );
        // ... in creating layer with reports that have this status
        var layer = new L.ObjectsLayer(null, {
            modelname: "report",
            objectUrl: getUrl,
            style: { color: status_color },
            onEachFeature: function (geojson, layer) {
                if (geojson.properties.name) layer.bindLabel(geojson.properties.name);
            }
        });
        layer.load("/api/report/report.geojson?_status_id=" + status_id)
        map.addLayer(layer)

        // Sync layer to map to preserve classic layer functionnalities
        var mapsync = new L.MapListSync(dt,
            map,
            layer, {
            filter: {
                form: $('#mainfilter'),
                submitbutton: $('#filter'),
                resetbutton: $('#reset'),
                bboxfield: $('#id_bbox'),
            }
        });
        mapsync.on('reloaded', function (data) {
            MapEntity.history.saveListInfo({
                model: data.modelname,
                nb: data.nbrecords
            });
            layer.fire('info', { info: (data.nbrecords + ' ' + tr("results")) });
        });
        objectsLayers.push(layer);
    }
    window.objectsLayers = objectsLayers;

    // Listen to some events to maintain map functionalities (dirty...)
    // When page is first loaded, bind hovering and remove original data layer 
    objectsLayers[objectsLayers.length - 1].addEventListener("loaded", function () {
        map.removeLayer(window.objectsLayer);
        bindHover()
    });
    // Re-bind hovering everytime datatable content is changed
    $('#objects-list').on('draw.dt', bindHover);
}

function ChangeColor(e, data) {
    if (data.modelname != 'report')
        return;
    var map = data.map;
    map.eachLayer(function (layer) {
        if (layer.options['modelname'] === "report") {
            layer.setStyle({ color: $("#report_color").text() })
        }
    }
    )
}

function InitReportStatusLegend(e, data) {
    if (data.modelname != 'report')
        return;
    var map = data.map;

    var legend = L.control({ position: 'bottomleft' });
    legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'legend-statuses');
        header = ['<span style="text-align: center;display: block;"><strong>' + tr("Statuses") + '</strong></span>']
        inner = []
        // For each report status
        var status_ids_and_colors = JSON.parse($('#status_ids_and_colors').text());
        for (var status in status_ids_and_colors) {
            status_label = status_ids_and_colors[status]["label"]
            status_color = status_ids_and_colors[status]["color"]
            status_id = status_ids_and_colors[status]["identifier"]
            div.innerHTML +=
                inner.push(
                    '<i class="legend-circle ' + status_id + '" style="background:' + status_color + '"></i> ' + status_label
                );
        }
        div.innerHTML = header
        div.innerHTML += inner.join('<br>');
        return div;
    };
    legend.addTo(map);

    $(".legend-statuses")[0].style.display = 'none'; // init as hidden, use selector in controls overlay to display

    var LegendLayer = L.Class.extend({
        onAdd: function (map) {
            $(".legend-statuses").toggle();
        },
        onRemove: function (map) {
            $(".legend-statuses").toggle();
        },
    });
    control = new LegendLayer()
    map.layerscontrol.addOverlay(control, tr("Legend"));
    map.addLayer(control); //init as visible
}

$(window).on('entity:map:detail', ChangeColor);
$(window).on('entity:map:list', ChangeColors);
$(window).on('entity:map:list', InitReportStatusLegend);
