# -*- coding: utf-8 -*-

from django.test import TestCase

from caminae.land.factories import (
    PhysicalEdgeFactory, LandEdgeFactory, CompetenceEdgeFactory,
    WorkManagementEdgeFactory, SignageManagementEdgeFactory
)
from caminae.core.factories import PathFactory, PathAggregationFactory, getRandomLineStringInBounds, TopologyMixinFactory

from caminae.maintenance.filters import ProjectFilter, InterventionFilter
from caminae.maintenance.factories import InterventionFactory, ProjectFactory

class InterventionFilteringByLandTest(TestCase):

    def create_pair_of_distinct_path(self):
        return PathFactory(), PathFactory(geom=getRandomLineStringInBounds())

    def create_pair_of_distinct_by_topo_intervention(self):
        p1, seek_path = self.create_pair_of_distinct_path()

        topo_1 = TopologyMixinFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=topo_1, path=p1, start_position=0, end_position=1)

        seek_topo = TopologyMixinFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=seek_topo, path=seek_path, start_position=0, end_position=1)

        it_p1 = InterventionFactory.create(topology=topo_1)
        seek_it = InterventionFactory.create(topology=seek_topo)
        return seek_it, seek_path

    def test_filter_by_physical_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = PhysicalEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by physical type
        data = { 'physical_type': edge.physical_type.pk }

        qs = InterventionFilter(data=data).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)

    def test_filter_by_land_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = LandEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by land type
        data = { 'land_type': edge.land_type.pk }

        qs = InterventionFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)


    def test_filter_by_competence_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = CompetenceEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = { 'competence': edge.organization.pk }

        qs = InterventionFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)


    def test_filter_by_work_management_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = WorkManagementEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = { 'work': edge.organization.pk }

        qs = InterventionFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)


    def test_filter_by_signage_management_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = SignageManagementEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = { 'signage': edge.organization.pk }

        qs = InterventionFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)


class ProjectFilteringByLandTest(TestCase):

    def create_pair_of_distinct_path(self):
        return PathFactory(), PathFactory(geom=getRandomLineStringInBounds())

    def create_pair_of_distinct_by_topo_project(self):
        p1, seek_path = self.create_pair_of_distinct_path()

        topo_1 = TopologyMixinFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=topo_1, path=p1, start_position=0, end_position=1)

        seek_topo = TopologyMixinFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=seek_topo, path=seek_path, start_position=0, end_position=1)

        it_p1 = InterventionFactory.create(topology=topo_1)
        seek_it = InterventionFactory.create(topology=seek_topo)

        seek_proj = ProjectFactory.create()
        seek_proj.interventions.add(seek_it)

        proj_1 = ProjectFactory.create()
        proj_1.interventions.add(it_p1)

        return seek_proj, seek_path

    def test_filter_by_physical_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = PhysicalEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by physical type
        data = { 'physical_type': edge.physical_type.pk }

        qs = ProjectFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)

    def test_filter_by_land_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = LandEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by land type
        data = { 'land_type': edge.land_type.pk }

        qs = ProjectFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)


    def test_filter_by_competence_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = CompetenceEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = { 'competence': edge.organization.pk }

        qs = ProjectFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)


    def test_filter_by_work_management_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = WorkManagementEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = { 'work': edge.organization.pk }

        qs = ProjectFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)


    def test_filter_by_signage_management_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = SignageManagementEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = { 'signage': edge.organization.pk }

        qs = ProjectFilter(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)
