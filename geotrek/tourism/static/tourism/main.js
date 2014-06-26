$(window).on('entity:map', function (e, data) {

    var map = data.map;

    var template = $('#tourism-popup-template').html();

    function locationMarker(source, feature, latlng) {
        var html = L.Util.template('<img width="16" src="{pictogram_url}"/>',
                                   source);

        var icon = L.divIcon({html: html,
                              className: 'tourism-datasource-marker',
                              iconSize: [16, 0]});
        var marker = L.marker(latlng, {icon: icon});

        marker.on('click', function (e) {
            var props = L.Util.extend({title:'', description:'', website: ''},
                                      feature.properties);
                content = L.Util.template(template, props);

            marker.bindPopup(content)
                  .openPopup();
        });
        return marker;
    }

    function locationMarkerFunc(ds) {
        return function (feature, latlng) {
            return locationMarker(ds, feature, latlng);
        };
    }

    $.getJSON(window.SETTINGS.urls.tourism_datasources, function (datasources) {
        for (var i=0; i<datasources.length; i++) {
            var dataSource = datasources[i],
                pointToLayerFunc = locationMarkerFunc(dataSource);

            var is_visible = (!dataSource.targets || dataSource.targets.indexOf(data.appname) > -1);
            if (!is_visible)
                continue;

            var layer = new L.ObjectsLayer(null, {
                indexing: false,
                pointToLayer: pointToLayerFunc
            });
            layer.load(dataSource.geojson_url);
            var nameHTML = '<img style="background-color: lightgray" width="16" src="' + dataSource.pictogram_url + '"/>&nbsp;' + dataSource.title;
            map.layerscontrol.addOverlay(layer, nameHTML, tr('Data sources'));
        }
    });
});
