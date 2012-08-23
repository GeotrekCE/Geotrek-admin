// Testing javascript only stuff

var x = require('casper').selectXPath;
var casper = require('casper').create();
var baseurl = casper.cli.options['baseurl'];
casper.options.viewportSize = {width: 1146, height: 758};

casper.start(baseurl);

casper.waitForSelector("form",
    function success() {
        this.fill("form", {"username": "admin",
                           "password": "admin"}, true);
    },
    function fail() {
        this.test.assertExists("form");
});


// Testing getPercentageDistanceFromPoints
// Used to calculate start_position and end_position for topology
casper.thenOpen(baseurl + '/intervention/add/', function() {
    var distance = this.evaluate(function() {
        return MapEntity.Utils.getPercentageDistanceFromPoints(
            L.point(2, 2), [ L.point(1, 1), L.point(3, 3) ]
        );
    });
    this.test.assert(distance == 1/2);

    var distance = this.evaluate(function() {
        return MapEntity.Utils.getPercentageDistanceFromPoints(
            L.point(2, 2), [ L.point(1, 1), L.point(3, 3), L.point(4, 4) ]
        );
    });
    this.test.assert(distance == 1/3);

    var distance = this.evaluate(function() {
        return MapEntity.Utils.getPercentageDistanceFromPoints(
            L.point(2, 2), [ L.point(4, 4), L.point(3, 3), L.point(1, 1) ]
        );
    });
    this.test.assert(distance == 2/3);
});

casper.run(function() {this.test.renderResults(true);});
