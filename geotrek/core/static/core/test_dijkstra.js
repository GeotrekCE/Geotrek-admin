(function() {
// require dijkstra.js


/*
Existing paths:
    1 <-[1]-> 2
    2 <-[2]-> 3

    4 <-[3]-> 5
*/

var simple_valid_jsongraph = {
    "nodes": {
        "1": {
            "2": 1
        },
        "2": {
            "1": 1,
            "3": 2
        },
        "3": {
            "2": 2
        },
        "4": {
            "5": 3
        },
        "5": {
            "4": 3
        }
    },
    "edges": {
        "1": {
            "id": 1,
            "length": 5,
            "nodes_id": [
                1,
                2
            ]
        },
        "2": {
            "id": 2,
            "length": 10,
            "nodes_id": [
                2,
                3
            ]
        },
        "3": {
            "id": 3,
            "length": 15,
            "nodes_id": [
                4,
                5
            ]
        }
    }
};

test('Path unexistent path', function() {
    // Both nodes id exist but no path should join them
    var from_nodes_id = [1], to_nodes_id = [5];
    var cpaths = Geotrek.Dijkstra.get_shortest_path_from_graph(
        simple_valid_jsongraph, from_nodes_id, to_nodes_id
    );

    strictEqual(cpaths, null);
});


test('Path with 1 edge', function() {
    // Both nodes id exist but no path should join them
    var from_nodes_id = [4], to_nodes_id = [5];
    var cpaths = Geotrek.Dijkstra.get_shortest_path_from_graph(
        simple_valid_jsongraph, from_nodes_id, to_nodes_id
    );

    var path = cpaths.path;

    // Path should look like:
    // 4 -[3]-> 5

    equal(path.length, 1, "Path has on edges");
    equal(cpaths.weight, 15, "Weight should be equals to the weight of the edge 3");

    equal(path[0].edge.id, 3);
    equal(path[0].start, 4);
    equal(path[0].end, 5);

});

test('Path with 2 edges', function() {

    // Given the graph, search the shortest path from node id 1 to node id 3
    var from_nodes_id = [1], to_nodes_id = [3];
    var cpaths = Geotrek.Dijkstra.get_shortest_path_from_graph(
        simple_valid_jsongraph, from_nodes_id, to_nodes_id
    );

    var path = cpaths.path;

    // Path should look like:
    // 1 -[1]-> 2 -[2]-> 3

    equal(path.length, 2, "Path has two edges");
    equal(cpaths.weight, 5 + 10, "Weight should be equals to the sum of the edges 1 and 2 weights");

    equal(path[0].edge.id, 1);
    equal(path[0].start, 1);
    equal(path[0].end, 2);

    equal(path[1].edge.id, 2);
    equal(path[1].end, 3);
    equal(path[1].start, 2);

});

})();
