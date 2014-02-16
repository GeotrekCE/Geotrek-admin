var utils = require('./_nav-utils.js');

casper.test.begin('Create a new poi', function(test) {

    casper.start(utils.baseurl + '/poi/add/', function () {
        casper.waitForSelector('a.pointtopology-control');
    });

    casper.then(function () {
        test.pass('Point topology control available.');
        test.assertNotExists('a.linetopology-control',
                             'Line topology control is not available.');
    });

    casper.run(function done() {
        test.done();
    });
});
