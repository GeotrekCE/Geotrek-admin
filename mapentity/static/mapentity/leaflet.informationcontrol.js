L.Control.Information = L.Control.extend({
    options: {
        position: 'bottomright',
    },

    onAdd: function (map) {
        this._container = L.DomUtil.create('div', 'leaflet-control-information leaflet-control-attribution');
        L.DomEvent.disableClickPropagation(this._container);

        map.on('layeradd', this._onLayerAdd, this)
           .on('layerremove', this._onLayerRemove, this);

        return this._container;
    },

    onRemove: function (map) {
        map.off('layeradd', this._onLayerAdd)
           .off('layerremove', this._onLayerRemove);

    },

    _onLayerAdd: function (e) {
        if (e.layer && e.layer.on) {
            e.layer.on('info', L.Util.bind(function (ei) {
                this._container.innerHTML = ei.info;
            }, this));
        }
    },

    _onLayerRemove: function (e) {
        if (e.layer && e.layer.off) {
            e.layer.off('info');
        }
    }
});
