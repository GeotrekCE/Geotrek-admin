from unittest import skipIf

from django.conf import settings
from django.test import TestCase

from geotrek.land.tests.test_filters import LandFiltersTest

from geotrek.core.factories import PathFactory, TrailFactory
from geotrek.core.filters import PathFilterSet, TopologyFilter
from geotrek.core.models import Topology


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PathFilterLandTest(LandFiltersTest):

    filterclass = PathFilterSet


class TestFilter(TopologyFilter):
    model = Topology


class TopologyFilterTest(TestCase):
    def test_value_to_edges(self):
        topology = TestFilter()

        with self.assertRaises(NotImplementedError):
            topology.value_to_edges('Value')


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class TopologyFilterTrailTest(TestCase):
    def setUp(self):
        self.path = PathFactory()
        self.trail = TrailFactory(paths=[(self.path, 0, 1)])

    def test_trail_filters(self):
        PathFactory()
        qs = PathFilterSet().qs
        self.assertEqual(qs.count(), 2)

        data = {'trail': self.trail}
        qs = PathFilterSet(data=data).qs
        self.assertEqual(qs.count(), 1)
