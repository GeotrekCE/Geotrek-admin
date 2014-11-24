from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import Point, LineString

from geotrek.common.utils import almostequal
from geotrek.core.factories import PathFactory, TopologyFactory
from geotrek.core.models import Topology


def _build_point_topo(x, y):
    """Little helper to build point topologies
    """
    poi = Point(x, y, srid=settings.SRID)
    poi.transform(settings.API_SRID)
    return Topology.deserialize({'lat': poi.y, 'lng': poi.x})


class PointTopologiesTest(TestCase):

    def test_geom_is_preserved_if_middle_without_offset(self):
        """
        Middle without offset : point not moving
        +                  +
        |                  |
        X                  |        X
        |                  |
        |                  |
        +                  +
        """
        p1 = PathFactory.create(geom=LineString((0, 0),
                                                (0, 5)))
        poitopo = _build_point_topo(0, 2.5)
        self.assertTrue(almostequal(0.5, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(0, poitopo.offset))
        self.assertTrue(almostequal(0, poitopo.geom.x))
        self.assertTrue(almostequal(2.5, poitopo.geom.y))
        p1.geom = LineString((10, 0),
                             (10, 5))
        p1.save()
        poitopo.reload()
        self.assertTrue(almostequal(0.5, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(10, poitopo.offset))
        self.assertTrue(almostequal(0, poitopo.geom.x))
        self.assertTrue(almostequal(2.5, poitopo.geom.y))

    def test_geom_is_preserved_if_middle_with_offset(self):
        """
        Middle with offset : point not moving
        +                  +
        |                  |
        | X                |        X
        |                  |
        |                  |
        +                  +
        """
        p1 = PathFactory.create(geom=LineString((0, 0),
                                                (0, 5)))
        poitopo = _build_point_topo(-1, 2.5)
        self.assertTrue(almostequal(0.5, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(1, poitopo.offset))
        self.assertTrue(almostequal(-1, poitopo.geom.x))
        self.assertTrue(almostequal(2.5, poitopo.geom.y))
        p1.geom = LineString((10, 0),
                             (10, 5))
        p1.save()
        poitopo.reload()
        self.assertTrue(almostequal(0.5, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(11, poitopo.offset))
        self.assertTrue(almostequal(-1, poitopo.geom.x))
        self.assertTrue(almostequal(2.5, poitopo.geom.y))

    def test_offset_kept_but_aggregration_updated(self):
        """
        Shorten path, offset kept, aggregation updated.

          X                        X
        +-----------+            +------+

        """
        p1 = PathFactory.create(geom=LineString((0, 0), (20, 0)))
        poitopo = _build_point_topo(5, 10)
        self.assertTrue(almostequal(0.25, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(10, poitopo.offset))

        p1.geom = LineString((0, 0), (10, 0))
        p1.save()
        poitopo.reload()
        self.assertTrue(almostequal(0.5, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(10, poitopo.offset))
        # Not moved:
        self.assertTrue(almostequal(5, poitopo.geom.x))
        self.assertTrue(almostequal(10, poitopo.geom.y))

    def test_offset_and_aggregration_updated(self):
        """
        Shorten path, point is not moved (azymuth > 90 deg.)

               X                              X
        +-----------+            +------+


        TODO: for this case, using azymuths would be useful.
        See https://github.com/makinacorpus/Geotrek/issues/1316
        """
        p1 = PathFactory.create(geom=LineString((0, 0), (20, 0)))
        poitopo = _build_point_topo(10, 10)
        self.assertTrue(almostequal(0.5, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(10, poitopo.offset))

        p1.geom = LineString((0, 0), (0, 5))
        p1.save()
        poitopo.reload()
        self.assertTrue(almostequal(1.0, poitopo.aggregations.all()[0].start_position))
        self.assertTrue(almostequal(11.180339887, poitopo.offset))
        # Not moved (azymuth > 90degres)
        self.assertTrue(almostequal(10, poitopo.geom.x))
        self.assertTrue(almostequal(10, poitopo.geom.y))


class LineTopologiesTest(TestCase):
    def test_geom_is_updated_if_100_percent(self):
        """
            A         B               A             B
            >=========>               >==+      +===>
                                         \\    //
            Update AB.                    +====+
        """
        p = PathFactory.create(geom=LineString((0, 0), (4, 0)))
        t1 = TopologyFactory.create(no_path=True)
        t1.add_path(p)
        t1_agg = t1.aggregations.get()
        self.assertEqual(t1.offset, 0.0)
        self.assertEqual(t1.geom.coords, ((0, 0), (4, 0)))
        self.assertEqual(t1_agg.start_position, 0.0)
        self.assertEqual(t1_agg.end_position, 1.0)

        p.geom = LineString((0, 0), (1.98, 0), (2.0, -1), (2.02, 0), (4, 0))
        p.save()
        t1.reload()
        t1_agg = t1.aggregations.get()
        self.assertEqual(t1.offset, 0.0)
        self.assertEqual(t1.geom.coords, ((0, 0), (1.98, 0), (2.0, -1), (2.02, 0), (4, 0)))
        self.assertEqual(t1_agg.start_position, 0.0)
        self.assertEqual(t1_agg.end_position, 1.0)

    def test_geom_is_updated_if_has_path_among_agregations(self):
        """
            A     B        C       D          A     B      C       D
            +-->==+========+===>---+          +-->==+      +===>---+
                                                    \\    //
                                                     +====+
        """
        ab = PathFactory.create(geom=LineString((0, 0), (2, 0)))
        bc = PathFactory.create(geom=LineString((2, 0), (4, 0)))
        cd = PathFactory.create(geom=LineString((4, 0), (6, 0)))
        t1 = TopologyFactory.create(no_path=True)
        t1.add_path(ab, start=0.5, order=1)
        t1.add_path(bc, order=2)
        t1.add_path(cd, end=0.5, order=3)

        bc.geom = LineString((2, 0), (3, -1), (4, 0))
        bc.save()
        t1.reload()
        self.assertEqual(t1.geom.coords, ((1, 0), (2, 0), (3, -1), (4, 0), (5, 0)))

    def test_offset_is_not_updated_when_path_changes(self):
        """
            A         B
            +---------+
            >=========>

                            A         B
                            +---------+
                            >=========>
        """
        p = PathFactory.create(geom=LineString((0, 0), (4, 0)))
        t1 = TopologyFactory.create(offset=1, no_path=True)
        t1.add_path(p)
        p.geom = LineString((0, 10), (4, 10))
        p.save()
        t1.reload()
        self.assertEqual(t1.geom.coords, ((0, 11), (4, 11)))

    def test_pk_start_not_updated_if_start_at_0(self):
        """
            A         B          +>=>-----+ B
            >===>-----+          ||
                                 ^
                                 A
        """
        p = PathFactory.create(geom=LineString((0, 0), (4, 0)))
        t1 = TopologyFactory.create(no_path=True)
        t1.add_path(p, end=0.5)
        p.geom = LineString((0, -10), (0, 0), (4, 0))
        p.save()
        t1.reload()
        self.assertEqual(t1.geom.coords, ((0.0, -10.0), (0.0, 0.0), (2.0, 0.0)))

    def test_pk_start_not_updated_if_start_at_1(self):
        """
            A         B          A
            +-----<===<          +
                                 |
                                 +---<===< B
        """
        p = PathFactory.create(geom=LineString((0, 0), (4, 0)))
        t1 = TopologyFactory.create(no_path=True)
        t1.add_path(p, start=1.0, end=0.5)
        p.geom = LineString((0, 10), (0, 0), (4, 0))
        p.save()
        t1.reload()
        self.assertEqual(t1.geom.coords, ((4, 0), (2, 0)))

    def test_pk_end_not_updated_if_end_at_1(self):
        """
            A         B          +--->===> B
            +----->===>          |
                                 ^
                               A
        """
        p = PathFactory.create(geom=LineString((0, 0), (4, 0)))
        t1 = TopologyFactory.create(no_path=True)
        t1.add_path(p, start=0.5)
        p.geom = LineString((0, -10), (0, 0), (4, 0))
        p.save()
        t1.reload()
        self.assertEqual(t1.geom.coords, ((2, 0), (4, 0)))

    def test_pk_end_not_updated_if_end_at_0(self):
        """
            A         B          +-------+ B
            <===<-----+          |
                                 v
                                 ||
                                 v
                               A
        """
        p = PathFactory.create(geom=LineString((0, 0), (4, 0)))
        t1 = TopologyFactory.create(no_path=True)
        t1.add_path(p, start=0.0, end=0.5)
        p.geom = LineString((0, -10), (0, 0), (4, 0))
        p.save()
        t1.reload()
        self.assertEqual(t1.geom.coords, ((0, -10), (0, 0), (2, 0)))

    def test_both_pk_updated_when_path_is_shorten(self):
        """
            A             B     A         B
            +--->===>-----+     +--->===>-+
        """
        p = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        t1 = TopologyFactory.create(no_path=True)
        t1.add_path(p, start=0.4, end=0.6)
        p.geom = LineString((2, 0), (8, 0))
        p.save()
        t1.reload()
        self.assertEqual(t1.geom.coords, ((4, 0), (6, 0)))

    def test_both_pk_updated_to_closest_points(self):
        """
            A             B     A                      B
            +--->===>-----+     +-----+         +------+
                                      \\       /
                                       +===>--+
        """
        p = PathFactory.create(geom=LineString((0, 0), (10, 0)))
        t1 = TopologyFactory.create(no_path=True)
        t1.add_path(p, start=0.4, end=0.6)
        p.geom = LineString((0, 0), (2, 0), (2, -2), (8, -2), (8, 0), (10, 0))
        p.save()
        t1.reload()
        self.assertEqual(t1.geom.coords, ((2, 0), (2, -2), (6, -2)))
