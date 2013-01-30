L.GeomUtils = (function() {
    var self;
    return self = {

        // Calculate if a point p is between a and b
        isBetween: function(x, a, b, epsilon) {
            epsilon = epsilon || 0.5;
            var d = x.distanceTo(a) + x.distanceTo(b) - a.distanceTo(b);
            return d < epsilon;
        },

        // Use LatLng
        getPercentageDistanceFromPolyline: function(ll, polyline) {
            // Will test every point, considering a point is in a segment with an error of 5 meters
            return self.getPercentageDistance(ll, polyline.getLatLngs(), 2 /* in meters */, true);
        },

        // May be used for performance issue but you will loose precision
        getPercentageDistanceFromPolylineAsPoints: function(point, polyline) {
            return self.getPercentageDistance(point, polyline._parts[0], 0.5, true);
        },

        // You may pass latlng or point to this function
        getPercentageDistance: function(x, xs, epsilon, only_first) {
            var xs_len = 0
              , distance_found = false
              , closest_idx = null
              , distance = Number.MAX_VALUE;

            for (var i = 0; i < xs.length - 1; i++) {
                var x1 = xs[i], x2 = xs[i+1];

                // We iterate on each segment of the path
                if (!distance_found || !only_first) {
                    if (self.isBetween(x, x1, x2, epsilon)) {
                        distance_found = true;
                        xdistance = xs_len + x.distanceTo(x1);

                        if (only_first || xdistance < distance) {
                            distance = xdistance;
                            closest_idx = i;
                        }
                    }
                }

                xs_len += x1.distanceTo(x2);
            }
            var percent = Math.round((distance / xs_len)*100)/100;
            return distance_found ? { 'distance': percent, 'closest': closest_idx } : null;
        },

        // todo accept an array of positions ?
        getLatLngFromPos: function(map, polyline, pos_list, equal_delta) {
            equal_delta === equal_delta === undefined ? 5 /*in meters*/ : equal_delta;

            $.each(pos_list, function(i, pos) {
                var prev_pos = pos[i - 1];
                var sorted = prev_pos === undefined ? true : pos > prev_pos;

                if (! (pos >= 0 && pos <= 1 && sorted)) {
                    throw 'Wrong value: ' + pos_list;
                }
            });

            // Polyline related
            var polyline_lls = polyline.getLatLngs();
            var d_len = self.getDistances(polyline_lls)
              , polyline_len = d_len.length
              , polyline_distances = d_len.distances;

            // Simple situation... simple solution.
            if (pos_list.length == 1) {
                 if (pos_list[0] == 0.0) return [polyline_lls[0]];
                 if (pos_list[0] == 1.0) return [polyline_lls[polyline_lls.length-1]];
            }

            var ds = $.map(pos_list, function(pos) { return polyline_len * pos; });

            var res = [];
            var i;

            var current_distance = ds.shift()
              , current_geom = [];

            if (current_distance == 0) {
                res.push(self.cloneLatLng(polyline_distances[0].x1));
                current_distance = ds.shift()
            }

            for (i = 0; i < polyline_distances.length; i++) {
                var dist = polyline_distances[i];
                var new_acc = dist.acc + dist.distance;

                var delta = Math.abs(current_distance - new_acc)
                var distance_equal = delta < equal_delta;

                if (distance_equal || current_distance < new_acc) {
                    if (distance_equal) {
                        // Same point
                        res.push(self.cloneLatLng(dist.x2));
                    } else { 
                        // current_distance < new_acc
                        // New point

                        var dist_from_point = current_distance - dist.acc;
                        var ratio_dist = dist_from_point / dist.distance;
                        var ll = self.getPointOnLine(map, ratio_dist, dist.x1, dist.x2);

                        res.push(ll);
                    }

                    if (ds.length == 0) break;
                    current_distance = ds.shift()
                }
            }

            if (res.length < 1) console.warn("Could not get LatLng from position " + pos_list);
            return res;
        },

        cloneLatLng: function(latlng) {
            return new L.LatLng(latlng.lat, latlng.lng);
        },

        getPointOnLine: function(map, ratio_dist, ll1, ll2) {
            var p1 = map.project(ll1, 18)
              , p2 = map.project(ll2, 18)
              , d = p1.distanceTo(p2)
              , point_distance = ratio_dist * d;

            var coeff = self.getFunction(p1.x, p1.y, p2.x, p2.y);
            var angle = Math.atan(coeff.a);

            var sign_x = (p2.x - p1.x) > 0 ? -1 : 1;
            // var sign_y = (p2.y - p1.y) > 0 ? 1 : -1;
            // var y_new = p1.y + sign_y * point_distance * Math.cos(angle);

            var x_new = p1.x + sign_x * point_distance * Math.sin(angle);
            var y_new = coeff.a * x_new + coeff.b;

            return map.unproject(new L.Point(x_new, y_new), 18);
        },

        getFunction: function(x1, y1, x2, y2) {
            var a = (y2 - y1) / (x2 - x1);
            var b = y1 - (a * x1);
            return {'a': a, 'b': b};
        },

        getDistances: function(xs) {
            var xs_len = 0, d, distances = [];

            for (var i = 0; i < xs.length - 1; i++) {
                var x1 = xs[i], x2 = xs[i+1];
                d = x1.distanceTo(x2);

                // acc: so far (without distance)
                distances.push({
                    'i1': i, 'i2': i+1,
                    'x1': x1, 'x2': x2,
                    'acc': xs_len, 'distance': d
                });

                xs_len += d
            }
            return {'length': xs_len, 'distances': distances};
        },

        // Calculate length (works for either points or latlngs)
        length: function(xs) {
            var xs_len = 0;
            for (var i = 0; i < xs.length - 1; i++) {
                xs_len += xs[i].distanceTo(xs[i+1]);
            }
            return xs_len;
        },

        distance: function (map, latlng1, latlng2) {
            return map.latLngToLayerPoint(latlng1).distanceTo(map.latLngToLayerPoint(latlng2));
        },

        distanceSegment: function (map, latlng, latlngA, latlngB) {
            var p = map.latLngToLayerPoint(latlng),
               p1 = map.latLngToLayerPoint(latlngA),
               p2 = map.latLngToLayerPoint(latlngB);
            return L.LineUtil.pointToSegmentDistance(p, p1, p2);
        },

        latlngOnSegment: function (map, latlng, latlngA, latlngB) {
            var p = map.latLngToLayerPoint(latlng),
               p1 = map.latLngToLayerPoint(latlngA),
               p2 = map.latLngToLayerPoint(latlngB);
               closest = L.LineUtil.closestPointOnSegment(p, p1, p2);
            return map.layerPointToLatLng(closest);
        },

        closestOnLine: function (map, latlng, linestring) {
            return self.closestOnLatLngs(map, latlng, linestring.getLatLngs());
        },

        closestOnLatLngs: function (map, latlng, lls) {
            // Iterate on line segments
            var segmentmindist = Number.MAX_VALUE,
                ll = null;
            // Keep the closest point of all segments
            for (var j = 0; j < lls.length - 1; j++) {
                var p1 = lls[j],
                    p2 = lls[j+1],
                    d = self.distanceSegment(map, latlng, p1, p2);
                if (d < segmentmindist) {
                    segmentmindist = d;
                    ll = self.latlngOnSegment(map, latlng, p1, p2);
                }
            }
            return ll;
        },

        closest: function (map, marker, snaplist, snap_distance) {
            var mindist = Number.MAX_VALUE,
                 chosen = null,
                 point = null;
            var n = snaplist.length;
            // /!\ Careful with size of this list, iterated at every marker move!
            if (n>1000) console.warn("Snap list is very big : " + n + " objects!");

            // Iterate the whole snaplist
            for (var i = 0; i < n ; i++) {
                var object = snaplist[i],
                    ll = null,
                    distance = Number.MAX_VALUE;
                if (object.getLatLng) {
                    // Single dimension, snap on points
                    ll = object.getLatLng();
                    distance = self.distance(map, marker.getLatLng(), ll);
                }
                else {
                    ll = L.GeomUtils.closestOnLine(map, marker.getLatLng(), object);
                    distance = L.GeomUtils.distance(map, marker.getLatLng(), ll);
                }
                // Keep the closest point of all objects
                if (distance < snap_distance && distance < mindist) {
                    mindist = distance;
                    chosen = object;
                    point = ll;
                }
            }
            // Try to snap on line points (extremities and middle points)
            if (chosen && chosen.getLatLngs) {
                var mindist = snap_distance,
                    linepoint = null;
                for (var i=0; i<chosen.getLatLngs().length; i++) {
                    var lp = chosen.getLatLngs()[i], 
                        distance = L.GeomUtils.distance(map, point, lp);
                    if (distance < mindist) {
                        linepoint = lp;
                        mindist = distance;
                    }
                }
                if (linepoint) point = linepoint;
            }
            return [chosen, point];
        },

        isBefore: function (polyline, other) {
            var lls = polyline.getLatLngs(),
               ll_p = lls[lls.length - 1];
            if (!other) return false;
            var lls = other.getLatLngs()
              , ll_a = lls[0];
            return ll_p.equals(ll_a);
        },

        isAfter: function (polyline, other) {
            var ll_p = polyline.getLatLngs()[0];
            if (!other) return false;
            var lls = other.getLatLngs()
              , ll_b = lls[lls.length - 1];
            return ll_p.equals(ll_b);
        },

        isStartAtEdges: function (polyline, other) {
            /** 
             * Returns true if the first point of the polyline
             * is equal to start or end of the other
             */
            var ll_p = polyline.getLatLngs()[0];
            if (!other) return false;

            var lls = other.getLatLngs()
              , ll_a = lls[0]
              , ll_b = lls[lls.length - 1];

            return ll_p.equals(ll_a) || ll_p.equals(ll_b);
        },

        lineReverse: function (line) {
            return L.polyline(line.getLatLngs().reverse());
        }
    };
})();
