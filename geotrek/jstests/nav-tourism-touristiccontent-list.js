var utils = require('./_nav-utils.js');

casper.test.begin('Touristic content categories', function(test) {

    casper.start(utils.baseurl + '/touristiccontent/list/', function(response) {
        test.assertExists('a[href="/touristiccontent/add/"]', 'Add button exists');

        // Select a category
        casper.click("a[data-category='1']");
        casper.waitForSelector("a[href='/touristiccontent/add/?category=1']");
    });

    casper.then(function () {
        test.pass('Selected category is passed to Add button');
    });

    casper.run(function done() {
        test.done();
    });
});
