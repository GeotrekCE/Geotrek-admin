var utils = require('./_nav-utils.js');

casper.test.begin('Map export', function(test) {

    var baseurl = casper.cli.options['baseurl'];

    utils.setUp();
    utils.loadCookies();

    casper.start(baseurl + '/path/list/', function() {
        casper.waitForResource(baseurl + '/api/path/path.geojson');
    });

    casper.then(function() {
        casper.waitForSelector('a.screenshot-control');
    });

    casper.then(function() {
        test.comment('Click on screenshot button');
        this.click('a.screenshot-control');
        this.waitForResource(baseurl + '/map_screenshot/');
    });

    casper.then(function() {
        test.pass('Screenshot can be obtained');
    });

    casper.run(function done() {
        test.done();
    });
});
