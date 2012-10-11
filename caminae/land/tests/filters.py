# -*- coding: utf-8 -*-

from django.test import TestCase

from caminae.land.factories import (
    PhysicalEdgeFactory, LandEdgeFactory, CompetenceEdgeFactory,
    WorkManagementEdgeFactory, SignageManagementEdgeFactory
)

from caminae.core.factories import PathFactory, PathAggregationFactory, getRandomLineStringInBounds
from caminae.core.filters import PathFilter


class PathFilteringByLandTest(TestCase):

    def create_pair_of_distinct_path(self):
        return PathFactory(), PathFactory(geom=getRandomLineStringInBounds())

    def _filter_by_edge(self, klassedgefactory, key, getvalue):
        useless_path, seek_path = self.create_pair_of_distinct_path()
        
        edge = klassedgefactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()
        data = {key : getvalue(edge)}
        
        qs = PathFilter().qs
        self.assertEqual(len(qs), 2)
        
        qs = PathFilter(data=data).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_path)

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
