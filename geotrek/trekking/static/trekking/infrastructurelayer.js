/*
var InfrastructuresLayer = L.GeoJSON.extend({

    initialize: function (infrastructuresData, options) {
        options = options || {};
        options.pointToLayer = this.infrastructuresMarker.bind(this);
        L.GeoJSON.prototype.initialize.call(this, infrastructuresData, options);
    },

    infrastructuresMarker: function(featureData, latlng) {
        // Label
        var category = featureData.properties.type.label,
            name = featureData.properties.name,
            infrastructureLabel = category + '&nbsp;: ' + name;
        if (name.indexOf(category) === 0) {  // startswith
            infrastructureLabel = name;
        }

        var img = L.Util.template('<img src="{SRC}" title="{TITLE}">', {
            SRC: featureData.properties.type.pictogram,
            TITLE: infrastructureLabel
        });

        var infrastructureicon = new L.DivIcon({className: 'infrastructure-marker-icon',
                                    iconSize: [this.options.iconSize, this.options.iconSize],
                                    html: img}),
		marker = L.marker(latlng, {icon: infrastructureicon});
        marker.properties = featureData.properties;
        marker.on('click', function() {
            $.get(`/api/infrastructure/drf/infrastructures/${featureData.id}/popup-content`, function(data) {
                marker.bindPopup(
                    data,
                    {autoPan: false});
                marker.openPopup();
            }).fail(function(jqXHR, textStatus, errorThrown) {
                console.error('Failed to load infrastructure popup content:', {
                    id: featureData.id,
                    status: jqXHR.status,
                    statusText: jqXHR.statusText,
                    textStatus: textStatus,
                    error: errorThrown
                });
            });
        });

        return marker;
    }
});
*/