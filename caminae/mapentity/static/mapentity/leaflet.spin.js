L.SpinMapMixin = {
    spin: function (state) {
        var state = !!state;
        if (state) {
            // start spinning !
            if (!this._spinner) {
                this._spinner = new Spinner().spin(this._container);
                this._spinning = 0;
            }
            this._spinning++;
        }
        else {
            this._spinning--;
            if (this._spinning <= 0) {
                // end spinning !
                if (this._spinner) {
                    this._spinner.stop();
                    this._spinner = null;
                }
            }
        }
    }
};

L.Map.include(L.SpinMapMixin);

L.Map.addInitHook(function () {
    this.on('layeradd', function (e) {
        if (!(e.layer instanceof L.GeoJSON)) return;
        if (e.layer.loading) this.spin(true);
        e.layer.on('loading', function (f) { console.log(f); this.spin(true) }, this);
        e.layer.on('loaded',  function (f) { this.spin(false) }, this);
    }, this);
    this.on('layerremove', function (e) {
        if (!(e.layer instanceof L.GeoJSON)) return;
        if (e.layer.loading) this.spin(false);
        e.layer.off('loaded');
        e.layer.off('loading');
    }, this);
});

