var Caminae = Caminae || {};

Caminae.TopologyHelper = (function() {

    // Returns true if the first point of the polyline
    // is shared with one of the edge of the polyline
    function getOrder(polyline, next_polyline) {
        var ll_p = polyline.getLatLngs()[0];
        if (!next_polyline) return false;

        var lls = next_polyline.getLatLngs()
          , ll_a = lls[0]
          , ll_b = lls[lls.length - 1];

        return ll_p.equals(ll_a) || ll_p.equals(ll_b);
    }

    // Returns [start_position, end_position]
    function getPosition(bound_by_first_point, distance) {
        // bound_by_first_point => start point is included
        return bound_by_first_point ? [0.0, distance] : [distance, 1.0];
    }

    function buildTopologyGeom(polylines, ll_start, ll_end, start, end) {
        var closest_first_idx = start.closest
          , closest_end_idx = end.closest;

        var polyline_start = polylines[0]
          , polyline_end = polylines[polylines.length - 1]
          , single_path = polyline_start == polyline_end
          // Positions:: polylines index => pair of position [ [0..1], [0..1] ]
          , positions = {};

        var polylines_inner = single_path ? null : polylines.slice(1, -1);

        // Is the first point bound to the next edge or is it the other way ?

        var lls_tmp, lls_end, latlngs = [];

        if (single_path) {
            var _ll_end, _ll_start, _closest_first_idx, _closest_end_idx;
            if (closest_first_idx < closest_end_idx) {
                _ll_end = ll_end, _ll_start = ll_start;
                _closest_first_idx = closest_first_idx, _closest_end_idx = closest_end_idx;
            } else {
                _ll_end = ll_start, _ll_start = ll_end;
                _closest_first_idx = closest_end_idx, _closest_end_idx = closest_first_idx;
            }

            lls_tmp = polyline_start.getLatLngs().slice(_closest_first_idx+1, _closest_end_idx + 1);
            lls_tmp.unshift(_ll_start);
            lls_tmp.push(_ll_end);
            latlngs.push(lls_tmp);
            positions[0] = [start.distance, end.distance];
        }
        else {
            var start_bound_by_first_point = getOrder(polyline_start, polylines[1]);
            if (start_bound_by_first_point) {
                // <--o-c- x---x---x // first point is shared ; include closest
                lls_tmp = polyline_start.getLatLngs().slice(0, closest_first_idx + 1)
                lls_tmp.push(ll_start);
            } else {
                // -c-o--> x---x---x // first point is not shared ; don't include closest
                lls_tmp = polyline_start.getLatLngs().slice(closest_first_idx + 1);
                lls_tmp.unshift(ll_start);
            }
            positions[0] = getPosition(start_bound_by_first_point, start.distance);

            latlngs.push(lls_tmp);

            $.each(polylines_inner, function(idx, l) {
                latlngs.push(l.getLatLngs());
            });

            var end_bound_by_first_point = getOrder(polyline_end, polylines[polylines.length - 2]);
            if (end_bound_by_first_point) {
                // x---x---x -c-o--> // first point is shared ; include closest
                lls_tmp = polyline_end.getLatLngs().slice(0, closest_end_idx + 1);
                lls_tmp.push(ll_end);
            } else {
                // x---x---x <--o-c- // first point is not shared ; don't include closest
                lls_tmp = polyline_end.getLatLngs().slice(closest_end_idx + 1);
                lls_tmp.unshift(ll_end);
            }
            positions[polylines.length - 1] = getPosition(end_bound_by_first_point, end.distance);

            latlngs.push(lls_tmp);
        }

        return {
            'geom': new L.MultiPolyline(latlngs),
            'positions': positions,
            'is_single_path': single_path
        };
    }

    return {
        buildTopologyGeom: buildTopologyGeom
    };
})();
