var utils = require('./_nav-utils.js');

casper.test.begin('Login from home page', function(test) {

    utils.setUp();

    casper.start(utils.baseurl + '/', function () {
        test.assertUrlMatch('/login/?next=/', 'Redirects to login page.');
        casper.echo('#4');
        test.assertExists('form', 'Form present.');
        casper.echo('#5');
    });
    casper.echo('#1');

    casper.then(function () {
        casper.echo('#6');
        casper.fill('form', {
            'username':    'admin',
            'password':    'admin',
        }, true);
        casper.echo('#7');
        casper.click('button[type="submit"]');
        casper.echo('#8');
    });
    casper.echo('#2');

    casper.then(function () {
        casper.echo('#9');
        test.assertUrlMatch('/', 'Logged-in and redirected.');
        casper.echo('#10');
        utils.saveCookies();
        casper.echo('#11');
    });
    casper.echo('#3');

    casper.run(function done() {
        casper.echo('#12');
        test.done();
    });
});
