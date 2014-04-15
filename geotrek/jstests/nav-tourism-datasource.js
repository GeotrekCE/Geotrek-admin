var utils = require('./_nav-utils.js');

casper.test.begin('Data sources can be added to the map', function(test) {

    casper.start(utils.baseurl + '/trek/list/', function(response) {
        casper.waitForText('OSM - ');
    });

    casper.then(function () {
        test.pass('Data sources are present in layer switcher');

        casper.click('.leaflet-control-layers-overlays label:last-child');

        casper.waitForSelector('.leaflet-marker-pane .leaflet-marker-icon');
    });

    casper.then(function () {
        test.pass('Markers are shown on map');

        var xpath = '//img[contains(@src, "/media/upload/datasource-refugee.svg")]';
        test.assertExists({type: 'xpath', path: xpath},
                          'Category icons are shown');

        casper.click('.tourism-datasource-marker:nth-of-type(1)');
        casper.waitForSelector('.leaflet-popup');
    });

    casper.then(function () {
        test.pass('Popup is shown on click');
        test.assertExists('.leaflet-popup span.title',
                            'Properties are shown within popup');
    });

    casper.thenOpen(utils.baseurl + '/path/list/', function(response) {
        casper.waitForResource('/api/datasource/datasources.json');
    });

    casper.then(function () {
        test.assertTextDoesntExist('OSM - ',
                                   'Tourism layer is not shown if target does not match');
    });

    casper.run(function done() {
        test.done();
    });
});
