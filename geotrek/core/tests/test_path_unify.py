# -*- coding: utf-8 -*-

from django.contrib.gis.geos import LineString, Point
from django.test import TestCase

from geotrek.core.factories import PathFactory, TopologyFactory, \
    PathAggregationFactory
from geotrek.core.models import PathAggregation


class UnifyPathTest(TestCase):
    def test_path_unify(self):
        """
          A         B   C         D     A                  D
          |---------| + |---------| --> |------------------|

          Test five cases : 1 - A match with C : unification D-C-A-B
                            2 - A match with D : unification C-D-A-B
                            3 - B match with C : unification A-B-C-D
                            4 - B match with D : unification A-B-D-C
                            5 - no match       : no unification
        """
        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((4, 0), (8, 0)))

        self.assertEqual(path_AB.unify_path(path_CD), True)
        self.assertEqual(path_AB.geom, LineString((0, 0), (4, 0), (8, 0)))

        path_AB = PathFactory.create(name="path_AB", geom=LineString((4, 0), (0, 0)))
        path_CD = PathFactory.create(name="path_CD", geom=LineString((4, 0), (8, 0)))

        self.assertEqual(path_AB.unify_path(path_CD), True)
        self.assertEqual(path_AB.geom, LineString((0, 0), (4, 0), (8, 0)))

        path_AB = PathFactory.create(name="path_AB", geom=LineString((4, 0), (0, 0)))
        path_CD = PathFactory.create(name="path_CD", geom=LineString((8, 0), (4, 0)))

        self.assertEqual(path_AB.unify_path(path_CD), True)
        self.assertEqual(path_AB.geom, LineString((0, 0), (4, 0), (8, 0)))

        path_AB = PathFactory.create(name="path_AB", geom=LineString((0, 0), (4, 0)))
        path_CD = PathFactory.create(name="path_CD", geom=LineString((8, 0), (4, 0)))

        self.assertEqual(path_AB.unify_path(path_CD), True)
        self.assertEqual(path_AB.geom, LineString((0, 0), (4, 0), (8, 0)))

        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((10, 0), (18, 0)))

        self.assertEqual(path_AB.unify_path(path_CD), False)

    def test_recompute_pk_no_reverse(self):
        """
        A---------------B + C-------------------D         A----------------------------------D
          |        |          |--|           |         =>   |       |        |--|           |
          E1 (0.2) |          E3 (0.2, 0.3)  |             E1 (0.1) |        E3 (0.6, 0.65) E4 (0.9)
                   E2 (0.6)                  E4 (0.8)               E2 (0.3)

        In case of AB == CD, matching B and C
        """
        path_1 = PathFactory.create(name="PATH_1", geom=LineString((0, 1), (10, 1)))
        path_2 = PathFactory.create(name="PATH_2", geom=LineString((10, 1), (20, 1)))

        e1 = TopologyFactory.create(geom=Point(2, 2))
        a1 = PathAggregationFactory.create(path=path_1, topo_object=e1)

        e2 = TopologyFactory.create(geom=Point(6, 1))
        a2 = PathAggregationFactory.create(path=path_1, topo_object=e2)

        e3 = TopologyFactory.create(geom=LineString((2, 1), (3, 1),))
        a3 = PathAggregationFactory.create(path=path_2, topo_object=e3)
        e4 = TopologyFactory.create(geom=Point(8, 2))
        a4 = PathAggregationFactory.create(path=path_2, topo_object=e4)

        path_1_original_length = path_1.length
        path_2_original_length = path_2.length
        path_1.unify_path(path_2)

        self.assertEqual(path_1.geom, LineString((0, 1), (10, 1), (20, 1)))

        # reload updated objects
        a1_updated = PathAggregation.objects.get(pk=a1.pk)
        a2_updated = PathAggregation.objects.get(pk=a2.pk)
        a3_updated = PathAggregation.objects.get(pk=a3.pk)
        a4_updated = PathAggregation.objects.get(pk=a4.pk)

        # test pk recompute on path_1 : new pk = old pk * old_path_1_length / new_path_1_length
        self.assertEqual(a1_updated.start_position, a1.start_position * (path_1_original_length / path_1.length))
        self.assertEqual(a1_updated.end_position, a1.end_position * (path_1_original_length / path_1.length))

        self.assertEqual(a2_updated.start_position, a2.start_position * (path_1_original_length / path_1.length))
        self.assertEqual(a2_updated.end_position, a1.end_position * (path_1_original_length / path_1.length))

        # test pk recompute on path_2 : new pk = old pk * old_path_2_length / new_path_1_length + old_path_1_length / new_path_1_length
        self.assertEqual(a3_updated.start_position, a3.start_position * (path_2_original_length / path_1.length) + path_1_original_length / path_1.length)
        self.assertEqual(a3_updated.start_position, a3.start_position * (path_2_original_length / path_1.length) + path_1_original_length / path_1.length)

        self.assertEqual(a4_updated.start_position, a4.start_position * (path_2_original_length / path_1.length) + path_1_original_length / path_1.length)
        self.assertEqual(a4_updated.start_position, a4.start_position * (path_2_original_length / path_1.length) + path_1_original_length / path_1.length)
