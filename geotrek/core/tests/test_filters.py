from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, Point
from django.test import TestCase

from geotrek.land.tests.test_filters import LandFiltersTest

from geotrek.core.factories import PathFactory, TrailFactory
from geotrek.core.filters import PathFilterSet, TopologyFilter
from geotrek.core.models import Topology

from geotrek.trekking.factories import TrekFactory
from geotrek.trekking.filters import TrekFilterSet


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PathFilterLandTest(LandFiltersTest):

    filterclass = PathFilterSet


class TestFilter(TopologyFilter):
    model = Topology


class TopologyFilterTest(TestCase):
    def test_values_to_edges(self):
        topology = TestFilter()

        with self.assertRaises(NotImplementedError):
            topology.values_to_edges(['Value'])


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class TopologyFilterTrailTest(TestCase):
    def setUp(self):
        self.path = PathFactory()
        self.trail = TrailFactory(paths=[(self.path, 0, 1)])

    def test_trail_filters(self):
        PathFactory()
        qs = PathFilterSet().qs
        self.assertEqual(qs.count(), 2)

        data = {'trail': [self.trail]}
        qs = PathFilterSet(data=data).qs
        self.assertEqual(qs.count(), 1)


class ValidTopologyFilterTest(TestCase):
    def setUp(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.path = PathFactory()
            self.trek = TrekFactory.create(name="Crossed", paths=[(self.path, 0, 1)])
        else:
            self.trek = TrekFactory.create(geom=LineString((0, 0), (5, 5)))

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_trek_filters_not_valid(self):
        trek = TrekFactory.create(name="Not crossed", paths=[(self.path, 0, 0.5)])
        TrekFactory.create(paths=[])
        qs = TrekFilterSet().qs
        self.assertEqual(qs.count(), 3)

        data = {'is_valid': True}
        qs = TrekFilterSet(data=data).qs
        self.assertIn(self.trek, qs)
        self.assertEqual(qs.count(), 2)

        data = {'is_valid': False}
        qs = TrekFilterSet(data=data).qs
        self.assertEqual(qs.count(), 1)

        geom = LineString(Point(700100, 6600000), Point(700000, 6600100), srid=settings.SRID)
        PathFactory.create(geom=geom)
        self.trek.reload()
        trek.reload()
        data = {'is_valid': True}
        qs = TrekFilterSet(data=data).qs
        self.assertNotIn(self.trek, qs)
        self.assertIn(trek, qs)
        self.assertEqual(qs.count(), 1)

        data = {'is_valid': False}
        qs = TrekFilterSet(data=data).qs
        self.assertIn(self.trek, qs)
        self.assertNotIn(trek, qs)
        self.assertEqual(qs.count(), 2)

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_trek_filters_not_valid_nds(self):
        TrekFactory.create(name="Empty", geom='SRID=2154;LINESTRING EMPTY')
        qs = TrekFilterSet().qs
        self.assertEqual(qs.count(), 2)

        data = {'is_valid': True}
        qs = TrekFilterSet(data=data).qs
        self.assertIn(self.trek, qs)
        self.assertEqual(qs.count(), 1)

        data = {'is_valid': False}
        qs = TrekFilterSet(data=data).qs
        self.assertEqual(qs.count(), 1)
