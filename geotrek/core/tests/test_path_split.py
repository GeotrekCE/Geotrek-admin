from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.test import TestCase

from geotrek.common.tests.utils import LineStringInBounds
from geotrek.core.models import Path, PathAggregation, Topology
from geotrek.core.tests.factories import (
    NetworkFactory,
    PathFactory,
    TopologyFactory,
    UsageFactory,
)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class SplitPathTest(TestCase):
    def test_split_attributes(self):
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        ab.networks.add(NetworkFactory.create())
        ab.usages.add(UsageFactory.create())
        PathFactory.create(geom=LineString((2, 0), (2, 2)))
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        self.assertEqual(ab.source, ab_2.source)
        self.assertEqual(ab.stake, ab_2.stake)
        self.assertListEqual(list(ab.networks.all()), list(ab_2.networks.all()))
        self.assertListEqual(list(ab.usages.all()), list(ab_2.usages.all()))

    def test_split_tee_1(self):
        """
               C
        A +----+----+ B
               |
               +      AB exists. Add CD.
               D
        """
        ab = PathFactory.create(name="AB", geom=LineStringInBounds((0, 0), (4, 0)))
        self.assertAlmostEqual(ab.length, 4, places=2)
        cd = PathFactory.create(geom=LineStringInBounds((2, 0), (2, 2)))
        self.assertAlmostEqual(cd.length, 2, places=2)

        # Make sure AB was split :
        ab.reload()
        self.assertEqual(
            ab.geom, LineStringInBounds((0, 0), (2, 0), srid=settings.SRID)
        )
        self.assertAlmostEqual(ab.length, 2, places=2)  # Length was also updated
        # And a clone of AB was created
        clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        self.assertEqual(len(clones), 1)
        ab_2 = clones[0]
        self.assertEqual(
            ab_2.geom, LineStringInBounds((2, 0), (4, 0), srid=settings.SRID)
        )
        self.assertAlmostEqual(ab_2.length, 2, places=2)  # Length was also updated

    def test_split_tee_2(self):
        """
        CD exists. Add AB.
        """
        cd = PathFactory.create(geom=LineStringInBounds((2, 0), (2, 2)))
        self.assertAlmostEqual(cd.length, 2, places=2)
        ab = PathFactory.create(name="AB", geom=LineStringInBounds((0, 0), (4, 0)))

        # Make sure AB was split :
        self.assertEqual(
            ab.geom, LineStringInBounds((0, 0), (2, 0), srid=settings.SRID)
        )
        self.assertAlmostEqual(ab.length, 2, places=2)  # Length was also updated

        clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        ab_2 = clones[0]
        self.assertEqual(
            ab_2.geom, LineStringInBounds((2, 0), (4, 0), srid=settings.SRID)
        )
        self.assertAlmostEqual(ab_2.length, 2, places=2)  # Length was also updated

    def test_split_cross(self):
        """
               C
               +
               |
        A +----+----+ B
               |
               +      AB exists. Add CD.
               D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((2, -2), (2, 2)))
        ab.reload()
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cd_2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(ab.geom, LineString((0, 0), (2, 0), srid=settings.SRID))
        self.assertEqual(cd.geom, LineString((2, -2), (2, 0), srid=settings.SRID))
        self.assertEqual(ab_2.geom, LineString((2, 0), (4, 0), srid=settings.SRID))
        self.assertEqual(cd_2.geom, LineString((2, 0), (2, 2), srid=settings.SRID))

    def test_split_cross_on_deleted(self):
        """
        Paths should not be splitted if they cross deleted paths.
        (attribute delete=True)
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        self.assertEqual(len(Path.objects.all()), 1)
        ab.delete()
        self.assertEqual(len(Path.objects.all()), 0)
        PathFactory.create(name="CD", geom=LineString((2, -2), (2, 2)))
        self.assertEqual(len(Path.objects.all()), 1)

    def test_split_on_update(self):
        """
                                       + E
                                       :
        A +----+----+ B         A +----+----+ B
                                       :
        C +----+ D              C +----+ D

                                    AB and CD exist. CD updated into CE.
        """
        ab = PathFactory.create(name="AB", geom=LineStringInBounds((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineStringInBounds((0, -2), (2, -2)))
        self.assertAlmostEqual(ab.length, 4, places=2)
        self.assertAlmostEqual(cd.length, 2, places=2)

        cd.geom = LineStringInBounds((0, -2), (2, -2), (2, 2))
        cd.save()
        ab.reload()
        self.assertAlmostEqual(ab.length, 2, places=2)
        self.assertAlmostEqual(cd.length, 4, places=2)
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cd_2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertAlmostEqual(ab_2.length, 2, places=2)
        self.assertAlmostEqual(cd_2.length, 2, places=2)

    def test_split_twice(self):
        """

             C   D
             +   +
             |   |
        A +--+---+--+ B
             |   |
             +---+

        """
        ab = PathFactory.create(name="AB", geom=LineStringInBounds((0, 0), (4, 0)))
        cd = PathFactory.create(
            name="CD", geom=LineStringInBounds((1, 2), (1, -2), (3, -2), (3, 2))
        )
        ab.reload()
        self.assertAlmostEqual(ab.length, 1, places=2)
        self.assertAlmostEqual(cd.length, 2, places=2)
        ab_clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        cd_clones = Path.objects.filter(name="CD").exclude(pk=cd.pk)
        self.assertEqual(len(ab_clones), 2)
        self.assertEqual(len(cd_clones), 2)
        # Depending on PostgreSQL fetch order
        if ab_clones[0].geom == LineStringInBounds((1, 0), (3, 0)):
            self.assertEqual(ab_clones[0].geom, LineStringInBounds((1, 0), (3, 0)))
            self.assertEqual(ab_clones[1].geom, LineStringInBounds((3, 0), (4, 0)))
        else:
            self.assertEqual(ab_clones[0].geom, LineStringInBounds((3, 0), (4, 0)))
            self.assertEqual(ab_clones[1].geom, LineStringInBounds((1, 0), (3, 0)))

        if cd_clones[0].geom == LineStringInBounds((3, 0), (3, 2)):
            self.assertEqual(cd_clones[0].geom, LineStringInBounds((3, 0), (3, 2)))
            self.assertEqual(
                cd_clones[1].geom,
                LineStringInBounds((1, 0), (1, -2), (3, -2), (3, 0)),
            )
        else:
            self.assertEqual(
                cd_clones[0].geom,
                LineStringInBounds((1, 0), (1, -2), (3, -2), (3, 0)),
            )
            self.assertEqual(cd_clones[1].geom, LineStringInBounds((3, 0), (3, 2)))

    def test_add_shortest_path(self):
        r"""
        A +----         -----+ C
               \       /
                \     /
                 --+--
                   B

               D        E
        A +---+---------+---+ C
               \       /
                \     /
                 --+--
                   B
        """
        ab = PathFactory.create(
            name="AB", geom=LineString((0, 0), (4, 0), (6, -2), (8, -2))
        )
        cb = PathFactory.create(
            name="CB", geom=LineString((14, 0), (12, 0), (10, -2), (8, -2))
        )
        de = PathFactory.create(name="DE", geom=LineString((4, 0), (12, 0)))

        # Paths were split, there are 5 now
        self.assertEqual(len(Path.objects.all()), 5)

        ab.reload()
        cb.reload()
        de.reload()
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cb_2 = Path.objects.filter(name="CB").exclude(pk=cb.pk)[0]

        self.assertEqual(de.geom, LineString((4, 0), (12, 0), srid=settings.SRID))
        self.assertEqual(ab.geom, LineString((0, 0), (4, 0), srid=settings.SRID))
        self.assertEqual(
            ab_2.geom, LineString((4, 0), (6, -2), (8, -2), srid=settings.SRID)
        )
        self.assertEqual(cb.geom, LineString((14, 0), (12, 0), srid=settings.SRID))
        self.assertEqual(
            cb_2.geom, LineString((12, 0), (10, -2), (8, -2), srid=settings.SRID)
        )

    def test_split_almost(self):
        r"""

           C   D
           +   +
            \ /
        A +--V--+ B
             E
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((1, 1), (2, -0.2), (3, 1)))
        ab.reload()
        cd.reload()
        eb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        ed = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(ab.geom, LineString((0, 0), (2, -0.2), srid=settings.SRID))
        self.assertEqual(cd.geom, LineString((1, 1), (2, -0.2), srid=settings.SRID))
        self.assertEqual(eb.geom, LineString((2, -0.2), (4, 0), srid=settings.SRID))
        self.assertEqual(ed.geom, LineString((2, -0.2), (3, 1), srid=settings.SRID))

    def test_split_almost_2(self):
        """
           + C
           |
        A +------- ... ----+ B
           |
           + D
        """
        cd = PathFactory.create(name="CD", geom=LineString((0.1, 1), (0.1, -1)))
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (10000000, 0)))
        ab.reload()
        cd.reload()
        self.assertEqual(
            ab.geom, LineString((0.1, 0), (10000000, 0), srid=settings.SRID)
        )
        self.assertEqual(cd.geom, LineString((0.1, 1), (0.1, 0), srid=settings.SRID))
        self.assertEqual(len(Path.objects.all()), 3)

    def test_split_almost_3(self):
        """
            + C
            |
        A +-+------ ... ----+ B
            |
            + D
        """
        cd = PathFactory.create(
            name="CD", geom=LineString((1.2, 1), (1.2, -1), srid=settings.SRID)
        )
        ab = PathFactory.create(
            name="AB", geom=LineString((0, 0), (10000000, 0), srid=settings.SRID)
        )
        ab.reload()
        cd.reload()
        self.assertEqual(ab.geom, LineString((0, 0), (1.2, 0), srid=settings.SRID))
        self.assertEqual(cd.geom, LineString((1.2, 1), (1.2, 0), srid=settings.SRID))
        self.assertEqual(len(Path.objects.all()), 4)

    def test_split_almost_4(self):
        """
             C
        -----+----+ A
        |    |
        |    |
        -----+----+ B
             D
        """
        ab = PathFactory.create(
            name="AB",
            geom=LineString(
                (998522.520690918, 6381896.4595642),
                (997785.990158081, 6381124.21846007),
                (998272.546691896, 6380561.77696227),
                (999629.548400879, 6381209.03106688),
            ),
        )
        cd = PathFactory.create(
            name="CD",
            geom=LineString(
                (998522.520690918, 6381896.4595642),
                (999098.044800479, 6380955.51783641),
            ),
        )
        ab.reload()
        cd.reload()
        self.assertEqual(len(Path.objects.all()), 3)

    def test_split_multiple(self):
        """

             C   E   G   I
             +   +   +   +
             |   |   |   |
        A +--+---+---+---+--+ B
             |   |   |   |
             +   +   +   +
             D   F   H   J
        """
        PathFactory.create(name="CD", geom=LineString((1, -2), (1, 2)))
        PathFactory.create(name="EF", geom=LineString((2, -2), (2, 2)))
        PathFactory.create(name="GH", geom=LineString((3, -2), (3, 2)))
        PathFactory.create(name="IJ", geom=LineString((4, -2), (4, 2)))
        PathFactory.create(name="AB", geom=LineString((0, 0), (5, 0)))

        self.assertEqual(len(Path.objects.filter(name="CD")), 2)
        self.assertEqual(len(Path.objects.filter(name="EF")), 2)
        self.assertEqual(len(Path.objects.filter(name="GH")), 2)
        self.assertEqual(len(Path.objects.filter(name="IJ")), 2)
        self.assertEqual(len(Path.objects.filter(name="AB")), 5)

    def test_split_multiple_2(self):
        """

             C   E   G   I
             +   +   +   +
             |   |   |   |
             |   |   |   |
        A +--+---+---+---+--+ B
             D   F   H   J
        """
        PathFactory.create(name="CD", geom=LineString((1, -2), (1, 2)))
        PathFactory.create(name="EF", geom=LineString((2, -2), (2, 2)))
        PathFactory.create(name="GH", geom=LineString((3, -2), (3, 2)))
        PathFactory.create(name="IJ", geom=LineString((4, -2), (4, 2)))
        PathFactory.create(name="AB", geom=LineString((0, -2), (5, -2)))

        self.assertEqual(len(Path.objects.filter(name="CD")), 1)
        self.assertEqual(len(Path.objects.filter(name="EF")), 1)
        self.assertEqual(len(Path.objects.filter(name="GH")), 1)
        self.assertEqual(len(Path.objects.filter(name="IJ")), 1)
        self.assertEqual(len(Path.objects.filter(name="AB")), 5)

    def test_split_multiple_3(self):
        r"""
               +            +
             E  \          /  F
        A +---+--+--------+--+---+ B
              |   \      /   |            AB exists. Create EF. Create CD.
              +----+----+----+
                    \  /
                     \/
        """
        PathFactory.create(name="AB", geom=LineString((0, 0), (10, 0)))
        PathFactory.create(name="EF", geom=LineString((2, 0), (2, -1), (8, -1), (8, 0)))

        PathFactory.create(name="CD", geom=LineString((2, 1), (5, -2), (8, 1)))

        self.assertEqual(len(Path.objects.filter(name="AB")), 5)
        self.assertEqual(len(Path.objects.filter(name="EF")), 3)
        self.assertEqual(len(Path.objects.filter(name="CD")), 5)

    def test_split_multiple_4(self):
        r"""
        Same as previous, without round values for intersections.

              C              D
               +            +
             E  \          /  F
        A +---+--+--------+--+---+ B
               \  \      /  /            AB exists. Create EF. Create CD.
                \  \    /  /
                 ---+--+---
                     \/
        """
        PathFactory.create(name="AB", geom=LineString((0, 0), (10, 0)))
        PathFactory.create(name="EF", geom=LineString((2, 0), (2, -1), (8, -1), (8, 0)))

        PathFactory.create(name="CD", geom=LineString((2, 1), (5, -2), (8, 1)))
        PathFactory.create(name="GH", geom=LineString((3, 1), (5, -2), (7, 1)))

        self.assertEqual(len(Path.objects.filter(name="AB")), 5)
        self.assertEqual(len(Path.objects.filter(name="EF")), 3)

    def test_split_multiple_5(self):
        r"""
             G E   C
             + +   +
              \|   |
         A +---+---+---+ B
               | - |
               |---+---+ F
                   |\
                   + +
                   D H
        """
        PathFactory.create(name="AB", geom=LineStringInBounds((0, 0), (300, 0)))
        PathFactory.create(name="CD", geom=LineStringInBounds((200, 100), (200, -200)))
        ab_1, ab_2 = Path.objects.filter(name="AB")
        cd_1, cd_2 = Path.objects.filter(name="CD")
        self.assertAlmostEqual(ab_1.length + ab_2.length, 300, places=0)
        self.assertAlmostEqual(cd_1.length + cd_2.length, 300, places=0)

        self.assertEqual(ab_1.geom, LineStringInBounds((0, 0), (200, 0)))
        self.assertEqual(cd_1.geom, LineStringInBounds((200, 100), (200, 0)))
        self.assertEqual(ab_2.geom, LineStringInBounds((200, 0), (300, 0)))
        self.assertEqual(cd_2.geom, LineStringInBounds((200, 0), (200, -200)))

        PathFactory.create(
            name="EF",
            geom=LineStringInBounds((100, 100), (100, -100), (300, -100)),
        )
        PathFactory.create(name="GH", geom=LineStringInBounds((50, 100), (250, -200)))

        self.assertEqual(Path.objects.filter(name="AB").count(), 4)
        self.assertEqual(Path.objects.filter(name="CD").count(), 4)
        self.assertEqual(Path.objects.filter(name="EF").count(), 5)
        self.assertEqual(Path.objects.filter(name="GH").count(), 5)

    def test_do_not_split_with_draft_1(self):
        """
               C
        A +----+----+ B
               |
               +      AB exists. Add CD draft.
               D
        AB is not split
        """
        ab = PathFactory.create(name="AB", geom=LineStringInBounds((0, 0), (4, 0)))
        self.assertAlmostEqual(ab.length, 4, places=2)
        cd = PathFactory.create(geom=LineStringInBounds((2, 0), (2, 2)), draft=True)
        self.assertAlmostEqual(cd.length, 2, places=2)
        ab.reload()
        self.assertEqual(ab.geom, LineStringInBounds((0, 0), (4, 0)))
        self.assertAlmostEqual(ab.length, 4, places=2)

    def test_do_not_split_with_draft_2(self):
        """
               C
        A +----+----+ B
               |
               +      AB draft exists. Add CD not draft.
               D
        AB is not split
        """
        ab = PathFactory.create(
            name="AB", geom=LineStringInBounds((0, 0), (4, 0)), draft=True
        )
        self.assertAlmostEqual(ab.length, 4, places=2)
        cd = PathFactory.create(geom=LineStringInBounds((2, 0), (2, 2)))
        self.assertAlmostEqual(cd.length, 2, places=2)
        ab.reload()
        self.assertEqual(ab.geom, LineStringInBounds((0, 0), (4, 0)))
        self.assertAlmostEqual(ab.length, 4, places=2)

    def test_do_not_split_with_draft_3(self):
        """
               C
        A +----+----+ B
               |
               +      AB draft exists. Add CD draft.
               D
        AB is not split
        """
        ab = PathFactory.create(
            name="AB", geom=LineStringInBounds((0, 0), (4, 0)), draft=True
        )
        self.assertAlmostEqual(ab.length, 4, places=2)
        cd = PathFactory.create(geom=LineStringInBounds((2, 0), (2, 2)), draft=True)
        self.assertAlmostEqual(cd.length, 2, places=2)
        ab.reload()
        self.assertEqual(ab.geom, LineStringInBounds((0, 0), (4, 0)))
        self.assertAlmostEqual(ab.length, 4, places=2)

    def test_do_not_split_with_draft_4(self):
        """
               C
        A +----+----+ B
               |
               +      AB exists. Add CD draft.
               D
        AB is not split
        Change CD to not draft
        AB is split
        """
        ab = PathFactory.create(
            name="AB", geom=LineStringInBounds((0, 0), (4, 0)), draft=False
        )
        self.assertAlmostEqual(ab.length, 4, places=2)
        cd = PathFactory.create(geom=LineStringInBounds((2, 0), (2, 2)), draft=True)
        self.assertAlmostEqual(cd.length, 2, places=2)
        ab.reload()
        self.assertEqual(
            ab.geom, LineStringInBounds((0, 0), (4, 0), srid=settings.SRID)
        )
        self.assertAlmostEqual(ab.length, 4, places=2)
        cd.draft = False
        cd.save()
        ab.reload()
        self.assertEqual(
            ab.geom, LineStringInBounds((0, 0), (2, 0), srid=settings.SRID)
        )
        self.assertAlmostEqual(ab.length, 2, places=2)
        clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        self.assertEqual(len(clones), 1)
        ab_2 = clones[0]
        self.assertEqual(
            ab_2.geom, LineStringInBounds((2, 0), (4, 0), srid=settings.SRID)
        )
        self.assertAlmostEqual(ab_2.length, 2, places=2)

    def test_do_not_split_with_draft_5(self):
        """
               C
        A +----+----+ B
               |
               +      AB draft exists. Add CD.
               D
        AB is not split
        Change AB to not draft
        AB is split
        """
        ab = PathFactory.create(
            name="AB", geom=LineStringInBounds((0, 0), (4, 0)), draft=True
        )
        self.assertAlmostEqual(ab.length, 4, places=2)
        cd = PathFactory.create(geom=LineStringInBounds((2, 0), (2, 2)), draft=False)
        self.assertAlmostEqual(cd.length, 2, places=2)
        ab.reload()
        self.assertEqual(
            ab.geom, LineStringInBounds((0, 0), (4, 0), srid=settings.SRID)
        )
        self.assertAlmostEqual(ab.length, 4, places=2)
        ab.draft = False
        ab.save()
        self.assertEqual(
            ab.geom, LineStringInBounds((0, 0), (2, 0), srid=settings.SRID)
        )
        self.assertAlmostEqual(ab.length, 2, places=2)
        clones = Path.objects.filter(name="AB").exclude(pk=ab.pk)
        self.assertEqual(len(clones), 1)
        ab_2 = clones[0]
        self.assertEqual(
            ab_2.geom, LineStringInBounds((2, 0), (4, 0), srid=settings.SRID)
        )
        self.assertAlmostEqual(ab_2.length, 2, places=2)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class SplitPathLineTopologyTest(TestCase):
    def create_line_topology(self, serialized):
        """We cannot use TopologyFactory here because we need a workflow similar to when creating a topology via the interface."""
        tmp_topo = Topology.deserialize(serialized)
        topology = Topology.objects.create()
        topology.mutate(tmp_topo)
        topology.refresh_from_db()
        return topology

    def test_split_tee_1(self):
        """
        AB exists with topology A'B' from left to right. Add CD.

                           C
          A              (2,0)             B
        (0,0) +-->---======+==>>==--->--+ (4,0)
                     A'    │     B'
                           ↓
                           │
                           +
                           D
                         (2,2)

        ->-  direction of path
        =>>=  direction of topology

        """
        # Create path AB
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))

        # Create a linear topology on path AB
        serialized = f'[{{"positions":{{"0":[0.25,0.75]}},"paths":[{ab.pk}]}}]'
        topology = self.create_line_topology(serialized)
        topo_geom = topology.geom

        # Check its path aggregation
        qs = PathAggregation.objects.filter(topo_object=topology)
        self.assertEqual(len(qs), 1)
        aggregation = qs.first()
        self.assertEqual(aggregation.path, ab)
        self.assertEqual(aggregation.start_position, 0.25)
        self.assertEqual(aggregation.end_position, 0.75)

        # Create a new path CD, intersecting path AB and the topology
        PathFactory.create(name="CD", geom=LineString((2, 0), (2, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # CB is a copy of AB

        # The topology now has two path aggregations (one on AC, one on BC)
        topology.refresh_from_db()
        self.assertEqual(len(topology.paths.all()), 2)
        self.assertEqual(len(ac.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 1)

        # The path aggregations positions have been adjusted
        aggr_ac = ac.aggregations.all()[0]
        aggr_cb = cb.aggregations.all()[0]
        self.assertEqual((0.5, 1.0), (aggr_ac.start_position, aggr_ac.end_position))
        self.assertEqual((0.0, 0.5), (aggr_cb.start_position, aggr_cb.end_position))

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_tee_1_reversed(self):
        """
        AB exists with topology B'A' from right to left. Add CD.

                           C
          A              (2,0)             B
        (0,0) +-->--===<<==+======--->--+ (4,0)
                     A'    │     B'
                           ↓
                           │
                           +
                           D
                         (2,2)

        ->-  direction of path
        =>>=  direction of topology

        """
        # Create path AB
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))

        # Create a linear topology on path AB
        serialized = f'[{{"positions":{{"0":[0.75,0.25]}},"paths":[{ab.pk}]}}]'
        topology = self.create_line_topology(serialized)
        topo_geom = topology.geom

        # Check its path aggregation
        qs = PathAggregation.objects.filter(topo_object=topology)
        self.assertEqual(len(qs), 1)
        aggregation = qs.first()
        self.assertEqual(aggregation.path, ab)
        self.assertEqual(aggregation.start_position, 0.75)
        self.assertEqual(aggregation.end_position, 0.25)

        # Create a new path CD, intersecting path AB and the topology
        PathFactory.create(name="CD", geom=LineString((2, 0), (2, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # CB is a copy of AB

        # The topology now has two path aggregations (one on AC, one on BC)
        topology.refresh_from_db()
        self.assertEqual(len(topology.paths.all()), 2)
        self.assertEqual(len(ac.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 1)

        # The path aggregations positions have been adjusted
        aggr_ac = ac.aggregations.all()[0]
        aggr_cb = cb.aggregations.all()[0]
        self.assertAlmostEqual(1, aggr_ac.start_position)
        self.assertAlmostEqual(0.5, aggr_ac.end_position)
        self.assertAlmostEqual(0.5, aggr_cb.start_position)
        self.assertAlmostEqual(0, aggr_cb.end_position)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_tee_2(self):
        """
              C
        A +---+---=====--+ B
              |   A'  B'
              +           AB exists with topology A'B'.
              D           Add CD
        """
        # Create path AB
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))

        # Create a linear topology on path AB
        topology = TopologyFactory.create(paths=[(ab, 0.5, 0.75)])
        topo_geom = topology.geom

        # Check its path aggregation
        qs = PathAggregation.objects.filter(topo_object=topology)
        self.assertEqual(len(qs), 1)
        aggregation = qs.first()
        self.assertEqual(aggregation.path, ab)
        self.assertEqual(aggregation.start_position, 0.5)
        self.assertEqual(aggregation.end_position, 0.75)

        # Create a new path CD, intersecting path AB but not the topology
        PathFactory.create(name="CD", geom=LineString((1, 0), (1, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # CB is a copy of AB

        # AC no longer has any topology linked to it
        self.assertEqual(len(ac.aggregations.all()), 0)

        # The topology is now linked to the new path (CB)
        topology.refresh_from_db()
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 1)
        self.assertEqual(topology.paths.all()[0].pk, cb.pk)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_tee_2_reversed(self):
        """
              C
        A +---+---=====--+ B
              |   A'  B'
              +           AB exists with topology A'B'.
              D           Add CD
        """
        # Create path AB
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))

        # Create a linear topology on path AB
        topology = TopologyFactory.create(paths=[(ab, 0.75, 0.5)])
        topo_geom = topology.geom

        # Check its path aggregation
        qs = PathAggregation.objects.filter(topo_object=topology)
        self.assertEqual(len(qs), 1)
        aggregation = qs.first()
        self.assertEqual(aggregation.path, ab)
        self.assertEqual(aggregation.start_position, 0.75)
        self.assertEqual(aggregation.end_position, 0.5)

        # Create a new path CD, intersecting path AB but not the topology
        PathFactory.create(name="CD", geom=LineString((1, 0), (1, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # CB is a copy of AB

        # AC no longer has any topology linked to it
        self.assertEqual(len(ac.aggregations.all()), 0)

        # The topology is now linked to the new path (CB)
        topology.refresh_from_db()
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 1)
        self.assertEqual(topology.paths.all()[0].pk, cb.pk)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_tee_3(self):
        """
                    C
        A +--=====--+---+ B
             A'  B' |
                    +    AB exists with topology A'B'.
                    D    Add CD
        """
        # Create path AB
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))

        # Create a linear topology on path AB
        topology = TopologyFactory.create(paths=[(ab, 0.3, 0.6)])
        topo_geom = topology.geom

        # Check its path aggregation
        qs = PathAggregation.objects.filter(topo_object=topology)
        self.assertEqual(len(qs), 1)
        aggregation = qs.first()
        self.assertEqual(aggregation.path, ab)
        self.assertEqual(aggregation.start_position, 0.3)
        self.assertEqual(aggregation.end_position, 0.6)

        # Create a new path CD, intersecting path AB but not the topology
        PathFactory.create(name="CD", geom=LineString((3, 0), (3, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # CB is a copy of AB

        # The topology is still linked to AC
        self.assertEqual(len(ac.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 0)

        # The path aggregations positions have been adjusted
        topology.refresh_from_db()
        aggr_ac = ac.aggregations.first()
        self.assertAlmostEqual(0.4, aggr_ac.start_position)
        self.assertAlmostEqual(0.8, aggr_ac.end_position)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_tee_3_reversed(self):
        """
                    C
        A +--=====--+---+ B
             A'  B' |
                    +    AB exists with topology A'B'.
                    D    Add CD
        """
        # Create path AB
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))

        # Create a linear topology on path AB
        topology = TopologyFactory.create(paths=[(ab, 0.45, 0.15)])
        topo_geom = topology.geom

        # Check its path aggregation
        qs = PathAggregation.objects.filter(topo_object=topology)
        self.assertEqual(len(qs), 1)
        aggregation = qs.first()
        self.assertEqual(aggregation.path, ab)
        self.assertEqual(aggregation.start_position, 0.45)
        self.assertEqual(aggregation.end_position, 0.15)

        # Create a new path CD, intersecting path AB but not the topology
        PathFactory.create(name="CD", geom=LineString((3, 0), (3, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # CB is a copy of AB

        # The topology is still linked to AC
        self.assertEqual(len(ac.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 0)

        # The path aggregations positions have been adjusted
        topology.refresh_from_db()
        aggr_ac = ac.aggregations.first()
        self.assertAlmostEqual(0.6, aggr_ac.start_position)
        self.assertAlmostEqual(0.2, aggr_ac.end_position)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_tee_4(self):
        """
                B   C   E
        A +--===+===+===+===--+ F
                    |
                    +    AB, BE, EF exist. A topology exists along them.
                    D    Add CD.
        """
        # Create paths AB, BE and EF
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (2, 0)))
        be = PathFactory.create(name="BE", geom=LineString((2, 0), (4, 0)))
        ef = PathFactory.create(name="EF", geom=LineString((4, 0), (6, 0)))

        # Create a linear topology on paths AB, BE and EF
        serialized = f'[{{"positions":{{"0":[0.5,1], "1":[0,1], "2":[0,0.5]}},"paths":[{ab.pk}, {be.pk}, {ef.pk}]}}]'
        topology = self.create_line_topology(serialized)
        topo_geom = topology.geom

        # Check its path aggregations
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(be.aggregations.all()), 1)
        self.assertEqual(len(ef.aggregations.all()), 1)
        self.assertEqual(len(topology.paths.all()), 3)

        # Create a new path CD, intersecting path BE and the topology
        PathFactory.create(name="CD", geom=LineString((3, 0), (3, 2)))
        bc = be  # BE has been shrunk into BC
        ce = (
            Path.objects.filter(name="BE").exclude(pk=be.pk).first()
        )  # CE is a copy of BE

        # The topology now covers 4 paths
        topology.refresh_from_db()
        self.assertEqual(len(topology.paths.all()), 4)
        # The topology is still linked to AB and EF
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(ef.aggregations.all()), 1)
        # BE and CE have one topology from 0.0 to 1.0
        self.assertEqual(len(bc.aggregations.all()), 1)
        self.assertEqual(len(ce.aggregations.all()), 1)
        aggr_bc = bc.aggregations.first()
        aggr_ce = ce.aggregations.first()
        self.assertEqual((0.0, 1.0), (aggr_bc.start_position, aggr_bc.end_position))
        self.assertEqual((0.0, 1.0), (aggr_ce.start_position, aggr_ce.end_position))
        self.assertEqual(len(topology.aggregations.all()), 4)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_tee_4_reversed(self):
        """
                B   C   E
        A +--===+===+===+===--+ F
                    |
                    +    AB, BE, EF exist. A topology exists along them.
                    D    Add CD.
        """
        # Create paths AB, BE and EF
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (2, 0)))
        be = PathFactory.create(name="BE", geom=LineString((4, 0), (2, 0)))
        ef = PathFactory.create(name="EF", geom=LineString((4, 0), (6, 0)))

        # Create a linear topology on paths AB, BE and EF
        serialized = f'[{{"positions":{{"0":[0.5,1], "1":[1,0], "2":[0,0.5]}},"paths":[{ab.pk}, {be.pk}, {ef.pk}]}}]'
        topology = self.create_line_topology(serialized)
        topo_geom = topology.geom

        # Check its path aggregations
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(be.aggregations.all()), 1)
        self.assertEqual(len(ef.aggregations.all()), 1)
        self.assertEqual(len(topology.paths.all()), 3)

        # Create a new path CD, intersecting path BE and the topology
        PathFactory.create(name="DC", geom=LineString((3, 0), (3, 2)))
        bc = be  # BE has been shrunk into BC
        ce = (
            Path.objects.filter(name="BE").exclude(pk=be.pk).first()
        )  # CE is a copy of BE

        # Topology now covers 4 paths
        topology.refresh_from_db()
        self.assertEqual(len(topology.paths.all()), 4)
        # Check its path aggregations
        aggr_ab = ab.aggregations.first()
        aggr_bc = bc.aggregations.first()
        aggr_ce = ce.aggregations.first()
        aggr_ef = ef.aggregations.first()
        self.assertAlmostEqual(0.5, aggr_ab.start_position)
        self.assertAlmostEqual(1, aggr_ab.end_position)
        self.assertAlmostEqual(1, aggr_bc.start_position)
        self.assertAlmostEqual(0, aggr_bc.end_position)
        self.assertAlmostEqual(1, aggr_ce.start_position)
        self.assertAlmostEqual(0, aggr_ce.end_position)
        self.assertAlmostEqual(0, aggr_ef.start_position)
        self.assertAlmostEqual(0.5, aggr_ef.end_position)
        self.assertEqual(len(topology.aggregations.all()), 4)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_twice(self):
        """

               C   D
               +   +
               |   |
        A +--==+===+==--+ B
               |   |
               +---+
        """
        # Create path AB
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))

        # Create a linear topology on path AB
        serialized = f'[{{"positions":{{"0":[0.1,0.9]}},"paths":[{ab.pk}]}}]'
        topology = self.create_line_topology(serialized)
        topo_geom = topology.geom

        # Check its path aggregation
        qs = PathAggregation.objects.filter(topo_object=topology)
        self.assertEqual(len(qs), 1)
        aggregation = qs.first()
        self.assertEqual(aggregation.path, ab)
        self.assertEqual(aggregation.start_position, 0.1)
        self.assertEqual(aggregation.end_position, 0.9)

        # Create a new path CD, intersecting path AB and the topology twice
        PathFactory.create(name="CD", geom=LineString((1, 2), (1, -2), (3, -2), (3, 2)))
        # AB has been shrunk and AB2 and AB3 have been created
        ab2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        ab3 = Path.objects.filter(name="AB").exclude(pk__in=[ab.pk, ab2.pk])[0]

        # The topology should now have 3 path aggregations
        topology.refresh_from_db()
        self.assertEqual(len(topology.paths.all()), 3)

        # Check its aggregation on AB
        self.assertEqual(len(ab.aggregations.all()), 1)
        aggr_ab = ab.aggregations.first()
        self.assertEqual((0.4, 1.0), (aggr_ab.start_position, aggr_ab.end_position))

        # Check its aggregation on AB2 and AB3
        if ab2.length_2d < ab3.length_2d:
            ab2, ab3 = ab3, ab2
        aggr_ab2 = ab2.aggregations.first()
        aggr_ab3 = ab3.aggregations.first()
        self.assertAlmostEqual(0, aggr_ab2.start_position)
        self.assertAlmostEqual(1, aggr_ab2.end_position)
        self.assertAlmostEqual(0, aggr_ab3.start_position)
        self.assertAlmostEqual(0.6, aggr_ab3.end_position)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_twice_reversed(self):
        """

               C   D
               +   +
               |   |
        A +--==+===+==--+ B
               |   |
               +---+
        """
        # Create path AB
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))

        # Create a linear topology on path AB
        serialized = f'[{{"positions":{{"0":[0.9,0.1]}},"paths":[{ab.pk}]}}]'
        topology = self.create_line_topology(serialized)
        topo_geom = topology.geom

        # Check its path aggregation
        qs = PathAggregation.objects.filter(topo_object=topology)
        self.assertEqual(len(qs), 1)
        aggregation = qs.first()
        self.assertEqual(aggregation.path, ab)
        self.assertEqual(aggregation.start_position, 0.9)
        self.assertEqual(aggregation.end_position, 0.1)

        # Create a new path CD, intersecting path AB and the topology twice
        PathFactory.create(name="CD", geom=LineString((1, 2), (1, -2), (3, -2), (3, 2)))
        # AB has been shrunk and AB2 and AB3 have been created
        ab2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        ab3 = Path.objects.filter(name="AB").exclude(pk__in=[ab.pk, ab2.pk])[0]

        # The topology should now have 3 path aggregations
        topology.refresh_from_db()
        self.assertEqual(len(topology.paths.all()), 3)

        # Check its aggregation on AB
        self.assertEqual(len(ab.aggregations.all()), 1)
        aggr_ab = ab.aggregations.first()
        self.assertEqual((1.0, 0.4), (aggr_ab.start_position, aggr_ab.end_position))

        # Check its aggregation on AB2 and AB3
        aggr_ab2 = ab2.aggregations.first()
        aggr_ab3 = ab3.aggregations.first()
        if aggr_ab2.start_position == 1.0:
            self.assertAlmostEqual(1, aggr_ab2.start_position)
            self.assertAlmostEqual(0, aggr_ab2.end_position)
            self.assertAlmostEqual(0.6, aggr_ab3.start_position)
            self.assertAlmostEqual(0, aggr_ab3.end_position)
        else:
            # Depended on postgresql fetch order, `ab2` was actually `ab3`
            self.assertAlmostEqual(1, aggr_ab3.start_position)
            self.assertAlmostEqual(0, aggr_ab3.end_position)
            self.assertAlmostEqual(0.6, aggr_ab2.start_position)
            self.assertAlmostEqual(0, aggr_ab2.end_position)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_on_update(self):
        """
                                          + E
                                          :
                                         ||
        A +-----------+ B         A +----++---+ B
                                         ||
        C +-====-+ D              C +--===+ D
        """
        PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((0, -1), (4, -1)))
        # Create a topology
        topology = TopologyFactory.create(paths=[(cd, 0.3, 0.9)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd.geom = LineString((0, -1), (2, -1), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 2)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(cd2.aggregations.all()), 1)
        aggr_cd = cd.aggregations.all()[0]
        aggr_cd2 = cd2.aggregations.all()[0]
        self.assertAlmostEqual(0.5, aggr_cd.start_position)
        self.assertAlmostEqual(1, aggr_cd.end_position)
        self.assertAlmostEqual(0, aggr_cd2.start_position)
        self.assertAlmostEqual(0.75, aggr_cd2.end_position)

    def test_split_on_update_2(self):
        """
                                          + E
                                          :
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C +-==------+ D           C +--===+ D
        """
        PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((0, -1), (4, -1)))
        # Create a topology
        topology = TopologyFactory.create(paths=[(cd, 0.15, 0.3)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd.geom = LineString((0, -1), (2, -1), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(cd2.aggregations.all()), 0)
        aggr_cd = cd.aggregations.all()[0]
        self.assertAlmostEqual(0.25, aggr_cd.start_position)
        self.assertAlmostEqual(0.5, aggr_cd.end_position)

    def test_split_on_update_3(self):
        """
                                          + E
                                          ||
                                          ||
        A +-----------+ B         A +-----+---+ B
                                          :
        C +------==-+ D           C +-----+ D
        """
        PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((0, -1), (4, -1)))
        # Create a topology
        topology = TopologyFactory.create(paths=[(cd, 0.7, 0.85)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd.geom = LineString((0, -1), (2, -1), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 0)
        self.assertEqual(len(cd2.aggregations.all()), 1)
        aggr_cd2 = cd2.aggregations.all()[0]
        self.assertAlmostEqual(0.25, aggr_cd2.start_position)
        self.assertAlmostEqual(0.625, aggr_cd2.end_position)

    def test_split_on_return_topology(self):
        """
        A       B       C       D
        +-------+-------+-------+
            >=================+
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        bc = PathFactory.create(name="BC", geom=LineString((4, 0), (8, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((8, 0), (12, 0)))
        topology = TopologyFactory.create(
            paths=[
                (ab, 0.5, 1),
                (bc, 0, 1),
                (cd, 0, 0.5),
                (cd, 0.5, 0.5),
                (cd, 0.5, 0),
                (bc, 1, 0),
                (ab, 1, 0.5),
            ]
        )
        self.assertEqual(len(topology.aggregations.all()), 7)

        topogeom = topology.geom

        PathFactory.create(name="split", geom=LineString((9, -1), (9, 1)))
        topology.reload()
        self.assertCountEqual(
            topology.aggregations.order_by("order").values_list("order", "path__name"),
            [
                (0, "AB"),
                (1, "BC"),
                (2, "CD"),
                (2, "CD"),
                (3, "CD"),
                (4, "CD"),
                (4, "CD"),
                (5, "BC"),
                (6, "AB"),
            ],
        )
        self.assertTrue(topology.geom.equals(topogeom))

    def test_split_on_topology_with_offset(self):
        """
        A               B
        +---------------+
            >=======+
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(paths=[(ab, 0.25, 0.75)], offset=1)
        self.assertEqual(len(topology.aggregations.all()), 1)

        topogeom = topology.geom

        PathFactory.create(name="split", geom=LineString((2, -2), (2, 2)))

        topology.reload()
        self.assertCountEqual(
            topology.aggregations.order_by("order").values_list("order", "path__name"),
            [(0, "AB"), (0, "AB")],
        )
        self.assertTrue(topology.geom.equals(topogeom))

    def test_split_on_topology_with_offset_and_point(self):
        """
        A               B
        +---------------+
            >=======+
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (5, 0)))
        topology = TopologyFactory.create(
            paths=[(ab, 0.2, 0.6), (ab, 0.6, 0.6), (ab, 0.6, 0.8)], offset=1
        )
        self.assertEqual(len(topology.aggregations.all()), 3)

        topogeom = topology.geom

        PathFactory.create(name="split", geom=LineString((2, -2), (2, 2)))

        topology.reload()
        self.assertCountEqual(
            topology.aggregations.order_by("order").values_list("order", "path__name"),
            [(0, "AB"), (0, "AB"), (1, "AB"), (2, "AB")],
        )
        self.assertTrue(topology.geom.equals(topogeom))


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class SplitPathPointTopologyTest(TestCase):
    def test_split_tee_1(self):
        """
                C
        A +-----X----+ B
                |
                +    AB exists with topology at C.
                D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(paths=[(ab, 0.5, 0.5)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd = PathFactory.create(geom=LineString((2, 0), (2, 2)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        self.assertEqual(len(topology.paths.all()), 3)
        self.assertEqual(len(ab.aggregations.all()), 1)
        aggr_ab = ab.aggregations.all()[0]
        self.assertEqual(len(cb.aggregations.all()), 1)
        aggr_cb = cb.aggregations.all()[0]
        self.assertEqual(len(cd.aggregations.all()), 1)
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_ab.start_position, aggr_ab.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cb.start_position, aggr_cb.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cd.start_position, aggr_cd.end_position))

    def test_split_tee_2(self):
        """
                C
        A +--X--+----+ B
                |
                +    AB exists.
                D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(paths=[(ab, 0.25, 0.25)])
        self.assertEqual(len(topology.paths.all()), 1)
        PathFactory.create(geom=LineString((2, 0), (2, 2)))
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 1)
        aggr_ab = ab.aggregations.all()[0]
        self.assertEqual((0.5, 0.5), (aggr_ab.start_position, aggr_ab.end_position))

    def test_split_tee_3(self):
        """
                C
        A +-----+--X--+ B
                |
                +    AB exists.
                D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(paths=[(ab, 0.75, 0.75)])
        self.assertEqual(len(topology.paths.all()), 1)
        PathFactory.create(geom=LineString((2, 0), (2, 2)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 0)
        self.assertEqual(len(cb.aggregations.all()), 1)
        aggr_cb = cb.aggregations.all()[0]
        self.assertEqual((0.5, 0.5), (aggr_cb.start_position, aggr_cb.end_position))

    def test_split_tee_4(self):
        """
                C
        A X-----+----+ B
                |
                +    AB exists.
                D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(paths=[(ab, 0, 0)])
        self.assertEqual(len(topology.paths.all()), 1)
        PathFactory.create(geom=LineString((2, 0), (2, 2)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 0)
        aggr_ab = ab.aggregations.all()[0]
        self.assertEqual((0.0, 0.0), (aggr_ab.start_position, aggr_ab.end_position))

    def test_split_tee_5(self):
        """
                C
        A +-----+----X B
                |
                +    AB exists.
                D    Add CD.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(paths=[(ab, 1, 1)])
        self.assertEqual(len(topology.paths.all()), 1)
        PathFactory.create(name="CD", geom=LineString((2, 0), (2, 2)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 0)
        self.assertEqual(len(cb.aggregations.all()), 1)
        aggr_cb = cb.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_cb.start_position, aggr_cb.end_position))

    def test_split_tee_6(self):
        """
            X
                C
        A +-----+-----+ B
                |
                +    AB exists. Add CD.
                D    Point with offset is now linked to AC.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (8, 0)))

        poi = Point(1, 3, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        topology = Topology.deserialize({"lat": poi.y, "lng": poi.x})
        topology.save()
        aggr = topology.aggregations.all()[0]
        position = topology.geom.coords

        self.assertAlmostEqual(3, topology.offset, places=6)
        self.assertAlmostEqual(0.125, aggr.start_position, places=6)
        self.assertAlmostEqual(0.125, aggr.end_position, places=6)

        # Add CD
        PathFactory.create(name="CD", geom=LineString((4, 0), (4, 2)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        aggr_ab = ab.aggregations.all()[0]

        topology.reload()
        self.assertAlmostEqual(3, topology.offset, places=6)
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 0)
        self.assertEqual(position, topology.geom.coords)
        self.assertAlmostEqual(0.5, aggr_ab.start_position, places=6)
        self.assertAlmostEqual(0.5, aggr_ab.end_position, places=6)

    def test_split_tee_7(self):
        """
                    X
                C
        A +-----+-----+ B
                |
                +    AB exists. Add CD.
                D    Point with offset is now linked to CB.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (8, 0)))

        poi = Point(7, 3, srid=settings.SRID)
        poi.transform(settings.API_SRID)
        topology = Topology.deserialize({"lat": poi.y, "lng": poi.x})
        topology.save()
        aggr = topology.aggregations.all()[0]
        position = topology.geom.coords

        self.assertAlmostEqual(3, topology.offset, places=6)
        self.assertAlmostEqual(0.875, aggr.start_position, places=6)
        self.assertAlmostEqual(0.875, aggr.end_position, places=6)

        # Add CD
        PathFactory.create(name="CD", geom=LineString((4, 0), (4, 2)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        topology.reload()
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 0)
        self.assertEqual(len(cb.aggregations.all()), 1)
        self.assertAlmostEqual(3, topology.offset, places=6)
        self.assertEqual(position, topology.geom.coords)
        aggr_cb = cb.aggregations.all()[0]
        self.assertAlmostEqual(0.75, aggr_cb.start_position, places=6)
        self.assertAlmostEqual(0.75, aggr_cb.end_position, places=6)

    def test_split_on_update(self):
        """
                                          + D
                                          :
                                          :
        A +-----------+ B         A +-----X---+ B
                                          :
        C +---X---+ D              C +----+
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((0, 1), (4, 1)))

        topology = TopologyFactory.create(paths=[(cd, 0.5, 0.5)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd.geom = LineString((2, -2), (2, 2))
        cd.save()
        ab2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]

        self.assertEqual(len(ab2.aggregations.all()), 1)
        self.assertEqual(len(cd2.aggregations.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(topology.paths.all()), 4)

        aggr_ab = ab.aggregations.all()[0]
        aggr_ab2 = ab2.aggregations.all()[0]
        aggr_cd = cd.aggregations.all()[0]
        aggr_cd2 = cd2.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_ab.start_position, aggr_ab.end_position))
        self.assertEqual((0.0, 0.0), (aggr_ab2.start_position, aggr_ab2.end_position))
        self.assertEqual((1.0, 1.0), (aggr_cd.start_position, aggr_cd.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cd2.start_position, aggr_cd2.end_position))

    def test_split_on_update_2(self):
        """
                                          + D
                                          :
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C +-X-----+ D              C +--X-+
        """
        PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((0, 1), (4, 1)))
        topology = TopologyFactory.create(paths=[(cd, 0.25, 0.25)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd.geom = LineString((2, -2), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(cd2.aggregations.all()), 0)
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((0.5, 0.5), (aggr_cd.start_position, aggr_cd.end_position))

    def test_split_on_update_3(self):
        """
                                          + E
                                          X
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C +-----X-+ D              C +----+ D
        """
        PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((0, 1), (4, 1)))
        topology = TopologyFactory.create(paths=[(cd, 0.75, 0.75)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd.geom = LineString((2, -2), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 0)
        self.assertEqual(len(cd2.aggregations.all()), 1)
        aggr_cd2 = cd2.aggregations.all()[0]
        self.assertEqual((0.5, 0.5), (aggr_cd2.start_position, aggr_cd2.end_position))

    def test_split_on_update_4(self):
        """
                                          + E
                                          :
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C X-------+ D              C X----+ D
        """
        PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((0, 1), (4, 1)))
        topology = TopologyFactory.create(paths=[(cd, 0, 0)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd.geom = LineString((2, -2), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(cd2.aggregations.all()), 0)
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((0.0, 0.0), (aggr_cd.start_position, aggr_cd.end_position))

    def test_split_on_update_5(self):
        """
                                          X E
                                          :
                                          :
        A +-----------+ B         A +-----+---+ B
                                          :
        C +-------X D              C +----+ D
        """
        PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((0, 1), (4, 1)))
        topology = TopologyFactory.create(paths=[(cd, 1, 1)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd.geom = LineString((2, -2), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]
        self.assertEqual(len(topology.paths.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 0)
        self.assertEqual(len(cd2.aggregations.all()), 1)
        aggr_cd2 = cd2.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_cd2.start_position, aggr_cd2.end_position))

    def test_split_on_update_6(self):
        """
                                          D
        A +-----------+ B         A +-----X---+ B
                                          :
        C +-------X D                     :
                                          +
                                          C
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((0, 1), (4, 1)))
        topology = TopologyFactory.create(paths=[(cd, 1, 1)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd.geom = LineString((2, -2), (2, 0))
        cd.save()
        db = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(db.aggregations.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(topology.paths.all()), 3)

        aggr_ab = ab.aggregations.all()[0]
        aggr_db = db.aggregations.all()[0]
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_ab.start_position, aggr_ab.end_position))
        self.assertEqual((0.0, 0.0), (aggr_db.start_position, aggr_db.end_position))
        self.assertEqual((1.0, 1.0), (aggr_cd.start_position, aggr_cd.end_position))

    def test_split_on_update_7(self):
        """
                                          C
        A +-----------+ B         A +-----X---+ B
                                          :
        C X-------+ D                     :
                                          + D
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        cd = PathFactory.create(name="CD", geom=LineString((0, 1), (4, 1)))
        topology = TopologyFactory.create(paths=[(cd, 0, 0)])
        self.assertEqual(len(topology.paths.all()), 1)

        cd.geom = LineString((2, 0), (2, -2))
        cd.save()
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 1)
        self.assertEqual(len(cd.aggregations.all()), 1)
        self.assertEqual(len(topology.paths.all()), 3)

        aggr_ab = ab.aggregations.all()[0]
        aggr_cb = cb.aggregations.all()[0]
        aggr_cd = cd.aggregations.all()[0]
        self.assertEqual((1.0, 1.0), (aggr_ab.start_position, aggr_ab.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cb.start_position, aggr_cb.end_position))
        self.assertEqual((0.0, 0.0), (aggr_cd.start_position, aggr_cd.end_position))


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class SplitPathGenericTopologyTest(TestCase):
    def create_line_topology(self, serialized):
        """We cannot use TopologyFactory here because we need a workflow similar to when creating a topology via the interface."""
        tmp_topo = Topology.deserialize(serialized)
        topology = Topology.objects.create()
        topology.mutate(tmp_topo)
        topology.refresh_from_db()
        return topology

    def test_add_simple_path(self):
        r"""
        A +--==          ==----+ C
               \\      //
                \\    //
                 ==+==
                   B
        Add path:

               D        E
        A +--==+--------+==----+ C
               \\      //
                \\    //
                 ==+==
                   B
        """
        ab = PathFactory.create(
            name="AB", geom=LineString((0, 0), (4, 0), (6, -2), (8, -2))
        )
        bc = PathFactory.create(
            name="BC", geom=LineString((8, -2), (10, -2), (12, 0), (14, 0))
        )
        topology = TopologyFactory.create(paths=[(ab, 0.25, 1), (bc, 0, 0.75)])
        self.assertEqual(len(topology.paths.all()), 2)
        originalgeom = LineString(
            (2.2071067811865475, 0),
            (4, 0),
            (6, -2),
            (8, -2),
            (10, -2),
            (12, 0),
            (12.2928932188134521, 0),
            srid=settings.SRID,
        )
        self.assertEqual(topology.geom, originalgeom)

        # Add a path
        de = PathFactory.create(name="DE", geom=LineString((4, 0), (12, 0)))
        self.assertEqual(len(Path.objects.all()), 5)
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        bc_2 = Path.objects.filter(name="BC").exclude(pk=bc.pk)[0]

        # Topology aggregations were updated
        topology.reload()
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(ab_2.aggregations.all()), 1)
        self.assertEqual(len(bc.aggregations.all()), 1)
        self.assertEqual(len(bc_2.aggregations.all()), 1)
        self.assertEqual(len(de.aggregations.all()), 0)
        aggr_ab = ab.aggregations.all()[0]
        aggr_ab2 = ab_2.aggregations.all()[0]
        aggr_bc = bc.aggregations.all()[0]
        aggr_bc2 = bc_2.aggregations.all()[0]
        self.assertAlmostEqual(0.551776695296637, aggr_ab.start_position)
        self.assertAlmostEqual(1, aggr_ab.end_position)
        self.assertAlmostEqual(0, aggr_ab2.start_position)
        self.assertAlmostEqual(1, aggr_ab2.end_position)
        self.assertAlmostEqual(0, aggr_bc.start_position)
        self.assertAlmostEqual(1, aggr_bc.end_position)
        self.assertAlmostEqual(0, aggr_bc2.start_position)
        self.assertAlmostEqual(0.146446609406726, aggr_bc2.end_position)

        # But topology resulting geometry did not change
        self.assertEqual(topology.geom, originalgeom)

    def test_add_path_converge(self):
        r"""
        A +--==          ==----+ C
               \\      //
                \\    //
                 ==+==
                   B
        Add path:

               D        E
        A +--==+--------+==----+ C
               \\      //
                \\    //
                 ==+==
                   B
        """
        ab = PathFactory.create(
            name="AB", geom=LineString((0, 0), (4, 0), (6, -2), (8, -2))
        )
        cb = PathFactory.create(
            name="CB", geom=LineString((14, 0), (12, 0), (10, -2), (8, -2))
        )
        topology = TopologyFactory.create(paths=[(ab, 0.25, 1), (cb, 1, 0.25)])
        self.assertEqual(len(topology.paths.all()), 2)
        originalgeom = LineString(
            (2.2071067811865475, 0),
            (4, 0),
            (6, -2),
            (8, -2),
            (10, -2),
            (12, 0),
            (12.2928932188134521, 0),
            srid=settings.SRID,
        )
        self.assertEqual(topology.geom, originalgeom)

        # Add a path
        de = PathFactory.create(name="DE", geom=LineString((4, 0), (12, 0)))
        self.assertEqual(len(Path.objects.all()), 5)
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cb_2 = Path.objects.filter(name="CB").exclude(pk=cb.pk)[0]

        # Topology aggregations were updated
        topology.reload()
        self.assertEqual(len(ab.aggregations.all()), 1)
        self.assertEqual(len(ab_2.aggregations.all()), 1)
        self.assertEqual(len(cb.aggregations.all()), 1)
        self.assertEqual(len(cb_2.aggregations.all()), 1)
        self.assertEqual(len(de.aggregations.all()), 0)
        aggr_ab = ab.aggregations.all()[0]
        aggr_ab2 = ab_2.aggregations.all()[0]
        aggr_cb = cb.aggregations.all()[0]
        aggr_cb2 = cb_2.aggregations.all()[0]
        self.assertAlmostEqual(0.551776695296637, aggr_ab.start_position)
        self.assertAlmostEqual(1, aggr_ab.end_position)
        self.assertAlmostEqual(0, aggr_ab2.start_position)
        self.assertAlmostEqual(1, aggr_ab2.end_position)
        self.assertAlmostEqual(1, aggr_cb2.start_position)
        self.assertAlmostEqual(0, aggr_cb2.end_position)
        self.assertAlmostEqual(1, aggr_cb.start_position)
        self.assertAlmostEqual(0.853553390593274, aggr_cb.end_position)

        # But topology resulting geometry did not change
        self.assertEqual(topology.geom, originalgeom)

    def test_add_path_diverge(self):
        r"""
        A +--==          ==----+ C
               \\      //
                \\    //
                 ==+==
                   B
        Add path:

               D        E
        A +--==+--------+==----+ C
               \\      //
                \\    //
                 ==+==
                   B
        """
        # Create paths BA and BC
        ba = PathFactory.create(
            name="BA", geom=LineString((8, -2), (6, -2), (4, 0), (0, 0))
        )
        bc = PathFactory.create(
            name="BC", geom=LineString((8, -2), (10, -2), (12, 0), (14, 0))
        )

        # Create a linear topology on paths BA and BC
        serialized = f'[{{"positions":{{"0":[0.75,0], "1":[0,0.75]}},"paths":[{ba.pk}, {bc.pk}]}}]'
        topology = self.create_line_topology(serialized)
        topo_geom = topology.geom

        # Check its geometry and number of path aggregations
        topology.refresh_from_db()
        self.assertEqual(len(topology.paths.all()), 2)
        expected_geom = LineString(
            (2.2071067811865475, 0),
            (4, 0),
            (6, -2),
            (8, -2),
            (10, -2),
            (12, 0),
            (12.2928932188134521, 0),
            srid=settings.SRID,
        )
        self.assertEqual(topology.geom, expected_geom)

        # Create a new path DE, intersecting paths BA and BC
        de = PathFactory.create(name="DE", geom=LineString((4, 0), (12, 0)))
        self.assertEqual(len(Path.objects.all()), 5)
        bd = ba  # BA has been shrunk into BD
        da = Path.objects.filter(name="BA").exclude(pk=ba.pk)[0]  # DA is a copy of BA
        be = bc  # BC has been shrunk into BE
        ec = Path.objects.filter(name="BC").exclude(pk=bc.pk)[0]  # EC is a copy of BC

        # Topology aggregations were updated
        topology.refresh_from_db()
        self.assertEqual(len(bd.aggregations.all()), 1)
        self.assertEqual(len(da.aggregations.all()), 1)
        self.assertEqual(len(be.aggregations.all()), 1)
        self.assertEqual(len(ec.aggregations.all()), 1)
        self.assertEqual(len(de.aggregations.all()), 0)
        aggr_bd = bd.aggregations.all()[0]
        aggr_da = da.aggregations.all()[0]
        aggr_be = be.aggregations.all()[0]
        aggr_ec = ec.aggregations.all()[0]
        self.assertAlmostEqual(0.448223304703363, aggr_da.start_position)
        self.assertAlmostEqual(0, aggr_da.end_position)
        self.assertAlmostEqual(1, aggr_bd.start_position)
        self.assertAlmostEqual(0, aggr_bd.end_position)
        self.assertAlmostEqual(0, aggr_be.start_position)
        self.assertAlmostEqual(1, aggr_be.end_position)
        self.assertAlmostEqual(0, aggr_ec.start_position)
        self.assertAlmostEqual(0.146446609406726, aggr_ec.end_position)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])
