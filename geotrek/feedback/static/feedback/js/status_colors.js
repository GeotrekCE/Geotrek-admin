function ChangeColors(e, data) {
    if (data.modelname != 'report') {
        return;
    }
    function IndependentColors(feature) {
        return { 'color': feature.properties.color }
    }
    window.objectsLayer.options.style = IndependentColors
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
            if (status_ids_and_colors[status]["display_in_legend"]) {
                status_label = status_ids_and_colors[status]["label"]
                status_color = status_ids_and_colors[status]["color"]
                status_id = status_ids_and_colors[status]["identifier"]
                div.innerHTML +=
                    inner.push(
                        '<i class="legend-circle ' + status_id + '" style="background:' + status_color + '"></i> ' + status_label
                    );
            }
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
