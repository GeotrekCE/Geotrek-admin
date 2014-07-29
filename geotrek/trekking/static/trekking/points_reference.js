PointsReferenceField = L.GeometryField.extend({

    initialize: function () {
        L.GeometryField.prototype.initialize.apply(this, arguments);
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