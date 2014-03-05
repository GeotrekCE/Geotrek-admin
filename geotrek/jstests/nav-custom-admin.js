var utils = require('./_nav-utils.js');

casper.test.begin('Adminsite', function(test) {

    utils.setUp();

    casper.start(utils.baseurl + '/admin/', function () {
        casper.assertTextExists('Back to application');
    });

    casper.run(function done() {
        test.done();
    });
});
