/*
var POILayer = L.GeoJSON.extend({
    initialize: function (poisData, options) {
        options = options || {};
        options.pointToLayer = this.poisMarker.bind(this);
        L.GeoJSON.prototype.initialize.call(this, poisData, options);
    },

    poisMarker: function (featureData, latlng) {
        // Label
        var category = featureData.properties.type.label,
            name = featureData.properties.name,
            poiLabel = category + '&nbsp;: ' + name;
        if (name.indexOf(category) === 0) {  // startswith
            poiLabel = name;
        }

        var img = L.Util.template('<img src="{SRC}" title="{TITLE}">', {
            SRC: featureData.properties.type.pictogram,
            TITLE: poiLabel
        });

        var poicon = new L.DivIcon({
                className: 'poi-marker-icon',
                iconSize: [this.options.iconSize, this.options.iconSize],
                html: img
            }),
            marker = L.marker(latlng, {icon: poicon});
        marker.properties = featureData.properties;

        marker.on('click', function () {
            $.get(`/api/poi/drf/pois/${featureData.id}/popup-content`, function (data) {
                marker.bindPopup(
                    data,
                    {autoPan: false});
                marker.openPopup();
            }).fail(function (jqXHR, textStatus, errorThrown) {
                console.error('Failed to load POI popup content for ID ' + featureData.id + ':', textStatus, errorThrown);
            });
        });
        return marker;
    }
 });

 */

