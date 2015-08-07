var ServiceLayer = L.GeoJSON.extend({

    initialize: function (servicesData, options) {
        options = options || {};
        options.pointToLayer = this.servicesMarker.bind(this);
        L.GeoJSON.prototype.initialize.call(this, servicesData, options);
    },

    servicesMarker: function(featureData, latlng) {
        // Label
        var serviceLabel = featureData.properties.type.name;

        var img = L.Util.template('<img src="{SRC}" title="{TITLE}">', {
            SRC: featureData.properties.type.pictogram,
            TITLE: serviceLabel
        });

        var serviceicon = new L.DivIcon({className: 'service-marker-icon',
                                    iconSize: [this.options.iconSize, this.options.iconSize],
                                    html: img}),
            marker = L.marker(latlng, {icon: serviceicon});
        marker.properties = featureData.properties;

        return marker;
    }
});
