/**
 * Marks the `geom_changed` hidden field as checked whenever the user creates, edits or
 * removes the geometry for the `geom` field's map widget (LinearTopologyMapWidget).
 */

document.addEventListener('DOMContentLoaded', function () {
    const geomElem = document.getElementById('id_geom');
    const geomChangedElem = document.getElementById('id_geom_changed');
    if (!geomElem || !geomChangedElem) return;

    const proto = Object.getPrototypeOf(geomElem);
    const nativeDescriptor = Object.getOwnPropertyDescriptor(proto, 'value');

    Object.defineProperty(geomElem, 'value', {
        configurable: true,
        get: function () {
            return nativeDescriptor.get.call(this);
        },
        set: function (val) {
            geomChangedElem.checked = true;
            geomChangedElem.value = true;
            nativeDescriptor.set.call(this, val);
        }
    });
});