var POILayer = L.GeoJSON.extend({

    initialize: function (poisData, options) {
        options = options || {};
        options.pointToLayer = this.poisMarker.bind(this);
        L.GeoJSON.prototype.initialize.call(this, poisData, options);
    },

    poisMarker: function(featureData, latlng) {
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

        var poicon = new L.DivIcon({className: 'poi-marker-icon',
                                    iconSize: [this.options.iconSize, this.options.iconSize],
                                    html: img}),
            marker = L.marker(latlng, {icon: poicon});
        marker.properties = featureData.properties;

        /* If POI has a thumbnail, show popup on click */
        if (marker.properties.thumbnail) {
            marker.bindPopup(
                L.Util.template('<img src="{SRC}" width="110" height="110">', {
                    SRC: marker.properties.thumbnail
                }),
                {autoPan: false});
        }
        return marker;
    }
});
