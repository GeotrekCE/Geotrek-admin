var utils = require('./_nav-utils.js');

casper.test.begin('Trek detail page', function(test) {

    casper.start(utils.baseurl + '/trek/9000/', function () {
        casper.waitForSelector("img[src='/static/trekking/parking.png']");
    });

    casper.then(function () {
        test.pass('Parking icon is shown on map.');

        casper.waitForSelector(".leaflet-marker-icon.poi-marker-icon");
    });

    casper.then(function () {
        test.pass('POI are shown on the map.');

        casper.waitForSelector(".leaflet-marker-icon.point-reference");
    });

    casper.then(function () {
        test.pass('Points of reference are shown on the map.');
    });

    casper.run(function done() {
        test.done();
    });
});
