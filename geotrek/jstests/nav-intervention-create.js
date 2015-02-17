var utils = require('./_nav-utils.js');

casper.test.begin('Create a new intervention', function(test) {

    casper.start(utils.baseurl + '/intervention/add/', function () {
        // Workaround a bug if we try to use leaflet draw controls before
        // graph is loaded
        casper.waitForResource("graph.json");
    });

    casper.then(function () {
        test.pass('Graph is loaded.');
        casper.waitForSelector('a.linetopology-control');
    });

    casper.then(function () {
        test.pass('Line topology control available.');
        test.assertExists('a.pointtopology-control', 'Point topology control available.');

        casper.waitWhileSelector('.leaflet-control.control-disabled');
    });

    casper.then(function () {
        test.info('Activate point');
        casper.click('a.pointtopology-control');
        casper.waitForSelector('.leaflet-control.enabled a.pointtopology-control');
    });

    casper.then(function () {
        test.pass('Point control was activated.');
        casper.waitForSelector('.leaflet-control.control-disabled a.linetopology-control');
    });

    casper.then(function () {
        test.pass('Line topology control was disabled.');

        casper.mouseEvent('mousemove', '#id_topology_map');
        casper.click('#id_topology_map');
        casper.waitForSelector('.leaflet-marker-pane .leaflet-marker-draggable');
    });

    casper.then(function () {
        test.pass('Point marker was added.');
        casper.wait(1000);
    });

     casper.then(function () {
        var values = casper.getFormValues('form#mainform');
        test.assertTruthy(values['topology']);

        test.info('Activate line');
        casper.click('a.linetopology-control');
        casper.waitForSelector('.leaflet-control.enabled a.linetopology-control');
    });

    casper.then(function () {
        test.pass('Line control was activated.');
        casper.waitForSelector('.leaflet-control.control-disabled a.pointtopology-control');
    });

    casper.then(function () {
        test.pass('Point topology control was disabled.');
        casper.waitWhileSelector('.leaflet-marker-pane .leaflet-marker-draggable');
    });

    casper.then(function () {
        test.pass('Point marker was removed.');
    });

    casper.run(function done() {
        test.done();
    });
});
