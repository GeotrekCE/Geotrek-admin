var Caminae = Caminae || {};

Caminae.Dijkstra = (function() {

    // TODO: doc
    function get_shortest_path_from_graph(graph, from_ids, to_ids, exclude_from_to) {
        // coerce int to string
        from_ids = $.map(from_ids, function(k) { return '' + k; });
        to_ids = $.map(to_ids, function(k) { return '' + k; });

        var graph_nodes = graph.nodes;
        var graph_edges = graph.edges;

        function getPairWeightNode(node_id) {
            var l = [];
            $.each(graph_nodes[node_id], function(k, v) {
                // Warning - weight is in fact edge.length in our data
                l.push({'node_id': k, 'weight': graph_edges[v].length});
            });
            return l;
        }

        function is_source(node_id) {
            return (from_ids.indexOf(node_id) != -1)
        }
        function is_destination(node_id) {
            return (to_ids.indexOf(node_id) != -1)
        }

        var djk = {};

        // weight is smallest so far: take it whatever happens
        from_ids.forEach(function(node_id) {
            djk[node_id] = {'prev': null, 'node': node_id, 'weight': 0, 'visited': false};
        });

        // return the ID of an unvisited node that has the less weight (less djk weight)
        // FIXME: performance -> shoud not contain visited node, should be sorted by weight
        function djk_get_next_id () {
            var nodes_id = Object.keys(djk);
            var mini_weight = Number.MAX_VALUE;
            var mini_id = null;
            var node_djk = null;
            var weight = null;

            for (var k = 0; k < nodes_id.length; k++) {
                var node_id = nodes_id[k];
                node_djk = djk[node_id];
                weight = node_djk.weight;

                // if already visited - skip
                if (node_djk.visited === true)
                    continue;

                // Weight can't get lower - take it
                if (weight == 0)
                    return node_id;

                // Otherwise try to find the minimum
                if (weight < mini_weight) {
                    mini_id = node_id;
                    mini_weight = weight;
                }
            }
            return mini_id;
        }


        var djk_current_node, current_node_id;

        while (true) {
            // Get the next node to visit
            djk_current_node = djk_get_next_id();

            // Last node exhausted - we didn't find a path
            if (djk_current_node === null)
                return null;

            // The node exist
            current_djk_node = djk[djk_current_node];
            // Mark as visited (won't be chosen)
            current_djk_node.visited = true;
            // we could del it out of djk

            current_node_id = current_djk_node.node;

            // Last point
            if (is_destination(current_node_id))
                break;

            // refactor to get next
            var pairs_weight_node = getPairWeightNode(current_node_id);


            // if current_djk_node.weight > ... BREAK
            for (var i = 0; i < pairs_weight_node.length; i++) {
                var edge_weight = pairs_weight_node[i].weight;
                var next_node_id = pairs_weight_node[i].node_id;

                var next_weight = current_djk_node.weight + edge_weight;

                var djk_next_node = djk[next_node_id];

                // push new node or update it
                if (djk_next_node) {
                    // update node ?
                    if (djk_next_node.visited === true)
                        continue;

                    if (djk_next_node.weight > next_weight)
                        continue;

                    djk_next_node.weight = next_weight;
                    djk_next_node.prev = current_djk_node;

                } else {
                    // push node
                    djk[next_node_id] = {
                          'prev': current_djk_node
                        , 'node': next_node_id
                        , 'weight': next_weight
                        , 'visited': false
                    };

                }
            }
        };


        var path = [];
        // Extract path
        // current_djk_node is the destination
        var final_weight = current_djk_node.weight;
        var tmp = current_djk_node;
        while (!is_source(tmp.node)) {
            path.push(tmp.node);
            tmp = tmp.prev;
        }


        if (exclude_from_to) {
            path.shift(); // remove last node
        } else {
            path.push(tmp.node); // push first node
        }

        // miss first and last step
        path.reverse();

        var i, j, full_path = [];
        for (i = 0; i < path.length - 1; i++) {
            var node_1 = path[i], node_2 = path[i+1];
            var edge = graph_edges[graph_nodes[node_1][node_2]];

            // start end and edge are just ids
            full_path.push({
                'start': node_1,
                'end': node_2,
                'edge': edge,
                'weight': edge.length
            });
        }

        return {
              'path': full_path
            , 'weight': final_weight
        };

    };

    return {
        'get_shortest_path_from_graph': get_shortest_path_from_graph
    };
})();

