import json

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.gis.geos import LineString
from django.core.urlresolvers import reverse

from geotrek.core.factories import PathFactory
from geotrek.core.graph import graph_edges_nodes_of_qs
from geotrek.core.models import Path


class SimpleGraph(TestCase):

    def setUp(self):
        user = User.objects.create_user('homer', 'h@s.com', 'dooh')
        success = self.client.login(username=user.username, password='dooh')
        self.assertTrue(success)
        self.url = reverse('core:path_json_graph')

    def test_python_graph_from_path(self):
        p_1_1 = (1., 1.)
        p_2_2 = (2., 2.)
        p_3_3 = (3., 3.)
        p_4_4 = (4., 4.)
        p_5_5 = (5., 5.)

        def gen_random_point():
            """Return unique (non-conflicting) point"""
            return ((0., x + 1.) for x in xrange(10, 100))

        r_point = gen_random_point().next

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

        computed_graph = graph_edges_nodes_of_qs(Path.objects.order_by('id'))
        self.assertDictEqual(computed_graph, graph)

    def test_json_graph_empty(self):

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        graph = json.loads(response.content)
        self.assertDictEqual({'edges': {}, 'nodes': {}}, graph)

    def test_json_graph_simple(self):
        path = PathFactory(geom=LineString((0, 0), (1, 1)))
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        graph = json.loads(response.content)
        self.assertDictEqual({'edges': {str(path.pk): {u'id': path.pk, u'length': 1.4142135623731, u'nodes_id': [1, 2]}},
                              'nodes': {u'1': {u'2': path.pk}, u'2': {u'1': path.pk}}}, graph)

    def test_json_graph_headers(self):
        """
        Last modified depends on
        """
        PathFactory(geom=LineString((0, 0), (1, 1)))
        response = self.client.get(self.url)
        last_modified = response['Last-Modified']
        expires = response['Expires']
        self.assertNotEqual(expires, None)
        self.assertEqual(expires, last_modified)
