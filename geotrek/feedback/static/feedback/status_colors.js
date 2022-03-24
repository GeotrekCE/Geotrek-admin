function getUrl(properties, layer) {
    return window.SETTINGS.urls.detail.replace(new RegExp('modelname', 'g'), data.modelname)
        .replace('0', properties.pk);
}

function ChangeColors(e, data) {
    if (data.modelname != 'report')
        return;
    var map = data.map;
    var dt = MapEntity.mainDatatable;

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

    }
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

function toggleLegend() {
    $(".legend-inner").toggle();
}

function ShowLegend(e, data) {
    if (data.modelname != 'report')
        return;
    var map = data.map;

    var legend = L.control({ position: 'bottomleft' });
    legend.onAdd = function (map) {

        var div = L.DomUtil.create('div', 'legend-statuses');
        inner = ['<button onclick="toggleLegend()"><strong>' + tr("Statuses") + '</strong></button><div class="legend-inner">']
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
        inner.push("</div>")
        div.innerHTML = inner.join('<br>');
        return div;
    };
    legend.addTo(map);
}

$(window).on('entity:map:detail', ChangeColor);
$(window).on('entity:map:list', ChangeColors);
$(window).on('entity:map:list', ShowLegend);
