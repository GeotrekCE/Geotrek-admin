# -*- coding: utf-8 -*-
from geotrek.land.tests.test_filters import LandFiltersTest

from geotrek.core.filters import PathFilterSet


class PathFilterLandTest(LandFiltersTest):

    filterclass = PathFilterSet
