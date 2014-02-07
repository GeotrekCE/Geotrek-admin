var utils = require('./_nav-utils.js');

casper.test.begin('Create a new intervention', function(test) {

    var baseurl = casper.cli.options['baseurl'];

    utils.setUp();
    utils.loadCookies();

    casper.start(baseurl + '/intervention/add/', function () {
        casper.waitForSelector('a.linetopology-control', function sucess () {
            test.assertExists('a.linetopology-control', 'Line topology control available.');
            test.assertExists('a.pointtopology-control', 'Point topology control available.');
        });
    });

    casper.run(function done() {
        test.done();
    });
});
