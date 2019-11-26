from unittest import skipIf

from django.conf import settings

from geotrek.land.tests.test_filters import LandFiltersTest

from geotrek.core.filters import PathFilterSet


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PathFilterLandTest(LandFiltersTest):

    filterclass = PathFilterSet
