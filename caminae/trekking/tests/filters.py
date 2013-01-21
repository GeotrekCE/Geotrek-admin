# -*- coding: utf-8 -*-
from caminae.land.tests.filters import LandFiltersTest

from caminae.trekking.filters import TrekFilter
from caminae.trekking.factories import TrekFactory


class TrekFilterLandTest(LandFiltersTest):

    filterclass = TrekFilter


    def create_pair_of_distinct_path(self):
        useless_path, seek_path = super(TrekFilterLandTest, self).create_pair_of_distinct_path()
        self.create_pair_of_distinct_topologies(TrekFactory, useless_path, seek_path)
        return useless_path, seek_path
