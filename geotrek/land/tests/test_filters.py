# -*- coding: utf-8 -*-

from django.test import TestCase

from geotrek.core.factories import PathFactory, PathAggregationFactory, getRandomLineStringInBounds
from geotrek.land.factories import (
    PhysicalEdgeFactory, LandEdgeFactory, CompetenceEdgeFactory,
    WorkManagementEdgeFactory, SignageManagementEdgeFactory
)


class LandFiltersTest(TestCase):

    filterclass = None

    def create_pair_of_distinct_path(self):
        return PathFactory(), PathFactory(geom=getRandomLineStringInBounds())

    def create_pair_of_distinct_topologies(self, topologyfactoryclass, useless_path, seek_path):
        topo_1 = topologyfactoryclass(no_path=True)
        PathAggregationFactory.create(topo_object=topo_1, path=useless_path, start_position=0, end_position=1)
        seek_topo = topologyfactoryclass(no_path=True)
        PathAggregationFactory.create(topo_object=seek_topo, path=seek_path, start_position=0, end_position=1)
        return topo_1, seek_topo

    def _filter_by_edge(self, edgefactoryclass, key, getvalue):
        if self.filterclass is None:
            # Do not run abstract tests
            return
        useless_path, seek_path = self.create_pair_of_distinct_path()
        useless_edge, seek_edge = self.create_pair_of_distinct_topologies(edgefactoryclass, useless_path, seek_path)

        qs = self.filterclass().qs
        self.assertEqual(len(qs), 2)

        data = {key: getvalue(seek_edge)}
        qs = self.filterclass(data=data).qs
        self.assertEqual(len(qs), 1)

    def test_filter_by_physical_edge(self):
        self._filter_by_edge(PhysicalEdgeFactory, 'physical_type', lambda edge: edge.physical_type.pk)

    def test_filter_by_land_edge(self):
        self._filter_by_edge(LandEdgeFactory, 'land_type', lambda edge: edge.land_type.pk)

    def test_filter_by_competence_edge(self):
        self._filter_by_edge(CompetenceEdgeFactory, 'competence', lambda edge: edge.organization.pk)

    def test_filter_by_work_management_edge(self):
        self._filter_by_edge(WorkManagementEdgeFactory, 'work', lambda edge: edge.organization.pk)

    def test_filter_by_signage_management_edge(self):
        self._filter_by_edge(SignageManagementEdgeFactory, 'signage', lambda edge: edge.organization.pk)
