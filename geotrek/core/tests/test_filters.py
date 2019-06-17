# -*- coding: utf-8 -*-
from django.test import tag

from geotrek.land.tests.test_filters import LandFiltersTest

from geotrek.core.filters import PathFilterSet


@tag('dynamic_segmentation')
class PathFilterLandTest(LandFiltersTest):

    filterclass = PathFilterSet
