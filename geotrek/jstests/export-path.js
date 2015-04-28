var utils = require('./_nav-utils.js');

casper.test.begin('Path exports files', function(test) {

    casper.start(utils.baseurl + '/path/1/', function(response) {
        test.assertEqual(200, response.status, 'Object exists');
        test.assertEqual('text/html; charset=utf-8', response.contentType,
                         'Detail page is HTML');
    });

    casper.thenOpen(utils.baseurl + '/api/en/path/1/profile.svg', function(response) {
        test.assertEqual(200, response.status, 'Image profile export works');
        test.assertEqual('image/svg+xml', response.contentType,
                         'Profile is SVG');
    });

    casper.thenOpen(utils.baseurl + '/convert/?url=/api/en/path/1/profile.svg&from=image/svg%2Bxml&to=image/png', function(response) {
        test.assertEqual(200, response.status, 'Image profile conversion works');
        test.assertMatch(response.contentType, /^image\/png/,
                         'Profile can be converted to PNG');
    });

    casper.thenOpen(utils.baseurl + '/document/path-1.odt', function(response) {
        test.assertEqual(200, response.status, 'Document export works');
        test.assertEqual('application/vnd.oasis.opendocument.text', response.contentType,
                         'Document is ODT');
    });

    casper.thenOpen(utils.baseurl + '/convert/?url=/document/path-1.odt', function(response) {
        test.assertEqual(200, response.status, 'Document conversion works');
        test.assertMatch(response.contentType, /^application\/pdf/,
                         'Document can be converted to PDF');
    });

    casper.run(function done() {
        test.done();
    });
});
