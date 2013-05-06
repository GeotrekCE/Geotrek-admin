# -*- coding: utf-8 -*-
from geotrek.land.tests.filters import LandFiltersTest

from geotrek.trekking.filters import TrekFilter
from geotrek.trekking.factories import TrekFactory


class TrekFilterLandTest(LandFiltersTest):

    filterclass = TrekFilter


    def create_pair_of_distinct_path(self):
        useless_path, seek_path = super(TrekFilterLandTest, self).create_pair_of_distinct_path()
        self.create_pair_of_distinct_topologies(TrekFactory, useless_path, seek_path)
        return useless_path, seek_path
