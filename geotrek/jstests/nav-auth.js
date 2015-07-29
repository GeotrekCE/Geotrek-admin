var utils = require('./_nav-utils.js');

casper.test.begin('Login from home page', function(test) {

    utils.setUp();

    casper.start(utils.baseurl + '/', function () {
        test.assertUrlMatch('/login/?next=/', 'Redirects to login page.');
        test.assertExists('form', 'Form present.');
    });

    casper.then(function () {
        casper.fill('form', {
            'username':    'admin',
            'password':    'admin',
        }, true);
        casper.click("button[type='submit']");
    });

    casper.then(function () {
        test.assertUrlMatch('/', 'Logged-in and redirected.');
        utils.saveCookies();
    });

    casper.run(function done() {
        test.done();
    });
});
