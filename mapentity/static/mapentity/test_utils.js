(function() {

var percentageDistance = function(ll, polyline) {
    return MapEntity.Utils.getPercentageDistance(
        ll, polyline.getLatLngs(), 1000 /* in meters */, true
    );
}

var getLatLngFromPos = function() {
    return MapEntity.Utils.getLatLngFromPos.apply(null,
        [].slice.call(arguments).concat([ 2000 /* meters */ ])
    );
}


$('<div id="map"></div>')
    .css({'width': '400px', 'height': '200px', 'min-height': '200px'
        , 'position': 'absolute', 'top': 0, 'left': 200
        , 'z-index': 5000})
    .appendTo(document.body);

var map = L.map('map', {
    center: [5, 5],
    zoom: 3
});

$('#map').hide();

var getPolyline10 = function() {
    return new L.Polyline([ 
             [0, 0]
           , [5, 5]
           , [10, 10]
    ]);
};

var getPolyline10reversed = function() {
    return new L.Polyline([
             [10, 10]
           , [5, 5]
           , [0, 0]
    ]);
};

var ORIG_LATLNG_MARGIN = L.LatLng.MAX_MARGIN;

function compareLatLngs(lls1, lls2) {

    equal(lls1.length, lls2.length);

    // Big margin of error because we use LatLng with only round numbers (1, 2, 3, ...)
    L.LatLng.MAX_MARGIN = 1.0E-9; // 1.0E-9: initial

    for (var i = 0; i < lls1.length; i++) {
        var ll1 = lls1[i], ll2 = lls2[i];
        ok(ll1.equals(ll2))
    }

    L.LatLng.MAX_MARGIN = ORIG_LATLNG_MARGIN;
}

function okLatLng(ll1, ll2) {
    L.LatLng.MAX_MARGIN = 1.0E-1; // 1.0E-9: initial
    ok(ll1.equals(ll2));
    L.LatLng.MAX_MARGIN = ORIG_LATLNG_MARGIN;
}

function almostEqual(n1, n2) {
    return ok(Math.abs(n1 - n2) < 0.01);
}

test('Testing existing/existing: 0 1', function() {
    var start_point = 0, end_point = 1;

    var pl = getPolyline10();
    var res = getLatLngFromPos(map, pl, [start_point, end_point]);

    var lls = pl.getLatLngs();

    equal(res.length, 2);
    okLatLng(res[0], lls[0]);
    okLatLng(res[1], lls[lls.length - 1]);

    almostEqual(percentageDistance(res[0], pl).distance, start_point);
    almostEqual(percentageDistance(res[1], pl).distance, end_point);
});

test('Testing existing/existing: 0 0.5', function() {
    var start_point = 0, end_point = 0.5;

    var pl = getPolyline10();
    var res = getLatLngFromPos(map, pl, [start_point, end_point]);

    equal(res.length, 2);

    okLatLng(res[0], L.latLng(0, 0));
    okLatLng(res[1], L.latLng(5, 5));

    almostEqual(percentageDistance(res[0], pl).distance, start_point);
    almostEqual(percentageDistance(res[1], pl).distance, end_point);
});

test('Testing existing/existing: 0.5 1', function() {
    var start_point = 0.5, end_point = 1;

    var pl = getPolyline10();
    var res = getLatLngFromPos(map, pl, [start_point, end_point]);

    equal(res.length, 2);

    okLatLng(res[0], L.latLng(5, 5));
    okLatLng(res[1], L.latLng(10, 10));

    almostEqual(percentageDistance(res[0], pl).distance, start_point);
    almostEqual(percentageDistance(res[1], pl).distance, end_point);
});

test('Testing non-existing/existing: 0.1 1', function() {
    var start_point = 0.1, end_point = 1;

    var pl = getPolyline10();
    var res = getLatLngFromPos(map, pl, [start_point, end_point]);

    equal(res.length, 2);

    okLatLng(res[0], L.latLng(1, 1));
    okLatLng(res[1], L.latLng(10, 10));

    almostEqual(percentageDistance(res[0], pl).distance, start_point);
    almostEqual(percentageDistance(res[1], pl).distance, end_point);
});

test('Testing existing/non-existing: 0 0.9', function() {
    var start_point = 0, end_point = 0.9;

    var pl = getPolyline10();
    var res = getLatLngFromPos(map, pl, [start_point, end_point]);

    equal(res.length, 2);

    okLatLng(res[0], L.latLng(0, 0));
    okLatLng(res[1], L.latLng(9, 9));

    almostEqual(percentageDistance(res[0], pl).distance, start_point);
    almostEqual(percentageDistance(res[1], pl).distance, end_point);
});

test('Testing existing middle/non-existing 0.5 0.9', function() {
    var start_point = 0.5, end_point = 0.9;

    var pl = getPolyline10();
    var res = getLatLngFromPos(map, pl, [start_point, end_point]);

    equal(res.length, 2);

    okLatLng(res[0], L.latLng(5, 5));
    okLatLng(res[1], L.latLng(9, 9));

    almostEqual(percentageDistance(res[0], pl).distance, start_point);
    almostEqual(percentageDistance(res[1], pl).distance, end_point);
});

test('Testing non-existing/existing middle 0.1 0.5', function() {
    var start_point = 0.1, end_point = 0.5;

    var pl = getPolyline10();
    var res = getLatLngFromPos(map, pl, [start_point, end_point]);

    equal(res.length, 2);

    okLatLng(res[0], L.latLng(1, 1));
    okLatLng(res[1], L.latLng(5, 5));

    almostEqual(percentageDistance(res[0], pl).distance, start_point);
    almostEqual(percentageDistance(res[1], pl).distance, end_point);
});

test('Testing non-existing/non-existing 0.3 0.7', function() {
    var start_point = 0.3, end_point = 0.7;

    var pl = getPolyline10();
    var res = getLatLngFromPos(map, pl, [start_point, end_point]);

    equal(res.length, 2);

    okLatLng(res[0], L.latLng(3, 3));
    okLatLng(res[1], L.latLng(7, 7));

    almostEqual(percentageDistance(res[0], pl).distance, start_point);
    almostEqual(percentageDistance(res[1], pl).distance, end_point);
});


test('Testing, reverse geom, non-existing/non-existing 0.3 0.7', function() {
    var start_point = 0.3, end_point = 0.7;

    var pl = getPolyline10reversed();
    var res = getLatLngFromPos(map, pl, [start_point, end_point]);

    equal(res.length, 2);

    okLatLng(res[0], L.latLng(7, 7));
    okLatLng(res[1], L.latLng(3, 3));

    almostEqual(percentageDistance(res[0], pl).distance, start_point);
    almostEqual(percentageDistance(res[1], pl).distance, end_point);
});

})();

