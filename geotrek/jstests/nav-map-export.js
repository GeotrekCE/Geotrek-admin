var utils = require('./_nav-utils.js');

casper.test.begin('Map export', function(test) {

    casper.start(utils.baseurl + '/path/list/', function() {
        casper.waitForSelector('.leaflet-clickable');
    });

    casper.then(function() {
        casper.waitForSelector('a.screenshot-control');
    });

    casper.then(function() {
        test.comment('Click on screenshot button');
        this.click('a.screenshot-control');
        this.waitForResource(utils.baseurl + '/map_screenshot/');
    });

    casper.then(function(resource) {
        test.assertEqual(resource.status, 200,
                         'Screenshot can be obtained');
        var contenttype = resource.headers.get('Content-Type');
        test.assertEqual(contenttype, 'image/png',
                         'Screenshot is PNG');
        var disposition = resource.headers.get('Content-Disposition');
        test.assertTrue(/attachment; filename=/.test(disposition),
                        'Screenshot is served as attachment.');
    });

    casper.run(function done() {
        test.done();
    });
});
