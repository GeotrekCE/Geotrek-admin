from django.test import TestCase
from django.contrib.gis.geos import LineString

from caminae.core.factories import PathFactory
from caminae.core.graph import graph_of_qs
from caminae.core.models import Path


class SimpleGraph(TestCase):

    def test_python_graph_from_path(self):
        p_1_1 = (1., 1., 0.)
        p_2_2 = (2., 2., 0.)
        p_3_3 = (3., 3., 0.)
        p_4_4 = (4., 4., 0.)
        p_5_5 = (5., 5., 0.)
        p_6_6 = (6., 6., 0.)

        def gen_random_point():
            """Return unique (non-conflicting) point"""
            return ((x + 0., x + 1., 0.) for x in xrange(10, 100))

        r_point = gen_random_point().next

        e_1_2 = PathFactory(geom=LineString(p_1_1, r_point(), p_2_2))
        e_2_3 = PathFactory(geom=LineString(p_2_2, r_point(), p_3_3))

        # Non connex
        e_4_5 = PathFactory(geom=LineString(p_4_4, r_point(), p_5_5))

        # Add an edge with the p_1_1 in its center
        # e_5_1_6 = PathFactory(geom=LineString(p_5_5, r_point(), p_1_1, r_point(), p_6_6))

        graph = {
            p_1_1: {
                p_2_2: e_1_2,
            },
            p_2_2: {
                p_1_1: e_1_2,
                p_3_3: e_2_3,
            },
            p_3_3: {
                p_2_2: e_2_3,
            },
            # Non connex
            p_4_4: { p_5_5: e_4_5, },
            p_5_5: { p_4_4: e_4_5, },
        }

        computed_graph = graph_of_qs(Path.objects.all())

        self.assertDictEqual(computed_graph, graph)



