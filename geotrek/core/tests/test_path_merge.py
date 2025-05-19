from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.test import TestCase
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory

from geotrek.core.models import PathAggregation, Topology
from geotrek.core.tests.factories import (
    PathAggregationFactory,
    PathFactory,
    TopologyFactory,
)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class MergePathTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_path_merge_without_snap(self):
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
        original_AB_length = path_AB.length
        original_CD_length = path_CD.length

        self.assertEqual(path_AB.merge_path(path_CD), True)

        self.assertEqual(
            path_AB.geom,
            LineString((0.0, 0.0), (4.0, 0.0), (8.0, 0.0), srid=settings.SRID),
        )
        self.assertEqual(path_AB.length, original_AB_length + original_CD_length)

        path_AB.delete()
        path_CD.delete()

        path_AB = PathFactory.create(name="path_AB", geom=LineString((4, 0), (0, 0)))
        path_CD = PathFactory.create(name="path_CD", geom=LineString((4, 0), (8, 0)))
        original_AB_length = path_AB.length
        original_CD_length = path_CD.length

        self.assertEqual(path_AB.merge_path(path_CD), True)
        self.assertEqual(
            path_AB.geom, LineString((0, 0), (4, 0), (8, 0), srid=settings.SRID)
        )
        self.assertEqual(path_AB.length, original_AB_length + original_CD_length)

        path_AB.delete()
        path_CD.delete()

        path_AB = PathFactory.create(name="path_AB", geom=LineString((4, 0), (0, 0)))
        path_CD = PathFactory.create(name="path_CD", geom=LineString((8, 0), (4, 0)))
        original_AB_length = path_AB.length
        original_CD_length = path_CD.length

        self.assertEqual(path_AB.merge_path(path_CD), True)
        self.assertEqual(
            path_AB.geom, LineString((0, 0), (4, 0), (8, 0), srid=settings.SRID)
        )
        self.assertEqual(path_AB.length, original_AB_length + original_CD_length)

        path_AB.delete()
        path_CD.delete()

        path_AB = PathFactory.create(name="path_AB", geom=LineString((0, 0), (4, 0)))
        path_CD = PathFactory.create(name="path_CD", geom=LineString((8, 0), (4, 0)))
        original_AB_length = path_AB.length
        original_CD_length = path_CD.length

        self.assertEqual(path_AB.merge_path(path_CD), True)
        self.assertEqual(
            path_AB.geom, LineString((0, 0), (4, 0), (8, 0), srid=settings.SRID)
        )
        self.assertEqual(path_AB.length, original_AB_length + original_CD_length)

        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((50, 0), (100, 0)))
        original_AB_length = path_AB.length

        self.assertEqual(path_AB.merge_path(path_CD), False)
        self.assertEqual(path_AB.length, original_AB_length)

    def test_path_merge_with_snap(self):
        """
        A         B   C         D     A                  D
        |---------| + |---------| --> |------------------|

        Test five cases : 1 - A match with C : unification D-C-A-B
                          2 - A match with D : unification C-D-A-B
                          3 - B match with C : unification A-B-C-D
                          4 - B match with D : unification A-B-D-C
                          5 - no match       : no unification
        """
        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((0, 0), (15, 0)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((16, 0), (30, 0)))

        self.assertEqual(path_AB.merge_path(path_CD), True)
        self.assertEqual(
            path_AB.geom,
            LineString((0, 0), (15, 0), (16, 0), (30, 0), srid=settings.SRID),
        )

        path_AB.delete()
        path_CD.delete()

        path_AB = PathFactory.create(name="path_AB", geom=LineString((15, 0), (0, 0)))
        path_CD = PathFactory.create(name="path_CD", geom=LineString((16, 0), (30, 0)))

        self.assertEqual(path_AB.merge_path(path_CD), True)
        self.assertEqual(
            path_AB.geom,
            LineString((0, 0), (15, 0), (16, 0), (30, 0), srid=settings.SRID),
        )

        path_AB.delete()
        path_CD.delete()

        path_AB = PathFactory.create(name="path_AB", geom=LineString((15, 0), (0, 0)))
        path_CD = PathFactory.create(name="path_CD", geom=LineString((30, 0), (16, 0)))

        self.assertEqual(path_AB.merge_path(path_CD), True)
        self.assertEqual(
            path_AB.geom,
            LineString((0, 0), (15, 0), (16, 0), (30, 0), srid=settings.SRID),
        )

        path_AB.delete()
        path_CD.delete()

        path_AB = PathFactory.create(name="path_AB", geom=LineString((0, 0), (15, 0)))
        path_CD = PathFactory.create(name="path_CD", geom=LineString((30, 0), (16, 0)))

        self.assertEqual(path_AB.merge_path(path_CD), True)
        self.assertEqual(
            path_AB.geom,
            LineString((0, 0), (15, 0), (16, 0), (30, 0), srid=settings.SRID),
        )

        path_AB.delete()
        path_CD.delete()

        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((0, 0), (5, 0)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((50, 0), (100, 0)))

        self.assertEqual(path_AB.merge_path(path_CD), False)

    def test_path_merge_with_other_path_next_ws(self):
        """
                          F
                          |
                          |
                          E
        A---------------B + C-------------------D

        Do not merge !
        """
        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((0, 1), (10, 1)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((10, 1), (20, 1)))
        PathFactory.create(name="PATH_EF", geom=LineString((10, 1), (10, 5)))
        self.assertEqual(path_AB.merge_path(path_CD), 2)

    def test_recompute_pk_no_reverse(self):
        """
        A---------------B + C-------------------D         A----------------BC----------------D
          |        |          |--|           |         =>   |       |        |--|           |
          E1 (0.2) |          E3 (0.2, 0.3)  |             E1 (0.1) |        E3 (0.6, 0.65) E4 (0.9)
                   E2 (0.6)                  E4 (0.8)               E2 (0.3)

        In case of AB == CD, matching B and C
        """
        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((0, 1), (10, 1)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((10, 1), (20, 1)))

        e1 = TopologyFactory.create(geom=Point(2, 2))
        a1 = PathAggregationFactory.create(path=path_AB, topo_object=e1)

        e2 = TopologyFactory.create(geom=Point(6, 1))
        a2 = PathAggregationFactory.create(path=path_AB, topo_object=e2)

        e3 = TopologyFactory.create(
            geom=LineString(
                (2, 1),
                (3, 1),
            )
        )
        a3 = PathAggregationFactory.create(path=path_CD, topo_object=e3)
        e4 = TopologyFactory.create(geom=Point(8, 2))
        a4 = PathAggregationFactory.create(path=path_CD, topo_object=e4)

        path_AB_original_length = path_AB.length
        path_CD_original_length = path_CD.length
        path_AB.merge_path(path_CD)

        self.assertEqual(
            path_AB.geom, LineString((0, 1), (10, 1), (20, 1), srid=settings.SRID)
        )

        # reload updated objects
        a1_updated = PathAggregation.objects.get(pk=a1.pk)
        a2_updated = PathAggregation.objects.get(pk=a2.pk)
        a3_updated = PathAggregation.objects.get(pk=a3.pk)
        a4_updated = PathAggregation.objects.get(pk=a4.pk)

        # test pk recompute on path_1 : new pk = old pk * old_path_1_length / new_path_1_length
        self.assertEqual(
            a1_updated.start_position,
            a1.start_position * (path_AB_original_length / path_AB.length),
        )
        self.assertEqual(
            a1_updated.end_position,
            a1.end_position * (path_AB_original_length / path_AB.length),
        )

        self.assertEqual(
            a2_updated.start_position,
            a2.start_position * (path_AB_original_length / path_AB.length),
        )
        self.assertEqual(
            a2_updated.end_position,
            a1.end_position * (path_AB_original_length / path_AB.length),
        )

        # test pk recompute on path_2 : new pk = old pk * old_path_2_length / new_path_1_length + old_path_1_length / new_path_1_length
        self.assertEqual(
            a3_updated.start_position,
            a3.start_position * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )
        self.assertEqual(
            a3_updated.end_position,
            a3.end_position * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )

        self.assertEqual(
            a4_updated.start_position,
            a4.start_position * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )
        self.assertEqual(
            a4_updated.end_position,
            a4.end_position * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )

    def test_path_aggregation(self):
        """
               A---------------B + C-------------------D         A-----------------BC----------------D
                       |---------------------|                            |------------------|
                       E1                                                 E1

        2 path aggregations
        """
        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((0, 1), (10, 1)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((10, 1), (20, 1)))
        e1 = TopologyFactory.create(paths=[(path_AB, 0.5, 1), (path_CD, 0, 0.5)])
        path_AB.merge_path(path_CD)
        self.assertEqual(
            path_AB.geom, LineString((0, 1), (10, 1), (20, 1), srid=settings.SRID)
        )
        self.assertEqual(PathAggregation.objects.filter(topo_object=e1).count(), 2)
        self.assertEqual(PathAggregation.objects.count(), 2)
        first = PathAggregation.objects.first()
        last = PathAggregation.objects.last()
        self.assertEqual((first.start_position, first.end_position), (0.25, 0.5))
        self.assertEqual((last.start_position, last.end_position), (0.5, 0.75))
        self.assertEqual(Topology.objects.count(), 1)

    def test_recompute_pk_reverse_AB(self):
        """
        A---------------B + C-------------------D         B-----------------AC----------------D
          |        |          |--|           |         =>    |          |     |--|           |
          E1 (0.2) |          E3 (0.2, 0.3)  |               |       E1 (0.4) E3 (0.6, 0.65) E4 (0.9)
                   E2 (0.6)                  E4 (0.8)        E2 (0.2)

        In case of AB == CD, matching A and C
        """
        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((10, 1), (0, 1)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((10, 1), (20, 1)))

        e1 = TopologyFactory.create(geom=Point(2, 2))
        a1 = PathAggregationFactory.create(path=path_AB, topo_object=e1)

        e2 = TopologyFactory.create(geom=Point(6, 1))
        a2 = PathAggregationFactory.create(path=path_AB, topo_object=e2)

        e3 = TopologyFactory.create(
            geom=LineString(
                (2, 1),
                (3, 1),
            )
        )
        a3 = PathAggregationFactory.create(path=path_CD, topo_object=e3)
        e4 = TopologyFactory.create(geom=Point(8, 2))
        a4 = PathAggregationFactory.create(path=path_CD, topo_object=e4)

        path_AB_original_length = path_AB.length
        path_CD_original_length = path_CD.length
        path_AB.merge_path(path_CD)

        self.assertEqual(
            path_AB.geom, LineString((0, 1), (10, 1), (20, 1), srid=settings.SRID)
        )

        # reload updated objects
        a1_updated = PathAggregation.objects.get(pk=a1.pk)
        a2_updated = PathAggregation.objects.get(pk=a2.pk)
        a3_updated = PathAggregation.objects.get(pk=a3.pk)
        a4_updated = PathAggregation.objects.get(pk=a4.pk)

        # test pk recompute on path_1 : new pk = old pk * old_path_1_length / new_path_1_length
        self.assertEqual(
            a1_updated.start_position,
            (1 - a1.start_position) * (path_AB_original_length / path_AB.length),
        )
        self.assertEqual(
            a1_updated.end_position,
            (1 - a1.end_position) * (path_AB_original_length / path_AB.length),
        )

        self.assertEqual(
            a2_updated.start_position,
            (1 - a2.start_position) * (path_AB_original_length / path_AB.length),
        )
        self.assertEqual(
            a2_updated.end_position,
            (1 - a1.end_position) * (path_AB_original_length / path_AB.length),
        )

        # test pk recompute on path_2 : new pk = old pk * old_path_2_length / new_path_1_length + old_path_1_length / new_path_1_length
        self.assertEqual(
            a3_updated.start_position,
            a3.start_position * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )
        self.assertEqual(
            a3_updated.end_position,
            a3.end_position * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )

        self.assertEqual(
            a4_updated.start_position,
            a4.start_position * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )
        self.assertEqual(
            a4_updated.end_position,
            a4.end_position * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )

        # test offset changes
        e1_updated = Topology.objects.get(pk=e1.pk)
        self.assertEqual(e1_updated.offset, -e1.offset)

    def test_recompute_pk_reverse_CD(self):
        """
        A---------------B + C-------------------D         A----------------BD----------------C
          |        |          |--|           |         =>   |       |         |         |--|
          E1 (0.2) |          E3 (0.2, 0.3)  |             E1 (0.1) |         |         E3 (0.8, 0.9)
                   E2 (0.6)                  E4 (0.8)               E2 (0.3)  E4 (0.6)

        In case of AB == CD, matching B and D
        """
        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((0, 1), (10, 1)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((20, 1), (10, 1)))

        e1 = TopologyFactory.create(geom=Point(2, 2))
        a1 = PathAggregationFactory.create(path=path_AB, topo_object=e1)

        e2 = TopologyFactory.create(geom=Point(6, 1))
        a2 = PathAggregationFactory.create(path=path_AB, topo_object=e2)

        e3 = TopologyFactory.create(
            geom=LineString(
                (2, 1),
                (3, 1),
            )
        )
        a3 = PathAggregationFactory.create(path=path_CD, topo_object=e3)
        e4 = TopologyFactory.create(geom=Point(8, 2))
        a4 = PathAggregationFactory.create(path=path_CD, topo_object=e4)

        path_AB_original_length = path_AB.length
        path_CD_original_length = path_CD.length
        path_AB.merge_path(path_CD)

        self.assertEqual(
            path_AB.geom, LineString((0, 1), (10, 1), (20, 1), srid=settings.SRID)
        )

        # reload updated objects
        a1_updated = PathAggregation.objects.get(pk=a1.pk)
        a2_updated = PathAggregation.objects.get(pk=a2.pk)
        a3_updated = PathAggregation.objects.get(pk=a3.pk)
        a4_updated = PathAggregation.objects.get(pk=a4.pk)

        # test pk recompute on path_1 : new pk = old pk * old_path_1_length / new_path_1_length
        self.assertEqual(
            a1_updated.start_position,
            a1.start_position * (path_AB_original_length / path_AB.length),
        )
        self.assertEqual(
            a1_updated.end_position,
            a1.end_position * (path_AB_original_length / path_AB.length),
        )

        self.assertEqual(
            a2_updated.start_position,
            a2.start_position * (path_AB_original_length / path_AB.length),
        )
        self.assertEqual(
            a2_updated.end_position,
            a1.end_position * (path_AB_original_length / path_AB.length),
        )

        # test pk recompute on path_2 : new pk = old pk * old_path_2_length / new_path_1_length + old_path_1_length / new_path_1_length
        self.assertEqual(
            a3_updated.start_position,
            (1 - a3.start_position) * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )
        self.assertEqual(
            a3_updated.end_position,
            (1 - a3.end_position) * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )

        self.assertEqual(
            a4_updated.start_position,
            (1 - a4.start_position) * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )
        self.assertEqual(
            a4_updated.end_position,
            (1 - a4.end_position) * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )

        # test offset changes
        e4_updated = Topology.objects.get(pk=e4.pk)
        self.assertEqual(e4_updated.offset, -e4.offset)

    def test_recompute_pk_reverse_AB_CD(self):
        """
        A---------------B + C-------------------D         B----------------AD----------------C
          |        |          |--|           |         =>    |          |     |         |--|
          E1 (0.2) |          E3 (0.2, 0.3)  |               |       E1 (0.4) |         E3 (0.8, 0.9)
                   E2 (0.6)                  E4 (0.8)       E2 (0.2)         E4 (0.6)

        In case of AB == CD, matching A and D
        """
        path_AB = PathFactory.create(name="PATH_AB", geom=LineString((10, 1), (0, 1)))
        path_CD = PathFactory.create(name="PATH_CD", geom=LineString((20, 1), (10, 1)))

        e1 = TopologyFactory.create(geom=Point(2, 2))
        a1 = PathAggregationFactory.create(path=path_AB, topo_object=e1)

        e2 = TopologyFactory.create(geom=Point(6, 1))
        a2 = PathAggregationFactory.create(path=path_AB, topo_object=e2)

        e3 = TopologyFactory.create(
            geom=LineString(
                (2, 1),
                (3, 1),
            )
        )
        a3 = PathAggregationFactory.create(path=path_CD, topo_object=e3)
        e4 = TopologyFactory.create(geom=Point(8, 2))
        a4 = PathAggregationFactory.create(path=path_CD, topo_object=e4)

        path_AB_original_length = path_AB.length
        path_CD_original_length = path_CD.length
        path_AB.merge_path(path_CD)

        self.assertEqual(
            path_AB.geom, LineString((0, 1), (10, 1), (20, 1), srid=settings.SRID)
        )

        # reload updated objects
        a1_updated = PathAggregation.objects.get(pk=a1.pk)
        a2_updated = PathAggregation.objects.get(pk=a2.pk)
        a3_updated = PathAggregation.objects.get(pk=a3.pk)
        a4_updated = PathAggregation.objects.get(pk=a4.pk)

        # test pk recompute on path_1 : new pk = old pk * old_path_1_length / new_path_1_length
        self.assertEqual(
            a1_updated.start_position,
            (1 - a1.start_position) * (path_AB_original_length / path_AB.length),
        )
        self.assertEqual(
            a1_updated.end_position,
            (1 - a1.end_position) * (path_AB_original_length / path_AB.length),
        )

        self.assertEqual(
            a2_updated.start_position,
            (1 - a2.start_position) * (path_AB_original_length / path_AB.length),
        )
        self.assertEqual(
            a2_updated.end_position,
            (1 - a1.end_position) * (path_AB_original_length / path_AB.length),
        )

        # test pk recompute on path_2 : new pk = old pk * old_path_2_length / new_path_1_length + old_path_1_length / new_path_1_length
        self.assertEqual(
            a3_updated.start_position,
            (1 - a3.start_position) * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )
        self.assertEqual(
            a3_updated.end_position,
            (1 - a3.end_position) * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )

        self.assertEqual(
            a4_updated.start_position,
            (1 - a4.start_position) * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )
        self.assertEqual(
            a4_updated.end_position,
            (1 - a4.end_position) * (path_CD_original_length / path_AB.length)
            + path_AB_original_length / path_AB.length,
        )

        # test offset changes
        e1_updated = Topology.objects.get(pk=e1.pk)
        self.assertEqual(e1_updated.offset, -e1.offset)
        e4_updated = Topology.objects.get(pk=e4.pk)
        self.assertEqual(e4_updated.offset, -e4.offset)

    def test_response_is_json(self):
        response = self.client.post(reverse("core:path-drf-merge-path"))
        self.assertEqual(response.get("Content-Type"), "application/json")
