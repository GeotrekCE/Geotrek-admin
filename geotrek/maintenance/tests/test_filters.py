# -*- coding: utf-8 -*-
from datetime import datetime

from django.test import TestCase

from geotrek.land.factories import (
    PhysicalEdgeFactory, LandEdgeFactory, CompetenceEdgeFactory,
    WorkManagementEdgeFactory, SignageManagementEdgeFactory
)
from geotrek.core.factories import PathFactory, PathAggregationFactory, getRandomLineStringInBounds, TopologyFactory

from geotrek.maintenance.filters import (ProjectFilterSet, InterventionFilterSet,
                                         InterventionYearSelect, ProjectYearSelect)
from geotrek.maintenance.factories import (InterventionFactory, ProjectFactory,
                                           InfrastructureInterventionFactory)


class InterventionFilteringByLandTest(TestCase):

    def create_pair_of_distinct_path(self):
        return PathFactory(), PathFactory(geom=getRandomLineStringInBounds())

    def create_pair_of_distinct_by_topo_intervention(self):
        p1, seek_path = self.create_pair_of_distinct_path()

        topo_1 = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=topo_1, path=p1, start_position=0, end_position=1)

        seek_topo = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=seek_topo, path=seek_path, start_position=0, end_position=1)

        InterventionFactory.create(topology=topo_1)
        seek_it = InterventionFactory.create(topology=seek_topo)
        return seek_it, seek_path

    def test_filter_by_physical_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = PhysicalEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by physical type
        data = {'physical_type': edge.physical_type.pk}

        qs = InterventionFilterSet(data=data).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)

    def test_filter_by_land_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = LandEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by land type
        data = {'land_type': edge.land_type.pk}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)

    def test_filter_by_competence_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = CompetenceEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = {'competence': edge.organization.pk}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)

    def test_filter_by_work_management_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = WorkManagementEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = {'work': edge.organization.pk}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)

    def test_filter_by_signage_management_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = SignageManagementEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = {'signage': edge.organization.pk}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)


class ProjectFilteringByLandTest(TestCase):

    def create_pair_of_distinct_path(self):
        return PathFactory(), PathFactory(geom=getRandomLineStringInBounds())

    def create_pair_of_distinct_by_topo_project(self):
        p1, seek_path = self.create_pair_of_distinct_path()

        topo_1 = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=topo_1, path=p1, start_position=0, end_position=1)

        seek_topo = TopologyFactory.create(no_path=True)
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

        # filter by physical type
        data = {'physical_type': edge.physical_type.pk}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)

    def test_filter_by_land_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = LandEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by land type
        data = {'land_type': edge.land_type.pk}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)

    def test_filter_by_competence_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = CompetenceEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = {'competence': edge.organization.pk}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)

    def test_filter_by_work_management_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = WorkManagementEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = {'work': edge.organization.pk}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)

    def test_filter_by_signage_management_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = SignageManagementEdgeFactory(no_path=True)
        PathAggregationFactory.create(topo_object=edge, path=seek_path, start_position=0, end_position=1)
        edge.reload()

        # filter by organization
        data = {'signage': edge.organization.pk}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)


class InterventionYearsFilterTest(TestCase):
    def setUp(self):
        InfrastructureInterventionFactory.create(date=datetime(2012, 11, 10))
        InfrastructureInterventionFactory.create(date=datetime(1932, 11, 10))
        self.filter = InterventionFilterSet()
        self.widget = self.filter.filters['year'].field.widget

    def test_year_choices_come_from_interventions(self):
        output = self.widget.render(name='year', value=None)
        self.assertEqual(type(self.widget), InterventionYearSelect)
        self.assertEqual(output.count('<option'), 3)
        self.assertIn('>2012<', output)
        self.assertIn('>1932<', output)

    def test_new_interventions_appear_dynamically(self):
        InfrastructureInterventionFactory.create(date=datetime(2024, 11, 10))
        output = self.widget.render(name='year', value=None)
        self.assertEqual(output.count('<option'), 4)
        self.assertIn('>2024<', output)


class ProjectYearsFilterTest(TestCase):
    def setUp(self):
        ProjectFactory.create(begin_year=1500, end_year=2000)
        ProjectFactory.create(begin_year=1700, end_year=1800)
        self.filter = ProjectFilterSet()
        self.widget = self.filter.filters['in_year'].field.widget

    def test_year_choices_come_from_project(self):
        output = self.widget.render(name='project', value=None)
        self.assertEqual(type(self.widget), ProjectYearSelect)
        self.assertEqual(output.count('<option'), 5)
        self.assertIn('>1500<', output)
        self.assertIn('>1700<', output)
        self.assertIn('>1800<', output)
        self.assertIn('>2000<', output)

    def test_new_projects_appear_dynamically(self):
        ProjectFactory.create(begin_year=1500, end_year=2100)
        output = self.widget.render(name='year', value=None)
        self.assertEqual(output.count('<option'), 6)
        self.assertIn('>2100<', output)

    def test_new_projects_can_be_filtered_on_new_years(self):
        filter = ProjectFilterSet(data={'in_year': 1250})
        p = ProjectFactory.create(begin_year=1200, end_year=1300)
        self.assertIn(p, filter.qs)
        self.assertEqual(len(filter.qs), 1)
