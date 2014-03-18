var utils = require('./_nav-utils.js');

casper.test.begin('History tabs', function(test) {

    var objectName = null;

    casper.start(utils.baseurl + '/path/list/', function () {
        test.assertExists('#historylist .history #entitylist-dropdown',
                            'List drop down present');
        test.assertNotExists('#historylist .history.active.first',
                               'Path tab history not shown');
    });

    casper.thenOpen(utils.baseurl + '/path/2/', function () {
        var selector = '#historylist .history.path.active.first';
        test.assertExists(selector, 'Current path tab is shown');

        objectName = casper.evaluate(function() {
            return $('#historylist .history.first span.content').text();
        });
        test.assertTruthy(objectName, 'Active tab shows object name');
    });

    casper.thenOpen(utils.baseurl + '/path/3/', function () {
        var name = casper.evaluate(function() {
            return $('#historylist .history.first span.content').text();
        });
        test.assertTruthy(name, 'Active tab was updated.');
        test.assertElementCount('#historylist .history', 3,
                                'Previous tabs are shown');
        test.assertSelectorHasText('#historylist .history:nth-child(3) span.content', objectName,
                                   'Previous tab shows object name.');
    });

    // TODO : test clicks closes tab
    // TODO : test clicks on first tab redirects to next one
    // TODO : test clicks on last tab redirects to list

    // TODO : test creation/edition page show title in tab
    // TODO : test creation/edition are not inserted into history

    casper.run(function done() {
        test.done();
    });
});
