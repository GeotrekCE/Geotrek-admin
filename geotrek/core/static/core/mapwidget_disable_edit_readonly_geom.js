/**
 * Prevents Geoman's edit controls (drag, change, delete) from modifying read-only
 * geometries on the map (e.g. when a linear topology's `geom` field has `modifiable=False`
 * or when `allowed_types` restricts editing to points).
 */

document.addEventListener('DOMContentLoaded', () => {
    if (typeof MaplibreGeometryField !== 'undefined') {
        const origLoadInitialGeometry = MaplibreGeometryField.prototype._loadInitialGeometry;
        MaplibreGeometryField.prototype._loadInitialGeometry = function () {
            const origNormalize = this.dataManager.normalizeToFeatureCollection.bind(this.dataManager);
            this.dataManager.normalizeToFeatureCollection = (geojson) => {
                const normalized = origNormalize(geojson);
                const shapeMap = {
                    point: 'marker',
                    multipoint: 'marker',
                    linestring: 'line',
                    multilinestring: 'line',
                    polygon: 'polygon',
                    multipolygon: 'polygon',
                };
                normalized.features.forEach((feature) => {
                    const geomType = (feature.geometry?.type || '').toLowerCase();
                    const shape = shapeMap[geomType];
                    if (!this.options.modifiable || (shape && !this._isShapeForThisField(shape))) {
                        feature.properties = feature.properties || {};
                        feature.properties.disableEdit = true;
                    }
                });
                return normalized;
            };
            return origLoadInitialGeometry.call(this);
        };

        MaplibreGeometryField.prototype._syncCustomMarkersFromSource = function () {
            if (!this._customMarkers) return;
            const entries = Object.entries(this._customMarkers);
            if (entries.length === 0) return;

            const featureStore = this.map?.gm?.features?.featureStore;
            const source = this.map?.getSource('gm_main');
            const data = source?._data;
            const updateable = data?.updateable;
            const features = data?.geojson?.features || data?.features;

            for (const [id, marker] of entries) {
                if (!marker) continue;
                let f = featureStore?.get?.(id)?.getGeoJson?.() || updateable?.get?.(id);
                if (!f && Array.isArray(features)) {
                    f = features.find((feat) => String(feat.id ?? feat.properties?.gm_id) === String(id));
                }
                if (f?.geometry?.type === 'Point' && Array.isArray(f.geometry.coordinates)) {
                    const currentLngLat = marker.getLngLat();
                    if (currentLngLat.lng !== f.geometry.coordinates[0] || currentLngLat.lat !== f.geometry.coordinates[1]) {
                        marker.setLngLat(f.geometry.coordinates);
                    }
                }
            }
        };
    }

    if (typeof MaplibreDrawControlManager !== 'undefined') {
        const origAddFieldControls = MaplibreDrawControlManager.prototype.addFieldControls;
        MaplibreDrawControlManager.prototype.addFieldControls = function (fieldOptions) {
            if (fieldOptions && fieldOptions.modifiable) {
                const editControls = this.geoman?.options?.controls?.edit;
                if (editControls) {
                    ['drag', 'change', 'delete'].forEach((action) => {
                        if (editControls[action]) {
                            editControls[action].uiEnabled = true;
                        }
                    });
                    this.geoman.control?.updateReactivePanel?.();
                }
            }
            return origAddFieldControls.call(this, fieldOptions);
        };
    }

    if (typeof Geoman !== 'undefined' && Geoman.BaseEdit) {
        Geoman.BaseEdit.prototype.getFeatureByMouseEvent = function ({ event, sourceNames }) {
            if (!Geoman.isMapPointerEvent(event, { warning: true })) {
                return null;
            }
            const point = [event.point.x, event.point.y];
            const features = this.gm.mapAdapter
                .queryFeaturesByScreenCoordinates({
                    queryCoordinates: point,
                    sourceNames,
                })
                .filter((f) => f.getShapeProperty('disableEdit') !== true);
            if (features.length === 0) {
                return null;
            }
            return features.find((f) => !Geoman.SHAPE_NAMES.includes(f.shape)) ?? features[0];
        };

        Geoman.BaseEdit.prototype.setCursorToPointer = function (event) {
            if (event && !this.getFeatureByMouseEvent({ event, sourceNames: [Geoman.SOURCES.main] })) {
                return;
            }
            if (!this.flags.actionInProgress) {
                this.gm.mapAdapter.setCursor('pointer');
            }
        };
    }
});

