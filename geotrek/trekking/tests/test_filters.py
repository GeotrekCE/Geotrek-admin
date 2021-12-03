from geotrek.land.tests.test_filters import LandFiltersTest

from geotrek.trekking.filters import TrekFilterSet
from geotrek.trekking.tests.factories import TrekFactory


class TrekFilterLandTest(LandFiltersTest):

    filterclass = TrekFilterSet

    def test_land_filters_are_well_setup(self):
        filterset = TrekFilterSet()
        self.assertIn('work', filterset.filters)

    def create_pair_of_distinct_path(self):
        useless_path, seek_path = super().create_pair_of_distinct_path()
        self.create_pair_of_distinct_topologies(TrekFactory, useless_path, seek_path)
        return useless_path, seek_path
