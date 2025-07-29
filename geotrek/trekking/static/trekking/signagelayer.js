/*
var SignagesLayer = L.GeoJSON.extend({

    initialize: function (signagesData, options) {
        options = options || {};
        options.pointToLayer = this.signagesMarker.bind(this);
        L.GeoJSON.prototype.initialize.call(this, signagesData, options);
    },

    signagesMarker: function(featureData, latlng) {
        // Label
        var category = featureData.properties.type.label,
            name = featureData.properties.name,
            serviceLabel = category + '&nbsp;: ' + name;
        if (name.indexOf(category) === 0) {  // startswith
          serviceLabel = name;
        }

        var img = L.Util.template('<img src="{SRC}" title="{TITLE}">', {
            SRC: featureData.properties.type.pictogram,
            TITLE: serviceLabel
        });

        var serviceicon = new L.DivIcon({className: 'infrastructure-marker-icon',
                                    iconSize: [this.options.iconSize, this.options.iconSize],
                                    html: img});

        var marker = L.marker(latlng, {icon: serviceicon}).bindLabel(featureData.properties.name, {noHide: true});
        marker.on('click', function() {
            $.get(`/api/signage/drf/signages/${featureData.id}/popup-content`)
                .done(function(data) {
                    marker.bindPopup(
                        data,
                        {autoPan: false});
                    marker.openPopup();
                })
                .fail(function(jqXHR, textStatus, errorThrown) {
                    console.error('Failed to load signage popup content for ID ' + featureData.id + ':', textStatus, errorThrown);
                });
        });

        return marker;
    }
});

 */
