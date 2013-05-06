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
    var p = this.evaluate(function() {
        return L.GeomUtils.getPercentageDistance(
            L.point(2, 2), [ L.point(1, 1), L.point(3, 3) ]
        );
    });
    this.test.assert(p.distance == 1/2);
    this.test.assert(p.closest.x == 1 && p.closest.y == 1);

    var p = this.evaluate(function() {
        return L.GeomUtils.getPercentageDistance(
            L.point(2, 2), [ L.point(1, 1), L.point(3, 3), L.point(4, 4) ]
        );
    });
    this.test.assert(p.distance == 1/3);
    this.test.assert(p.closest.x == 1 && p.closest.y == 1);

    var p = this.evaluate(function() {
        return L.GeomUtils.getPercentageDistance(
            L.point(2, 2), [ L.point(4, 4), L.point(3, 3), L.point(1, 1) ]
        );
    });
    this.test.assert(p.distance == 2/3);
    this.test.assert(p.closest.x == 3 && p.closest.y == 3);
});

casper.run(function() {this.test.renderResults(true);});
