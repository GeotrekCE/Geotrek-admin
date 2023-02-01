function initializeViewer(base_tile_url, edit_annotations = false) {
    var tileUrl = base_tile_url + `/tiles/{z}/{x}/{y}.png?source=vips`;
    var metadataUrl = base_tile_url + "/info/metadata?source=vips";
    var viewer;

    fetch(metadataUrl)
        .then(response => response.json())
        .then(tileinfo => {
            const params = geo.util.pixelCoordinateParams(
                '#hdviewpoint-map', tileinfo.sizeX, tileinfo.sizeY, tileinfo.tileWidth, tileinfo.tileHeight);
            params.layer.url = tileUrl;
            viewer = geo.map(params.map);
            viewer.zoomRange({
                // do not set a min limit so that bounds clamping determines min
                min: -Infinity,
                max: 12,
            });
            viewer.createLayer('osm', params.layer);

            // Change default interactor options
            const interactorOpts = viewer.interactor().options();
            interactorOpts.zoomAnimation = {
                enabled: false,
            };
            interactorOpts.momentum = {
                enabled: true,
            };
            viewer.interactor().options(interactorOpts);

            var ui = viewer.createLayer('ui');
            // Create a zoom slider widget
            ui.createWidget('slider', {
                position: {
                    left: 40,
                    top: 40
                }
            });
            if (edit_annotations) {
                initAnnotationsWidget(viewer);
            }
            else {
                layer = viewer.createLayer('annotation');
                layer.geojson($('#geojson_annotations').text());
            }
            $(".loader-wrapper").remove();
        });
};
