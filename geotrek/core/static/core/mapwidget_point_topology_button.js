/**
 * Customizes GeotrekMapWidget draw controls for snapped fields:
 * - Uses Geotrek's `pointtopology-control.png` icon on the point draw button when snapping is enabled.
 * - Prevents native HTML5 dragging of button images (which would suppress click events and trigger
 *   MaplibreFileLayerControl's "Unsupported file type" alert on drop).
 * - Ensures Geoman's snapping helper mode is enabled when activating a snapped field's draw tool.
 */

document.addEventListener('DOMContentLoaded', () => {
    if (typeof MaplibreDrawControlManager === 'undefined') {
        return;
    }

    const origCreateFieldButtons = MaplibreDrawControlManager.prototype._createFieldButtons;
    MaplibreDrawControlManager.prototype._createFieldButtons = function (fieldId, opts, shapes) {
        origCreateFieldButtons.call(this, fieldId, opts, shapes);
        if (!this._customButtonsContainer) {
            return;
        }

        const staticUrl = window.SETTINGS?.urls?.static || '/static/';
        const buttons = this._customButtonsContainer.querySelectorAll(
            `.mapentity-draw-btn[data-field-id="${fieldId}"]`
        );
        buttons.forEach((btn) => {
            btn.draggable = false;
            btn.addEventListener('dragstart', (e) => e.preventDefault());

            if (
                btn.dataset.shape === 'marker' &&
                opts?.snappingConfig?.enabled &&
                !opts?.customIcon
            ) {
                const img = btn.querySelector('img');
                if (img) {
                    img.src = `${staticUrl}core/images/pointtopology-control.png`;
                }
            }

            btn.querySelectorAll('img').forEach((img) => {
                img.draggable = false;
                img.setAttribute('draggable', 'false');
                img.style.pointerEvents = 'none';
                img.style.userSelect = 'none';
            });
        });
    };

    const origOnFieldButtonClick = MaplibreDrawControlManager.prototype._onFieldButtonClick;
    MaplibreDrawControlManager.prototype._onFieldButtonClick = function (fieldId, shape, btn) {
        origOnFieldButtonClick.call(this, fieldId, shape, btn);
        const fieldOpts = this._fields?.[fieldId]?.options;
        if (
            btn.classList.contains('active') &&
            fieldOpts?.snappingConfig?.enabled &&
            this.geoman?.options?.enableMode
        ) {
            this.geoman.options.enableMode('helper', 'snapping');
        }
    };
});
