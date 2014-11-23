from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import Point, LineString

from geotrek.common.utils import almostequal
from geotrek.core.factories import PathFactory
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
