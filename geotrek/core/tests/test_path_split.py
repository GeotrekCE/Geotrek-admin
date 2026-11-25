from unittest import expectedFailure

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.test import TestCase

from geotrek.common.tests.utils import LineStringInBounds
from geotrek.core.models import Path, Topology
from geotrek.core.tests.factories import (
    NetworkFactory,
    PathFactory,
    TopologyFactory,
    UsageFactory,
)


class AggregationsAssertionsMixin:
    def assertAggregations(self, topology, expected):
        """
        Check that the path aggregations of a topology are exactly `expected`,
        a list of (path, start_position, end_position).

        For a linear topology, `expected` is given along the topology: the
        aggregations sorted by their "order" must match it one by one, and their
        orders must go from 0 to n-1 without duplicates.

        For a point topology (every expected aggregation has start = end), the
        aggregations are compared regardless of their order, and all their
        orders must be 0: point topologies are never reordered.
        """
        topology.refresh_from_db()
        expected = [
            (path.pk, round(start, 6), round(end, 6)) for path, start, end in expected
        ]
        actual = [
            (order, path_id, round(start, 6), round(end, 6))
            for order, path_id, start, end in topology.aggregations.order_by(
                "order", "id"
            ).values_list("order", "path_id", "start_position", "end_position")
        ]
        if all(start == end for _, start, end in expected):  # Point topology
            self.assertCountEqual([aggregation[1:] for aggregation in actual], expected)
            self.assertEqual(
                [aggregation[0] for aggregation in actual], [0] * len(expected)
            )
        else:  # Linear topology
            self.assertEqual(
                actual,
                [(order, *aggregation) for order, aggregation in enumerate(expected)],
            )

    def get_path(self, name, *coords):
        """Find a piece of a split path by its name and geometry."""
        return Path.objects.get(
            name=name, geom__equals=LineString(*coords, srid=settings.SRID)
        )


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


class SplitPathLineTopologyTest(AggregationsAssertionsMixin, TestCase):
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
        self.assertAggregations(topology, [(ab, 0.25, 0.75)])

        # Create a new path CD, intersecting path AB and the topology
        PathFactory.create(name="CD", geom=LineString((2, 0), (2, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # CB is a copy of AB

        # The aggregations are ordered along the topology, which is still valid
        self.assertAggregations(topology, [(ac, 0.5, 1), (cb, 0, 0.5)])
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(ab, 0.75, 0.25)])

        # Create a new path CD, intersecting path AB and the topology
        PathFactory.create(name="CD", geom=LineString((2, 0), (2, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # CB is a copy of AB

        # The aggregations are ordered along the topology, which is still valid
        self.assertAggregations(topology, [(cb, 0.5, 0), (ac, 1, 0.5)])
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(ab, 0.5, 0.75)])

        # Create a new path CD, intersecting path AB but not the topology
        PathFactory.create(name="CD", geom=LineString((1, 0), (1, 2)))
        cb = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # CB is a copy of AB

        # The topology is now linked to the new path (CB) and is still valid
        self.assertAggregations(topology, [(cb, 1 / 3, 2 / 3)])
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(ab, 0.75, 0.5)])

        # Create a new path CD, intersecting path AB but not the topology
        PathFactory.create(name="CD", geom=LineString((1, 0), (1, 2)))
        cb = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # CB is a copy of AB

        # The topology is now linked to the new path (CB) and is still valid
        self.assertAggregations(topology, [(cb, 2 / 3, 1 / 3)])
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(ab, 0.3, 0.6)])

        # Create a new path CD, intersecting path AB but not the topology
        PathFactory.create(name="CD", geom=LineString((3, 0), (3, 2)))
        ac = ab  # AB has been shrunk into AC

        # The topology is still linked to AC, with adjusted positions, and is still valid
        self.assertAggregations(topology, [(ac, 0.4, 0.8)])
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(ab, 0.45, 0.15)])

        # Create a new path CD, intersecting path AB but not the topology
        PathFactory.create(name="CD", geom=LineString((3, 0), (3, 2)))
        ac = ab  # AB has been shrunk into AC

        # The topology is still linked to AC, with adjusted positions, and is still valid
        self.assertAggregations(topology, [(ac, 0.6, 0.2)])
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(ab, 0.5, 1), (be, 0, 1), (ef, 0, 0.5)])

        # Create a new path CD, intersecting path BE and the topology
        PathFactory.create(name="CD", geom=LineString((3, 0), (3, 2)))
        bc = be  # BE has been shrunk into BC
        ce = (
            Path.objects.filter(name="BE").exclude(pk=be.pk).first()
        )  # CE is a copy of BE

        # The aggregations are ordered along the topology, which is still valid.
        # The aggregations on AB and EF were not modified.
        self.assertAggregations(
            topology, [(ab, 0.5, 1), (bc, 0, 1), (ce, 0, 1), (ef, 0, 0.5)]
        )
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(ab, 0.5, 1), (be, 1, 0), (ef, 0, 0.5)])

        # Create a new path CD, intersecting path BE and the topology
        PathFactory.create(name="DC", geom=LineString((3, 0), (3, 2)))
        bc = be  # BE has been shrunk into BC
        ce = (
            Path.objects.filter(name="BE").exclude(pk=be.pk).first()
        )  # CE is a copy of BE

        # The aggregations are ordered along the topology, which is still valid:
        # BE is reversed, so the topology goes through CE before BC
        self.assertAggregations(
            topology, [(ab, 0.5, 1), (ce, 1, 0), (bc, 1, 0), (ef, 0, 0.5)]
        )
        self.assertTrue(topology.coupled)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_with_waypoint_on_kept_piece(self):
        """
        AB exists with a topology along its whole length, with a waypoint W.
        Add CD: the waypoint stays on the kept piece AC.

                  C
        A +===W===+=======+ B
                  |
                  + D

        A (0,0), B (4,0), W (1,0), C (2,0)
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(
            paths=[(ab, 0, 0.25), (ab, 0.25, 0.25), (ab, 0.25, 1)]
        )
        topo_geom = topology.geom

        PathFactory.create(name="CD", geom=LineString((2, 0), (2, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk).first()

        # The aggregations are ordered along the topology, which is still valid
        self.assertAggregations(
            topology, [(ac, 0, 0.5), (ac, 0.5, 0.5), (ac, 0.5, 1), (cb, 0, 1)]
        )
        self.assertTrue(topology.coupled)
        self.assertTrue(topology.geom.equals(topo_geom))

    def test_split_with_waypoint_on_kept_piece_reversed(self):
        """
        Same as above, with the topology going from B to A.

                  C
        A +===W===+=======+ B
                  |
                  + D

        A (0,0), B (4,0), W (1,0), C (2,0)
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(
            paths=[(ab, 1, 0.25), (ab, 0.25, 0.25), (ab, 0.25, 0)]
        )
        topo_geom = topology.geom

        PathFactory.create(name="CD", geom=LineString((2, 0), (2, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk).first()

        # The aggregations are ordered along the topology, which is still valid
        self.assertAggregations(
            topology, [(cb, 1, 0), (ac, 1, 0.5), (ac, 0.5, 0.5), (ac, 0.5, 0)]
        )
        self.assertTrue(topology.coupled)
        self.assertTrue(topology.geom.equals(topo_geom))

    @expectedFailure
    def test_split_with_waypoint_exactly_on_the_cut(self):
        """
        AB exists with a topology along its whole length, with a waypoint W.
        Add CD exactly on W.

                  C
        A +=======W=======+ B
                  |
                  + D

        A (0,0), B (4,0), W = C (2,0)

        Known failure: the waypoint is copied on CD as a junction point, and the trigger
        `core_pathaggregation_junction_point_iu_tgr` then deletes all the other
        aggregations of the topology (see `ft_topologies_paths_junction_point_iu`).
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(
            paths=[(ab, 0, 0.5), (ab, 0.5, 0.5), (ab, 0.5, 1)]
        )
        topo_geom = topology.geom

        PathFactory.create(name="CD", geom=LineString((2, 0), (2, 2)))
        ac = ab  # AB has been shrunk into AC
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk).first()

        self.assertAggregations(
            topology,
            [(ac, 0, 1), (ac, 1, 1), (cb, 0, 1)],
        )
        self.assertTrue(topology.coupled)
        self.assertTrue(topology.geom.equals(topo_geom))

    def test_split_with_waypoint_at_the_end_of_the_path(self):
        """
                B   C   E
        A +--===+===+===W===--+ F
                    |
                    +    AB, BE, EF exist. A topology exists along them,
                    D    with a waypoint W on E. Add CD: the waypoint is
                         copied at the end of the new piece CE, keeping its rank.
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (2, 0)))
        be = PathFactory.create(name="BE", geom=LineString((2, 0), (4, 0)))
        ef = PathFactory.create(name="EF", geom=LineString((4, 0), (6, 0)))
        topology = TopologyFactory.create(
            paths=[(ab, 0.5, 1), (be, 0, 1), (be, 1, 1), (ef, 0, 0.5)]
        )
        topo_geom = topology.geom

        PathFactory.create(name="CD", geom=LineString((3, 0), (3, 2)))
        bc = be  # BE has been shrunk into BC
        ce = Path.objects.filter(name="BE").exclude(pk=be.pk).first()

        # The aggregations are ordered along the topology, which is still valid
        self.assertAggregations(
            topology, [(ab, 0.5, 1), (bc, 0, 1), (ce, 0, 1), (ce, 1, 1), (ef, 0, 0.5)]
        )
        self.assertTrue(topology.coupled)
        self.assertTrue(topology.geom.equals(topo_geom))

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
        self.assertAggregations(topology, [(ab, 0.1, 0.9)])

        # Create a new path CD, intersecting path AB and the topology twice
        PathFactory.create(name="CD", geom=LineString((1, 2), (1, -2), (3, -2), (3, 2)))
        # AB has been shrunk into its first piece, AB2 and AB3 are the other pieces
        ab2 = self.get_path("AB", (1, 0), (3, 0))
        ab3 = self.get_path("AB", (3, 0), (4, 0))

        # The aggregations are ordered along the topology, which is still valid
        self.assertAggregations(topology, [(ab, 0.4, 1), (ab2, 0, 1), (ab3, 0, 0.6)])
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(ab, 0.9, 0.1)])

        # Create a new path CD, intersecting path AB and the topology twice
        PathFactory.create(name="CD", geom=LineString((1, 2), (1, -2), (3, -2), (3, 2)))
        # AB has been shrunk into its first piece, AB2 and AB3 are the other pieces
        ab2 = self.get_path("AB", (1, 0), (3, 0))
        ab3 = self.get_path("AB", (3, 0), (4, 0))

        # The aggregations are ordered along the topology (from B to A), which is still valid
        self.assertAggregations(topology, [(ab3, 0.6, 0), (ab2, 1, 0), (ab, 1, 0.4)])
        self.assertTrue(topology.coupled)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])

    def test_split_two_paths_of_the_topology_with_one_path(self):
        """
        AB and BC exist, with a topology from A' to C'.
        Add DE, which crosses AB at F and BC at G.

                        C +       + E (6,4)
                          |     /
                       C' +   /
                          ║ /
                          + G (4,2)
                        / ║
                      /   ║
                    /     ║
        A +---====+=======+ B
              A' /  F (2,0)
              /
            /
          + D (0,-2)

        A (0,0), B (4,0), C (4,4), A' (1,0), C' (4,3)
        =, ║  topology
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        bc = PathFactory.create(name="BC", geom=LineString((4, 0), (4, 4)))
        topology = TopologyFactory.create(paths=[(ab, 0.25, 1), (bc, 0, 0.75)])
        topo_geom = topology.geom

        PathFactory.create(name="DE", geom=LineString((0, -2), (6, 4)))
        self.assertEqual(Path.objects.count(), 7)
        af = ab  # AB has been shrunk into AF
        fb = Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        bg = bc  # BC has been shrunk into BG
        gc = Path.objects.filter(name="BC").exclude(pk=bc.pk).first()

        # The aggregations are ordered along the topology, which is still valid
        self.assertAggregations(
            topology, [(af, 0.5, 1), (fb, 0, 1), (bg, 0, 1), (gc, 0, 0.5)]
        )
        self.assertTrue(topology.coupled)
        self.assertTrue(topology.geom.equals(topo_geom))

    def test_split_three_times(self):
        """
        AB exists with a topology along its whole length.
        Add CD, which crosses AB three times, at E, F and G: AB is split
        into four pieces (and CD too).

              C +     +-----+
                |     |     |
        A +=====+=====+=====+=====+ B
                |E    |F    |G
                +-----+     + D

        A (0,0), B (4,0), E (1,0), F (2,0), G (3,0)
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(paths=[(ab, 0, 1)])
        topo_geom = topology.geom

        PathFactory.create(
            name="CD",
            geom=LineString((1, 2), (1, -2), (2, -2), (2, 2), (3, 2), (3, -2)),
        )
        ae = ab  # AB has been shrunk into AE
        ef = self.get_path("AB", (1, 0), (2, 0))
        fg = self.get_path("AB", (2, 0), (3, 0))
        gb = self.get_path("AB", (3, 0), (4, 0))

        # The aggregations are ordered along the topology, which is still valid
        self.assertAggregations(
            topology, [(ae, 0, 1), (ef, 0, 1), (fg, 0, 1), (gb, 0, 1)]
        )
        self.assertTrue(topology.coupled)
        self.assertTrue(topology.geom.equals(topo_geom))

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
        self.assertAggregations(topology, [(cd, 0.3, 0.9)])

        cd.geom = LineString((0, -1), (2, -1), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]

        # CD was split by recursive triggers: the aggregations are ordered along
        # the topology, which is still valid
        self.assertAggregations(topology, [(cd, 0.5, 1), (cd2, 0, 0.75)])
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(cd, 0.15, 0.3)])

        cd.geom = LineString((0, -1), (2, -1), (2, 2))
        cd.save()

        # The topology stays on the shrunk CD, with adjusted positions
        self.assertAggregations(topology, [(cd, 0.25, 0.5)])
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(cd, 0.7, 0.85)])

        cd.geom = LineString((0, -1), (2, -1), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]

        # The topology moved to the new piece CD2, with adjusted positions
        self.assertAggregations(topology, [(cd2, 0.25, 0.625)])
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(
            topology,
            [
                (ab, 0.5, 1),
                (bc, 0, 1),
                (cd, 0, 0.5),
                (cd, 0.5, 0.5),
                (cd, 0.5, 0),
                (bc, 1, 0),
                (ab, 1, 0.5),
            ],
        )

        topogeom = topology.geom

        PathFactory.create(name="split", geom=LineString((9, -1), (9, 1)))
        cd2 = (
            Path.objects.filter(name="CD").exclude(pk=cd.pk).first()
        )  # CD2 is a copy of CD

        # The aggregations are ordered along the topology, which goes through CD
        # and CD2 in both directions and passes through the waypoint on CD2.
        self.assertAggregations(
            topology,
            [
                (ab, 0.5, 1),
                (bc, 0, 1),
                (cd, 0, 1),
                (cd2, 0, 1 / 3),
                (cd2, 1 / 3, 1 / 3),
                (cd2, 1 / 3, 0),
                (cd, 1, 0),
                (bc, 1, 0),
                (ab, 1, 0.5),
            ],
        )
        self.assertTrue(topology.coupled)
        self.assertTrue(topology.geom.equals(topogeom))

    def test_split_on_topology_with_offset(self):
        """
        A               B
        +---------------+
            >=======+
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (4, 0)))
        topology = TopologyFactory.create(paths=[(ab, 0.25, 0.75)], offset=1)
        self.assertAggregations(topology, [(ab, 0.25, 0.75)])

        topogeom = topology.geom

        PathFactory.create(name="split", geom=LineString((2, -2), (2, 2)))
        ab2 = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # AB2 is a copy of AB

        self.assertAggregations(topology, [(ab, 0.5, 1), (ab2, 0, 0.5)])
        self.assertTrue(topology.coupled)
        self.assertEqual(topology.offset, 1)
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
        self.assertAggregations(
            topology, [(ab, 0.2, 0.6), (ab, 0.6, 0.6), (ab, 0.6, 0.8)]
        )

        topogeom = topology.geom

        PathFactory.create(name="split", geom=LineString((2, -2), (2, 2)))
        ab2 = (
            Path.objects.filter(name="AB").exclude(pk=ab.pk).first()
        )  # AB2 is a copy of AB

        # The waypoint (start = end) moved to AB2 with the line it is on
        self.assertAggregations(
            topology,
            [(ab, 0.5, 1), (ab2, 0, 1 / 3), (ab2, 1 / 3, 1 / 3), (ab2, 1 / 3, 2 / 3)],
        )
        self.assertTrue(topology.coupled)
        self.assertEqual(topology.offset, 1)
        self.assertTrue(topology.geom.equals(topogeom))


class SplitPathPointTopologyTest(AggregationsAssertionsMixin, TestCase):
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
        self.assertAggregations(topology, [(ab, 0.5, 0.5)])

        cd = PathFactory.create(geom=LineString((2, 0), (2, 2)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        # The junction point topology has one aggregation per path of the junction
        self.assertAggregations(topology, [(ab, 1, 1), (cb, 0, 0), (cd, 0, 0)])

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
        self.assertAggregations(topology, [(ab, 0.25, 0.25)])

        PathFactory.create(geom=LineString((2, 0), (2, 2)))

        # The topology stays on the shrunk AB, with an adjusted position
        self.assertAggregations(topology, [(ab, 0.5, 0.5)])

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
        self.assertAggregations(topology, [(ab, 0.75, 0.75)])

        PathFactory.create(geom=LineString((2, 0), (2, 2)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        # The topology moved to the new piece CB, with an adjusted position
        self.assertAggregations(topology, [(cb, 0.5, 0.5)])

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
        self.assertAggregations(topology, [(ab, 0, 0)])

        PathFactory.create(geom=LineString((2, 0), (2, 2)))

        # The topology stays at the start of the shrunk AB
        self.assertAggregations(topology, [(ab, 0, 0)])

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
        self.assertAggregations(topology, [(ab, 1, 1)])

        PathFactory.create(name="CD", geom=LineString((2, 0), (2, 2)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        # The topology moved to the end of the new piece CB
        self.assertAggregations(topology, [(cb, 1, 1)])

    @expectedFailure
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
        position = topology.geom.coords
        self.assertAlmostEqual(3, topology.offset, places=6)
        self.assertAggregations(topology, [(ab, 0.125, 0.125)])

        # Add CD
        PathFactory.create(name="CD", geom=LineString((4, 0), (4, 2)))

        # The topology stays on the shrunk AB, with an adjusted position
        self.assertAggregations(topology, [(ab, 0.25, 0.25)])
        self.assertAlmostEqual(3, topology.offset, places=6)
        self.assertEqual(position, topology.geom.coords)

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
        position = topology.geom.coords
        self.assertAlmostEqual(3, topology.offset, places=6)
        self.assertAggregations(topology, [(ab, 0.875, 0.875)])

        # Add CD
        PathFactory.create(name="CD", geom=LineString((4, 0), (4, 2)))
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        # The topology moved to the new piece CB, with an adjusted position
        self.assertAggregations(topology, [(cb, 0.75, 0.75)])
        self.assertAlmostEqual(3, topology.offset, places=6)
        self.assertEqual(position, topology.geom.coords)

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
        self.assertAggregations(topology, [(cd, 0.5, 0.5)])

        cd.geom = LineString((2, -2), (2, 2))
        cd.save()
        ab2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]

        # CD now crosses AB at the topology: the junction point topology has one
        # aggregation per path of the junction
        self.assertAggregations(
            topology, [(ab, 1, 1), (ab2, 0, 0), (cd, 1, 1), (cd2, 0, 0)]
        )

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
        self.assertAggregations(topology, [(cd, 0.25, 0.25)])

        cd.geom = LineString((2, -2), (2, 2))
        cd.save()

        # The topology stays on the shrunk CD, with an adjusted position
        self.assertAggregations(topology, [(cd, 0.5, 0.5)])

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
        self.assertAggregations(topology, [(cd, 0.75, 0.75)])

        cd.geom = LineString((2, -2), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]

        # The topology moved to the new piece CD2, with an adjusted position
        self.assertAggregations(topology, [(cd2, 0.5, 0.5)])

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
        self.assertAggregations(topology, [(cd, 0, 0)])

        cd.geom = LineString((2, -2), (2, 2))
        cd.save()

        # The topology stays at the start of the shrunk CD
        self.assertAggregations(topology, [(cd, 0, 0)])

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
        self.assertAggregations(topology, [(cd, 1, 1)])

        cd.geom = LineString((2, -2), (2, 2))
        cd.save()
        cd2 = Path.objects.filter(name="CD").exclude(pk=cd.pk)[0]

        # The topology moved to the end of the new piece CD2
        self.assertAggregations(topology, [(cd2, 1, 1)])

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
        self.assertAggregations(topology, [(cd, 1, 1)])

        cd.geom = LineString((2, -2), (2, 0))
        cd.save()
        db = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        # CD now ends on AB at the topology: the junction point topology has one
        # aggregation per path of the junction
        self.assertAggregations(topology, [(ab, 1, 1), (db, 0, 0), (cd, 1, 1)])

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
        self.assertAggregations(topology, [(cd, 0, 0)])

        cd.geom = LineString((2, 0), (2, -2))
        cd.save()
        cb = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]

        # CD now starts on AB at the topology: the junction point topology has one
        # aggregation per path of the junction
        self.assertAggregations(topology, [(ab, 1, 1), (cb, 0, 0), (cd, 0, 0)])


class SplitPathGenericTopologyTest(AggregationsAssertionsMixin, TestCase):
    def create_line_topology(self, serialized):
        """
        We cannot use TopologyFactory here because we need a workflow similar to when creating a
        topology via the interface.
        """
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
        self.assertAggregations(topology, [(ab, 0.25, 1), (bc, 0, 0.75)])
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
        PathFactory.create(name="DE", geom=LineString((4, 0), (12, 0)))
        self.assertEqual(len(Path.objects.all()), 5)
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        bc_2 = Path.objects.filter(name="BC").exclude(pk=bc.pk)[0]

        # The aggregations are ordered along the topology, which is still valid
        self.assertAggregations(
            topology,
            [
                (ab, 0.551776695296637, 1),
                (ab_2, 0, 1),
                (bc, 0, 1),
                (bc_2, 0, 0.146446609406726),
            ],
        )
        self.assertTrue(topology.coupled)

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
        self.assertAggregations(topology, [(ab, 0.25, 1), (cb, 1, 0.25)])
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
        PathFactory.create(name="DE", geom=LineString((4, 0), (12, 0)))
        self.assertEqual(len(Path.objects.all()), 5)
        ab_2 = Path.objects.filter(name="AB").exclude(pk=ab.pk)[0]
        cb_2 = Path.objects.filter(name="CB").exclude(pk=cb.pk)[0]

        # The aggregations are ordered along the topology, which is still valid:
        # CB is reversed, so the topology goes through CB2 before CB
        self.assertAggregations(
            topology,
            [
                (ab, 0.551776695296637, 1),
                (ab_2, 0, 1),
                (cb_2, 1, 0),
                (cb, 1, 0.853553390593274),
            ],
        )
        self.assertTrue(topology.coupled)

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

        # Check its path aggregations and geometry
        self.assertAggregations(topology, [(ba, 0.75, 0), (bc, 0, 0.75)])
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
        PathFactory.create(name="DE", geom=LineString((4, 0), (12, 0)))
        self.assertEqual(len(Path.objects.all()), 5)
        bd = ba  # BA has been shrunk into BD
        da = Path.objects.filter(name="BA").exclude(pk=ba.pk)[0]  # DA is a copy of BA
        be = bc  # BC has been shrunk into BE
        ec = Path.objects.filter(name="BC").exclude(pk=bc.pk)[0]  # EC is a copy of BC

        # The aggregations are ordered along the topology, which is still valid:
        # BA is reversed, so the topology goes through DA before BD
        self.assertAggregations(
            topology,
            [
                (da, 0.448223304703363, 0),
                (bd, 1, 0),
                (be, 0, 1),
                (ec, 0, 0.146446609406726),
            ],
        )
        self.assertTrue(topology.coupled)

        # The start and end positions of the geometry should not have changed
        self.assertAlmostEqual(topology.geom.coords[0][0], topo_geom.coords[0][0])
        self.assertAlmostEqual(topology.geom.coords[0][1], topo_geom.coords[0][1])
        self.assertAlmostEqual(topology.geom.coords[-1][0], topo_geom.coords[-1][0])
        self.assertAlmostEqual(topology.geom.coords[-1][1], topo_geom.coords[-1][1])
