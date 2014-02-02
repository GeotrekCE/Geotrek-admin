casper.test.begin('Login from home page', function(test) {

    var baseurl = casper.cli.options['baseurl'];

    casper.start(baseurl + '/', function () {
        test.assertUrlMatch('/login/?next=/', 'Redirects to login page.');
        test.assertExists('form', 'Form present.');
    });

    casper.run(function done() {
        test.done();
    });
});
