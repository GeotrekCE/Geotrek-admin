//
// Signage
//

$(window).on('entity:map', function (e, data) {
    var map = data.map;

    // Show signage layer in application maps
	var layer = new L.ObjectsLayer(null, {
		modelname: 'signage',
		style: L.Util.extend(window.SETTINGS.map.styles['signage'] || {}, { clickable:false }),
		pointToLayer: function (feature, latlng) {
			return L.marker(latlng).bindTooltip(feature.properties.name, { permanent: true });
		}
	});
	var url = window.SETTINGS.urls['signage_layer'];
	layer.load(url);
	map.layerscontrol.addOverlay(layer, tr('Signage'), tr('Infrastructure'));
});
