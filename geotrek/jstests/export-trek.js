var utils = require('./_nav-utils.js');

casper.test.begin('Trek exports files', function(test) {

    casper.start(utils.baseurl + '/trek/9000/', function(response) {
        test.assertEqual(200, response.status, 'Object exists');
        test.assertEqual('text/html; charset=utf-8', response.contentType,
                         'Detail page is HTML');
    });

    casper.thenOpen(utils.baseurl + '/image/trek-9000.png', function(response) {
        test.assertEqual(200, response.status, 'Image export works');
        test.assertMatch(response.contentType, /^image\/png/,
                         'Map export is PNG');
    });

    casper.thenOpen(utils.baseurl + '/document/print-trek-9000.odt', function(response) {
        test.assertEqual(200, response.status, 'Public export works');
        test.assertEqual('application/vnd.oasis.opendocument.text', response.contentType,
                         'Public document is ODT');
    });

    casper.thenOpen(utils.baseurl + '/api/en/trek/trek-9000.pdf', function(response) {
        test.assertEqual(200, response.status, 'Public export works');
        test.assertMatch(response.contentType, /^application\/pdf/,
                         'Public document can be converted to PDF');
    });

    casper.run(function done() {
        test.done();
    });
});
