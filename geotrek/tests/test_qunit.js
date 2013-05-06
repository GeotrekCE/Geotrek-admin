/*
*
* Get test names and urls at /jstest_list/, run them and generate test reports.
*
*/

var casper = require('casper').create();
var utils = require('utils');
var fs = require('fs');


var baseurl = casper.cli.options['baseurl'];
var reportdir = casper.cli.options['reportdir'];
var qunit_test_urls = baseurl + '/jstest_list/'

casper.options.viewportSize = {width: 1146, height: 758};



// Extracted a part of getPageContent (casper.js 1.0)
function coercePageContentToJSON(page_content) {
    // for some reason webkit/qtwebkit will always enclose body contents within html tags
    var match = new RegExp('^<html><head></head><body><pre.+?>(.*)</pre></body></html>$').exec(page_content);
    return JSON.parse(match[1]);
}

casper.start(qunit_test_urls).then(function() {

    var qunit_hash = coercePageContentToJSON(this.page.content);
    var qunit_names = Object.keys(qunit_hash);

    function nextOpen() {
        if (qunit_names.length == 0) return;

        var qunit_name = qunit_names.pop();
        var qunit_url = qunit_hash[qunit_name];

        casper.thenOpen(baseurl + qunit_url, function() {
            console.log('Testing "', qunit_name, '" at ', qunit_url);

            var xml = null;
            casper.waitFor(function check() {
                return xml = this.evaluate(function() {
                    return QUnit.getReport && QUnit.getReport();
                });
            }, function then() {
                // Change FUNC to TEST or whatever
                fs.write(reportdir + '/FUNC-qunit-' + qunit_name + '.xml', xml, 'w');
                nextOpen();
            });
        });
    }

    nextOpen();
});

casper.run();
