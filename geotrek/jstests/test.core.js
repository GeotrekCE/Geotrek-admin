var assert = chai.assert;


describe('Shortest path', function() {

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

    /*
    Existing paths:
        1 <-[1]-> 2
        2 <-[2]-> 3

        4 <-[3]-> 5
    */
    it('It should return null if path inexistant', function(done) {
        // Both nodes id exist but no path should join them
        var from_nodes_id = [1], to_nodes_id = [5];
        var cpaths = Geotrek.Dijkstra.get_shortest_path_from_graph(
            simple_valid_jsongraph, from_nodes_id, to_nodes_id
        );
        assert.equal(cpaths, null);
        done();
    });


    it('It should work with single path', function(done) {
        var from_nodes_id = [4], to_nodes_id = [5];
        var cpaths = Geotrek.Dijkstra.get_shortest_path_from_graph(
            simple_valid_jsongraph, from_nodes_id, to_nodes_id
        );
        var path = cpaths.path;
        // Path should look like:
        // 4 -[3]-> 5
        assert.equal(path.length, 1, "Path has one edges");
        assert.equal(cpaths.weight, 15, "Weight should be equals to the weight of the edge 3");

        assert.equal(path[0].edge.id, 3);
        assert.equal(path[0].start, 4);
        assert.equal(path[0].end, 5);
        done();
    });


    it('It should work with two paths', function(done) {
        var from_nodes_id = [1], to_nodes_id = [3];
        var cpaths = Geotrek.Dijkstra.get_shortest_path_from_graph(
            simple_valid_jsongraph, from_nodes_id, to_nodes_id
        );
        var path = cpaths.path;
        // Path should look like:
        // 1 -[1]-> 2 -[2]-> 3

        assert.equal(path.length, 2, "Path has two edges");
        assert.equal(cpaths.weight, 5 + 10, "Weight should be equals to the sum of the edges 1 and 2 weights");

        assert.equal(path[0].edge.id, 1);
        assert.equal(path[0].start, 1);
        assert.equal(path[0].end, 2);

        assert.equal(path[1].edge.id, 2);
        assert.equal(path[1].end, 3);
        assert.equal(path[1].start, 2);
        done();
    });
});




describe('Topology helper', function() {

    /*

           40.0     +<---------+
                  6 |          | 7
           30.0     v----------+

           20.0     ^
                  3 |
                    |
           10.0     ^<---------+
                    |          |
                  2 |          | 1
                    |          |
                    |          |
            0.0     +----------+
                    |
                  4 |     5
          -10.0     v<---------+
                              10.0
    */
    var layer = new L.ObjectsLayer({
        type: "FeatureCollection",
        features: [
            {type: "Feature",
             geometry: {type: "LineString", coordinates: [[0,0], [10,0], [10,10], [0,10]]},
             properties: {pk: 1}},
            {type: "Feature",
             geometry: {type: "LineString", coordinates: [[0,0], [0,10]]},
             properties: {pk: 2}},
            {type: "Feature",
             geometry: {type: "LineString", coordinates: [[0,10], [0,20]]},
             properties: {pk: 3}},
            {type: "Feature",
             geometry: {type: "LineString", coordinates: [[0,0], [0,-10]]},
             properties: {pk: 4}},
            {type: "Feature",
             geometry: {type: "LineString", coordinates: [[10,-10], [0,-10]]},
             properties: {pk: 5}},
            {type: "Feature",
             geometry: {type: "LineString", coordinates: [[0,40], [0,30]]},
             properties: {pk: 6}},
            {type: "Feature",
             geometry: {type: "LineString", coordinates: [[0,30], [10,30], [10,40], [0, 40]]},
             properties: {pk: 7}}
        ]
    }).addTo(map);

    function idToLayer(pk) { return layer.getLayer(pk); }

    function __inputData(from, to, ids) {
        /**
         * As returned by MultipathControl
         */
        var edges = $.map(ids, function (id) { return {id: id}; });
        return {
            computed_paths: [{
                from_pop: {ll: from},
                to_pop: {ll: to}
            }],
            new_edges: [edges]
        };
    }


    it('It should safely return if computed path is null', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(function idToLayer(){}, {});
        assert.deepEqual(topo, { layer: null, serialized: null });
        done();
    });


    it('It should work if start and end are on same path', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([0, 5]), L.latLng([0, 10]), [[1]]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.16751709787175395, 0.33503419574350934]
            },
            paths: [1]
        });
        done();
    });


    it('It should work if start and end are on continous paths', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([5, 0]), L.latLng([15, 0]), [2, 3]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.4999999999999995,1],   // [0.5, 1.0]
                "1": [0, 0.5000000000000009]   // [0.0, 0.5]
            },
            paths: [2,3]
        });
        done();
    });


    it('It should work if paths have opposite ways', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([0, 5]), L.latLng([5, 0]), [1, 2]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.16751709787175395, 0],
                "1": [0, 0.4999999999999995]
            },
            paths: [1, 2]
        });
        done();
    });


    it('It should go through extremities, even if paths have opposite ways', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([10, 3]), L.latLng([7, 0]), [1, 2]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.9010250453729739, 1.0],
                "1": [1.0, 0.6999999999999996]
            },
            paths: [1, 2]
        });
        done();
    });


    it('It should go through extremities only if it is the shortest way', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([5, 10]), L.latLng([2, 0]), [1, 2]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.5025512936152635, 0.0],
                "1": [0.0, 0.20000000000000026]
            },
            paths: [1, 2]
        });
        done();
    });


    it('It should go through extremities, even if paths have opposite ways 2', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([40, 3]), L.latLng([39, 0]), [7, 6]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.9127652411579061, 1.0],
                "1": [0.0, 0.10000000000000071]
            },
            paths: [7, 6]
        });
        done();
    });


    it('It should go through extremities only if it is the shortest way 2', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([35, 10]), L.latLng([32, 0]), [7, 6]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.5190218601242491, 0.0],
                "1": [1, 0.8000000000000006]
            },
            paths: [7, 6]
        });
        done();
    });


    it('It should work if middle paths have opposite ways', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([-5, 0]), L.latLng([15, 0]), [4, 2, 3]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.4999999999999981, 0],
                "1": [0, 1],
                "2": [0, 0.5000000000000009]
            },
            paths: [4, 2, 3]
        });
        done();
    });



    it('It should not cover start completely even if paths have opposite ways', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([-1.0, 0.0]), L.latLng([-10, 7.5]), [4, 5]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.10000000000000141, 1],
                "1": [1, 0.2500089985334514],
            },
            paths: [4, 5]
        });
        done();
    });


    it('It should work if loop with two paths same way', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([1, 0]), L.latLng([9, 0]), [2, 1, 2]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.10000000000000013, 0],
                "1": [0, 1],
                "2": [1, 0.8999999999999987],
            },
            paths: [2, 1, 2]
        });
        done();
    });


    it('It should work if loop with two paths opposite way', function(done) {
        var topo = Geotrek.TopologyHelper.buildTopologyFromComputedPath(idToLayer,
                        __inputData(L.latLng([31, 0]), L.latLng([39, 0]), [6, 7, 6]));

        // One sub-topology
        assert.equal(topo.serialized.length, 1);

        assert.deepEqual(topo.serialized[0], {
            offset: 0,
            positions: {
                "0": [0.8999999999999992, 1],
                "1": [0, 1],
                "2": [0, 0.10000000000000071],
            },
            paths: [6, 7, 6]
        });
        done();
    });
});
