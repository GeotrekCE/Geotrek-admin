from unittest import skipIf

from django.conf import settings
from django.test import TestCase

# Make sure dynamic filters are set up when testing
from geotrek.land import filters  # noqa

from geotrek.core.tests.factories import PathFactory, getRandomLineStringInBounds
from geotrek.land.tests.factories import (
    PhysicalEdgeFactory, LandEdgeFactory, CompetenceEdgeFactory,
    WorkManagementEdgeFactory, SignageManagementEdgeFactory,
    CirculationEdgeFactory
)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class LandFiltersTest(TestCase):

    filterclass = None

    def create_pair_of_distinct_path(self):
        return PathFactory(), PathFactory(geom=getRandomLineStringInBounds())

    def create_pair_of_distinct_topologies(self, topologyfactoryclass, useless_path, seek_path):
        topo_1 = topologyfactoryclass(paths=[useless_path])
        seek_topo = topologyfactoryclass(paths=[seek_path])
        return topo_1, seek_topo

    def _filter_by_edge(self, edgefactoryclass, key, getvalue):
        if self.filterclass is None:
            # Do not run abstract tests
            return
        useless_path, seek_path = self.create_pair_of_distinct_path()
        useless_edge, seek_edge = self.create_pair_of_distinct_topologies(edgefactoryclass, useless_path, seek_path)

        qs = self.filterclass().qs
        self.assertEqual(len(qs), 2)

        data = {key: []}
        qs = self.filterclass(data=data).qs
        self.assertEqual(len(qs), 2)

        data = {key: [getvalue(seek_edge)]}
        qs = self.filterclass(data=data).qs
        self.assertEqual(len(qs), 1)

        data = {key: [getvalue(seek_edge), getvalue(useless_edge)]}
        qs = self.filterclass(data=data).qs
        self.assertEqual(len(qs), 2)

    def test_filter_by_physical_edge(self):
        self._filter_by_edge(PhysicalEdgeFactory, 'physical_type', lambda edge: edge.physical_type.pk)

    def test_filter_by_land_edge(self):
        self._filter_by_edge(LandEdgeFactory, 'land_type', lambda edge: edge.land_type.pk)

    def test_filter_by_circulation_type(self):
        self._filter_by_edge(CirculationEdgeFactory, 'circulation_type', lambda edge: edge.circulation_type.pk)

    def test_filter_by_authorization_type(self):
        self._filter_by_edge(CirculationEdgeFactory, 'authorization_type', lambda edge: edge.authorization_type.pk)

    def test_filter_by_competence_edge(self):
        self._filter_by_edge(CompetenceEdgeFactory, 'competence', lambda edge: edge.organization.pk)

    def test_filter_by_work_management_edge(self):
        self._filter_by_edge(WorkManagementEdgeFactory, 'work', lambda edge: edge.organization.pk)

    def test_filter_by_signage_management_edge(self):
        self._filter_by_edge(SignageManagementEdgeFactory, 'signage', lambda edge: edge.organization.pk)
