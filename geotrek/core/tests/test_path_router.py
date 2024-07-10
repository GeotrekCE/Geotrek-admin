from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString
from django.core.cache import caches
from django.test import TestCase

from geotrek.core.path_router import PathRouter
from geotrek.core.models import Path
from geotrek.core.tests.factories import PathFactory


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PathRouterGraphGenerationTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path_router = PathRouter()

    def test_python_graph_from_path(self):
        p_1_1 = (1., 1.)
        p_2_2 = (2., 2.)
        p_3_3 = (3., 3.)
        p_4_4 = (4., 4.)
        p_5_5 = (5., 5.)

        def gen_random_point():
            """Return unique (non-conflicting) point"""
            return ((0., x + 1.) for x in range(10, 100))

        r_point = gen_random_point().__next__

        e_1_2 = PathFactory(geom=LineString(p_1_1, r_point(), p_2_2))
        e_2_3 = PathFactory(geom=LineString(p_2_2, r_point(), p_3_3))

        # Non connex
        e_4_5 = PathFactory(geom=LineString(p_4_4, r_point(), p_5_5))

        graph = {
            'nodes': {
                1: {2: e_1_2.pk},
                2: {1: e_1_2.pk, 3: e_2_3.pk},
                3: {2: e_2_3.pk},
                4: {5: e_4_5.pk},
                5: {4: e_4_5.pk}
            },
            'edges': {
                e_1_2.pk: {'nodes_id': [1, 2], 'length': e_1_2.length, 'id': e_1_2.pk},
                e_2_3.pk: {'nodes_id': [2, 3], 'length': e_2_3.length, 'id': e_2_3.pk},
                e_4_5.pk: {'nodes_id': [4, 5], 'length': e_4_5.length, 'id': e_4_5.pk}
            }
        }

        graph = self.path_router.graph_edges_nodes_of_qs(Path.objects.order_by('id'))
        self.assertDictEqual(graph, graph)

    def test_json_graph_empty(self):
        graph = self.path_router.graph_edges_nodes_of_qs(Path.objects.all())
        self.assertDictEqual({'edges': {}, 'nodes': {}}, graph)

    def test_json_graph_simple(self):
        path = PathFactory(geom=LineString((0, 0), (1, 1)))
        graph = self.path_router.graph_edges_nodes_of_qs(Path.objects.all())
        length = graph['edges'][path.pk].pop('length')
        self.assertDictEqual({'edges': {path.pk: {'id': path.pk, 'nodes_id': [1, 2]}},
                              'nodes': {1: {2: path.pk}, 2: {1: path.pk}}}, graph)
        self.assertAlmostEqual(length, 1.4142135623731)

    def test_json_graph_simple_cached(self):
        path = PathFactory(geom=LineString((0, 0), (1, 1)))
        graph = self.path_router.graph_edges_nodes_of_qs(Path.objects.all())

        length = graph['edges'][path.pk].pop('length')
        self.assertDictEqual({'edges': {path.pk: {'id': path.pk, 'nodes_id': [1, 2]}},
                              'nodes': {1: {2: path.pk}, 2: {1: path.pk}}}, graph)
        self.assertAlmostEqual(length, 1.4142135623731)

    def test_get_graph_from_cache(self):
        PathFactory(geom=LineString((0, 0), (1, 1)))
        cache = caches['fat']
        mock_graph = {
            'nodes': {1: {2: 1}, 2: {1: 1}, 3: {4: 2}, 4: {3: 2}},
            'edges': {
                1: {'id': 1, 'length': 1.4, 'nodes_id': [1, 2]},
                2: {'id': 2, 'length': 1.4, 'nodes_id': [3, 4]}
            }
        }
        cache.set('path_graph', (Path.no_draft_latest_updated(), mock_graph))
        path_router = PathRouter()
        self.assertEqual(path_router.nodes, mock_graph['nodes'])
        self.assertEqual(path_router.edges, mock_graph['edges'])


class PathRouterTest(TestCase):
    def test_set_cs_graph_set_cache(self):
        PathFactory(geom=LineString((0, 0), (1, 1)))
        PathFactory(geom=LineString((2, 2), (3, 3)))
        cache = caches['fat']
        cached_data_before = cache.get('dijkstra_matrix')
        self.assertIsNone(cached_data_before)
        PathRouter()
        cached_data_after = cache.get('dijkstra_matrix')
        self.assertIsNotNone(cached_data_after)

    def test_set_cs_graph_get_from_cache(self):
        PathFactory(geom=LineString((0, 0), (1, 1)))
        PathFactory(geom=LineString((2, 2), (3, 3)))
        cache = caches['fat']
        cache.set('dijkstra_matrix', (Path.no_draft_latest_updated(), 'mock cache data'))
        path_router = PathRouter()
        self.assertEqual(path_router.dijk_matrix, 'mock cache data')

    def test_get_edge_weight_incorrect_edge_id(self):
        path = PathFactory(geom=LineString((0, 0), (1, 1)))
        path_router = PathRouter()
        edge_weight = path_router.get_edge_weight(path.pk + 1)
        self.assertIsNone(edge_weight)

    def test_get_shortest_path_incorrect_node_id(self):
        PathFactory(geom=LineString((0, 0), (1, 1)))
        path_router = PathRouter()
        last_node_id = list(path_router.nodes.keys())[-1]
        route = path_router.get_shortest_path(last_node_id, last_node_id + 1)
        self.assertListEqual(route, [])

    def test_get_edge_id_by_nodes_no_linking_edge(self):
        path1 = PathFactory(geom=LineString((0, 0), (1, 1)))
        path2 = PathFactory(geom=LineString((2, 2), (3, 3)))
        path_router = PathRouter()
        first_edge = path_router.edges[path1.pk]
        first_node = path_router.nodes[first_edge['nodes_id'][0]]
        last_edge = path_router.edges[path2.pk]
        last_node = path_router.nodes[last_edge['nodes_id'][1]]
        edge_id = path_router.get_edge_id_by_nodes(first_node, last_node)
        self.assertIsNone(edge_id)
