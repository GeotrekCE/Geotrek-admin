L.Util.getWKT = function(layer) {

    if (layer instanceof L.Marker)
        return 'POINT(' + coord2str(layer.getLatLng()) + ')';
    else if (layer instanceof L.Polygon) {
        var closed = layer.getLatLngs();
        if (!closed[0].equals(closed[closed.length-1])) {
            closed.push(closed[0]);
        }
        return 'POLYGON(' + coord2str(closed) + ')';
    }
    else if (layer instanceof L.Polyline)
        return 'LINESTRING' + coord2str(layer.getLatLngs());
    return 'GEOMETRY()';


     function coord2str(obj) {
        if(obj.lng) return obj.lng + ' ' + obj.lat;
        if(obj.length === 0) return null;
        var n, c, wkt = [];
        for (n in obj) {
            c = coord2str(obj[n]);
            if (c) wkt.push(c);
        }
        return ("(" + String(wkt) + ")");
    }
};
