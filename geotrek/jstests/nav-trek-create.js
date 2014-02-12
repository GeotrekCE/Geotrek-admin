var utils = require('./_nav-utils.js');

casper.test.begin('Create a new trek', function(test) {

    var baseurl = casper.cli.options['baseurl'];

    utils.setUp();
    utils.loadCookies();

    casper.start(baseurl + '/trek/add/', function () {
        casper.waitForSelector('a.linetopology-control');
    });

    casper.then(function () {
        test.pass('Line topology control available.');
        test.assertNotExists('a.pointtopology-control', 'Point topology control is not available.');
    });

    casper.run(function done() {
        test.done();
    });
});
