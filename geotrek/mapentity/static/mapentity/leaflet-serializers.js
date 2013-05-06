L.Util.getWKT = function(layer) {
    coord2str = function (obj) {
        if(obj.lng) return obj.lng + ' ' + obj.lat + ' 0.0';
        if(obj.length == 0) return null;
        var n, c, wkt = [];
        for (n in obj) {
            c = coord2str(obj[n]);
            if (c) wkt.push(c);
        }
        return ("(" + String(wkt) + ")");
    };
    var coords = '()';
    if(layer.getLatLng) {
        coords = '(' + coord2str(layer.getLatLng()) + ')';
    }
    else if (layer.getLatLngs) {
        coords = coord2str(layer.getLatLngs());
    }
    var wkt = '';
    if (layer instanceof L.Marker) wkt += 'POINT'+coords;
    else if (layer instanceof L.Polygon) wkt += 'POLYGON('+coords+')';
    else if (layer instanceof L.MultiPolygon) wkt += 'MULTIPOLYGON('+coords+')';
    else if (layer instanceof L.Polyline) wkt += 'LINESTRING'+coords;
    else if (layer instanceof L.MultiPolyline) wkt += 'MULTILINESTRING('+coords+')';
    else {
        wkt += 'GEOMETRY'+coords;
    }
    return wkt;
};
