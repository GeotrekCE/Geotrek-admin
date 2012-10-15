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
            'latlngs': latlngs,
            'positions': positions,
            'is_single_path': single_path
        };
    }

    var getNextId = (function() {
        var next_id = 100000;
        return function() {
            return next_id++;
        };
    })();

    // pol: point on polyline
    function PointOnPolyline(marker) {
        this.marker = marker;
        // if valid
        this.ll = null;
        this.polyline = null;
        this.length = null;
        this.percent_distance = null;
        this._activated = false;

        this.events = L.Util.extend({}, L.Mixin.Events);

        this.markerEvents = {
            'move': function onMove (e) {
                var marker = e.target;
                if (marker.snap) marker.fire('snap', {object: marker.snap, location: marker.getLatLng()});
            },
            'snap': function onSnap(e) {
                this.ll = e.location;
                this.polyline = e.object;

                this.length = MapEntity.Utils.length(this.polyline.getLatLngs());
                this.percent_distance = MapEntity.Utils.getPercentageDistanceFromPolyline(this.ll, this.polyline).distance;

                this.events.fire('valid'); // self
            },
            'unsnap': function onUnsnap(e) {
                this.ll = null;
                this.polyline = null;
                this.events.fire('invalid');
            }
        };
    };

    PointOnPolyline.prototype.activated = function() {
        return this._activated;
    };

    PointOnPolyline.prototype.toggleActivate = function(activate) {
        activate = activate === undefined ? true : activate;

        if ((activate && this._activated) || (!activate && !this._activated))
            return;

        this._activated = activate;

        var method = activate ? 'on' : 'off';

        var marker = this.marker
          , markerEvents = this.markerEvents;

        marker[method]('move', markerEvents.move, this);
        marker[method]('snap', markerEvents.snap, this);
        marker[method]('unsnap', markerEvents.unsnap, this);
    };

    PointOnPolyline.prototype.isValid = function(graph) {
        return (this.ll && this.polyline);
    };

    // Alter the graph: adding two edges and one node (the polyline gets break in two parts by the point)
    // The polyline MUST be an edge of the graph.
    PointOnPolyline.prototype.addToGraph = function(graph) {
        if (! this.isValid())
            return null;

        var self = this;

        // var edge_id = this.layerToId(layer);
        var edge = graph.edges[this.polyline.properties.pk]
          , first_node_id = edge.nodes_id[0]
          , last_node_id = edge.nodes_id[1];

        // To which nodes dist start_point/end_point corresponds ?
        // The edge.nodes_id are ordered, it corresponds to polylines: coords[0] and coords[coords.length - 1]
        var dist_start_point = this.percent_distance * length
          , dist_end_point = (1 - this.percent_distance) * length
        ;

        var new_node_id = getNextId();

        var edge1 = {'id': getNextId(), 'length': dist_start_point, 'nodes_id': [first_node_id, new_node_id] };
        var edge2 = {'id': getNextId(), 'length': dist_end_point, 'nodes_id': [new_node_id, last_node_id]};

        var first_node = {}, last_node = {}, new_node = {};
        first_node[new_node_id] = new_node[first_node_id] = edge1.id;
        last_node[new_node_id] = new_node[last_node_id] = edge2.id;

        // <Alter Graph>
        var new_edges = {};
        new_edges[edge1.id] = graph.edges[edge1.id] = edge1;
        new_edges[edge2.id] = graph.edges[edge2.id] = edge2;

        graph.nodes[new_node_id] = new_node;
        $.extend(graph.nodes[first_node_id], first_node);
        $.extend(graph.nodes[last_node_id], last_node);
        // </Alter Graph>

        function rmFromGraph() {
            delete graph.edges[edge1.id];
            delete graph.edges[edge2.id];

            delete graph.nodes[new_node_id];
            delete graph.nodes[first_node_id][new_node_id];
            delete graph.nodes[last_node_id][new_node_id];
        }

        return {
            self: self,
            new_node_id: new_node_id,
            new_edges: new_edges,
            dist_start_point: dist_start_point,
            dist_end_point: dist_end_point,
            initial_edge: edge,
            rmFromGraph: rmFromGraph
        };
    };


    return {
        buildTopologyGeom: buildTopologyGeom,
        PointOnPolyline: PointOnPolyline
    };
})();
