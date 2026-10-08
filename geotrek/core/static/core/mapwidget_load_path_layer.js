document.addEventListener('DOMContentLoaded', () => {
    if (typeof MaplibreObjectsLayer === 'undefined') {
        return;
    }
    const origRegisterLazyLayer = MaplibreObjectsLayer.prototype.registerLazyLayer;
    MaplibreObjectsLayer.prototype.registerLazyLayer = function (modelname, category, nameHTML, primaryKey, dataUrl) {
        origRegisterLazyLayer.call(this, modelname, category, nameHTML, primaryKey, dataUrl);
        if (modelname === 'path' && this._map?.getContainer()?.id !== 'id_topology_map') {
            this.options.displayPopup = false;
            this.layerManager.layers.lazyOverlays[category][primaryKey].isVisible = true;
            this.layerManager.toggleLazyOverlay(category, primaryKey, true);
        }
    };
});
