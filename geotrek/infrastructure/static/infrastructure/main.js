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
			return L.marker(latlng).bindLabel(feature.properties.name, { noHide: true });
		}
	});
	var url = window.SETTINGS.urls['signage_layer'];
	layer.load(url);
	map.layerscontrol.addOverlay(layer, tr('Signage'), tr('Infrastructure'));
});


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
