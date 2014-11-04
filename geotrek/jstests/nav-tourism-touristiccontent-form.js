var utils = require('./_nav-utils.js');

casper.test.begin('Touristic content categories', function(test) {

    casper.start(utils.baseurl + '/touristiccontent/add/', function(response) {
        casper.waitWhileVisible('#div_id_type1');
    });

    casper.then(function () {
        test.pass('Touristic types are hidden by default');

        this.fill('form', {
            'category': ['1'] // Accomodation
        });

        casper.waitUntilVisible('#div_id_type1');
    });

    casper.then(function () {
        test.pass('Touristic types appear when category is selected');

        test.assertExists("#id_type1 option[value='9']", 'Some types are kept in list');
        test.assertNotExists("#id_type1 option[value='10']", 'Some types were removed');
    });

    casper.run(function done() {
        test.done();
    });
});
