//
// Infrastructure
//

$(window).on('entity:map', function (e, data) {
    var map = data.map;

    // Show infrastructure layer in application maps
	var layer = new L.ObjectsLayer(null, {
		modelname: 'infrastructure',
		style: L.Util.extend(window.SETTINGS.map.styles['infrastructure'] || {}, { clickable:false }),
		pointToLayer: function (feature, latlng) {
			var infrastructureIcon = L.icon({
				iconUrl: feature.properties.type.pictogram,
				iconSize: [18, 18],
				iconAnchor: [9, 9],
			});
			return L.marker(latlng, {icon: infrastructureIcon});
		}
	});
	var url = window.SETTINGS.urls['infrastructure_layer'];
	layer.load(url);
	map.layerscontrol.addOverlay(layer, tr('Infrastructure'), tr('Infrastructure'));
});
