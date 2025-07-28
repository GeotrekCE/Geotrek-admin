PointsReferenceField = L.GeometryField.extend({
    // This field is in charge of incrementing number for each marker
    // that is drawn or loaded.

    initialize: function () {
        L.GeometryField.prototype.initialize.apply(this, arguments);
    },

    addTo: function (map) {
        L.GeometryField.prototype.addTo.apply(this, arguments);
        var $toolbar = $(this._drawControl._container);
        $toolbar.find('.leaflet-draw-draw-marker').attr('title', tr('Add a point of reference'));
        $toolbar.find('.leaflet-draw-edit-edit').attr('title', tr('Move points of reference'));
        $toolbar.find('.leaflet-draw-edit-remove').attr('title', tr('Delete a point of reference'));
    },

    _controlDrawOptions: function () {
        var options = L.GeometryField.prototype._controlDrawOptions.call(this);
        options.draw.marker = {};
        options.draw.marker.icon = L.divIcon({className: 'point-reference', html: '+'});
        return options;
    },

    _setView: function () {
        // Do not affect map view on load (keep trek extent)
        // Override and do nothing.
    },

    setNumber: function (marker, number) {
        // Helper
        marker.setIcon(L.divIcon({className: 'point-reference', html: number}));
    },

    onCreated: function (e) {
        // When user added a marker
        L.GeometryField.prototype.onCreated.apply(this, arguments);
        this.setNumber(e.layer, this.drawnItems.getLayers().length);
    },

    onDeleted: function (e) {
        // When user deleted a marker
        L.GeometryField.prototype.onDeleted.apply(this, arguments);
        var points = this.drawnItems.getLayers();
        for (var i=0, n=points.length; i<n; i++) {
            this.setNumber(points[i], i+1);
        }
    },

    load: function () {
        // When instance multipoint is loaded
        var geometry = L.GeometryField.prototype.load.apply(this, arguments);
        if (geometry) {
            var points = geometry.getLayers();
            for (var i=0, n=points.length; i<n; i++) {
                this.setNumber(points[i], i+1);
            }
        }
        return geometry;
    }
});