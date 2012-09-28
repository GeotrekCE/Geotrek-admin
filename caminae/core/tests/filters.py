# -*- coding: utf-8 -*-

from django.test import TestCase

from caminae.land.factories import (
    PhysicalEdgeFactory, LandEdgeFactory, CompetenceEdgeFactory,
    WorkManagementEdgeFactory, SignageManagementEdgeFactory
)

from caminae.core.models import Path
from caminae.core.factories import PathFactory, PathAggregationFactory, getRandomLineStringInBounds
from caminae.core.filters import PathFilter


class PathFilteringByLandTest(TestCase):

    def create_pair_of_distinct_path(self):
        return PathFactory(), PathFactory(geom=getRandomLineStringInBounds())

    def test_filter_by_physical_edge(self):
        _, seek_path = self.create_pair_of_distinct_path()

        edge = PhysicalEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by physical type
        data = { 'physical_type': edge.physical_type.pk }

        qs = PathFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_path)

    def test_filter_by_land_edge(self):
        _, seek_path = self.create_pair_of_distinct_path()

        edge = LandEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by land type
        data = { 'land_type': edge.land_type.pk }

        qs = PathFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_path)


    def test_filter_by_competence_edge(self):
        _, seek_path = self.create_pair_of_distinct_path()

        edge = CompetenceEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = { 'competence': edge.organization.pk }

        qs = PathFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_path)


    def test_filter_by_work_management_edge(self):
        _, seek_path = self.create_pair_of_distinct_path()

        edge = WorkManagementEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = { 'work': edge.organization.pk }

        qs = PathFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_path)


    def test_filter_by_signage_management_edge(self):
        _, seek_path = self.create_pair_of_distinct_path()

        edge = SignageManagementEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = { 'signage': edge.organization.pk }

        qs = PathFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_path)

