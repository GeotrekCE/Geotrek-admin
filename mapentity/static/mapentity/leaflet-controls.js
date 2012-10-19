

L.Control.Information = L.Control.extend({
    options: {
        position: 'bottomright',
    },

    onAdd: function (map) {
        this._container = L.DomUtil.create('div', 'leaflet-control-attribution');
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


L.Mixin.ActivableControl = {
    activable: function (state) {
        /**
         * Allow to prevent user to activate the control.
         * (it is like setEnable(state), but ``enable`` word is used
         *  for handler already)
         */
        this._activable = state;
        if (this._container) {
            if (state)
                L.DomUtil.removeClass(this._container, 'disabled');
            else
                L.DomUtil.addClass(this._container, 'disabled');
        }
    },

    toggle: function() {
        this._activable = !!this._activable;  // from undefined to false :)
        
        if (!this._activable)
            return;  // do nothing if not activable

        if (this.handler.enabled()) {
            this.handler.disable.call(this.handler);
            this.handler.fire('disabled');
            L.DomUtil.removeClass(this._container, 'enabled');
        } else {
            this.handler.enable.call(this.handler);
            this.handler.fire('enabled');
            L.DomUtil.addClass(this._container, 'enabled');
        }
    },
};


L.Control.ExclusiveActivation = L.Class.extend({
    initialize: function () {
        this._controls = [];
    },

    add: function (control) {
        this._controls.push(control);
        var self = this;
        control.handler.on('enabled', function (e) {
            // When this control is enabled, disable the others !
            $.each(self._controls, function (i, c) {
                if (c != control) {
                    c.activable(false);
                }
            });
        }, this);
        
        control.handler.on('disabled', function (e) {
            // When this control is disabled, re-enable the others !
            // Careful, this will not take care of previous state :)
            $.each(self._controls, function (i, c) {
                c.activable(true);
            });
        }, this);
    },
});
