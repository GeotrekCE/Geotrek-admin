from unittest import skipIf

from datetime import datetime

from django.conf import settings
from django.contrib.gis.geos import LineString, MultiPolygon, Polygon
from django.test import TestCase

from geotrek.land.factories import (
    PhysicalEdgeFactory, LandEdgeFactory, CompetenceEdgeFactory,
    WorkManagementEdgeFactory, SignageManagementEdgeFactory
)
from geotrek.core.factories import PathFactory, getRandomLineStringInBounds, TopologyFactory

# Make sure dynamic filters are set up when testing
from geotrek.land import filters  # noqa

from geotrek.maintenance.filters import (ProjectFilterSet, InterventionFilterSet,
                                         InterventionYearSelect, ProjectYearSelect)
from geotrek.maintenance.factories import (InterventionFactory, ProjectFactory,
                                           InfrastructureInterventionFactory)
from geotrek.zoning.factories import CityFactory, DistrictFactory


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class InterventionFilteringByLandTest(TestCase):

    def create_pair_of_distinct_path(self):
        return PathFactory(), PathFactory(geom=getRandomLineStringInBounds())

    def create_pair_of_distinct_by_topo_intervention(self):
        p1, seek_path = self.create_pair_of_distinct_path()

        topo_1 = TopologyFactory.create(paths=[p1])

        seek_topo = TopologyFactory.create(paths=[seek_path])

        InterventionFactory.create(target=topo_1)
        seek_it = InterventionFactory.create(target=seek_topo)
        return seek_it, seek_path

    def test_filter_by_physical_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = PhysicalEdgeFactory(paths=[seek_path])

        # filter by physical type
        data = {'physical_type': edge.physical_type.pk}

        qs = InterventionFilterSet(data=data).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)

    def test_filter_by_land_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = LandEdgeFactory(paths=[seek_path])

        # filter by land type
        data = {'land_type': edge.land_type.pk}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)

    def test_filter_by_competence_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = CompetenceEdgeFactory(paths=[seek_path])

        # filter by organization
        data = {'competence': edge.organization.pk}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)

    def test_filter_by_work_management_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = WorkManagementEdgeFactory(paths=[seek_path])

        # filter by organization
        data = {'work': edge.organization.pk}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)

    def test_filter_by_signage_management_edge(self):
        seek_inter, seek_path = self.create_pair_of_distinct_by_topo_intervention()

        edge = SignageManagementEdgeFactory(paths=[seek_path])

        # filter by organization
        data = {'signage': edge.organization.pk}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_inter)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class ProjectFilteringByLandTest(TestCase):

    def create_pair_of_distinct_path(self):
        return PathFactory(), PathFactory(geom=getRandomLineStringInBounds())

    def create_pair_of_distinct_by_topo_project(self):
        p1, seek_path = self.create_pair_of_distinct_path()

        topo_1 = TopologyFactory.create(paths=[p1])

        seek_topo = TopologyFactory.create(paths=[seek_path])

        it_p1 = InterventionFactory.create(target=topo_1)
        seek_it = InterventionFactory.create(target=seek_topo)

        seek_proj = ProjectFactory.create()
        seek_proj.interventions.add(seek_it)

        proj_1 = ProjectFactory.create()
        proj_1.interventions.add(it_p1)

        return seek_proj, seek_path

    def test_filter_by_physical_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = PhysicalEdgeFactory(paths=[seek_path])

        # filter by physical type
        data = {'physical_type': edge.physical_type.pk}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)

    def test_filter_by_land_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = LandEdgeFactory(paths=[seek_path])

        # filter by land type
        data = {'land_type': edge.land_type.pk}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)

    def test_filter_by_competence_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = CompetenceEdgeFactory(paths=[seek_path])

        # filter by organization
        data = {'competence': edge.organization.pk}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)

    def test_filter_by_work_management_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = WorkManagementEdgeFactory(paths=[seek_path])

        # filter by organization
        data = {'work': edge.organization.pk}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], seek_proj)

    def test_filter_by_signage_management_edge(self):
        seek_proj, seek_path = self.create_pair_of_distinct_by_topo_project()

        edge = SignageManagementEdgeFactory(paths=[seek_path])

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
        output = self.widget.render(name='year', value=None, renderer=None)
        self.assertEqual(type(self.widget), InterventionYearSelect)
        self.assertEqual(output.count('<option'), 3)
        self.assertIn('>2012<', output)
        self.assertIn('>1932<', output)


class ProjectYearsFilterTest(TestCase):
    def setUp(self):
        ProjectFactory.create(begin_year=1500, end_year=2000)
        ProjectFactory.create(begin_year=1700, end_year=1800)
        self.filter = ProjectFilterSet()
        self.widget = self.filter.filters['in_year'].field.widget

    def test_year_choices_come_from_project(self):
        output = self.widget.render(name='project', value=None, renderer=None)
        self.assertEqual(type(self.widget), ProjectYearSelect)
        self.assertEqual(output.count('<option'), 5)
        self.assertIn('>1500<', output)
        self.assertIn('>1700<', output)
        self.assertIn('>1800<', output)
        self.assertIn('>2000<', output)

    def test_new_projects_can_be_filtered_on_new_years(self):
        filter = ProjectFilterSet(data={'in_year': 1250})
        p = ProjectFactory.create(begin_year=1200, end_year=1300)
        self.assertIn(p, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_year_with_string(self):
        filter = ProjectFilterSet(data={'in_year': 'toto'})
        p = ProjectFactory.create(begin_year=1200, end_year=1300)
        self.assertIn(p, filter.qs)
        self.assertEqual(len(filter.qs), 3)
        # We get all project if it's a wrong filter


class ProjectIntersectionFilterCityTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProjectIntersectionFilterCityTest, cls).setUpClass()
        cls.path_in = PathFactory.create(geom=LineString((0, 0), (2, 1), srid=settings.SRID))
        cls.path_out = PathFactory.create(geom=LineString((5, 5), (4, 4), srid=settings.SRID))
        cls.topo_in = TopologyFactory.create(paths=[cls.path_in])
        cls.topo_out = TopologyFactory.create(paths=[cls.path_out])
        cls.intervention_in = InterventionFactory.create(target=cls.topo_in)
        cls.intervention_out = InterventionFactory.create(target=cls.topo_out)
        cls.geom_district = MultiPolygon(Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID))

    def test_filter_in_city(self):
        filter = ProjectFilterSet(data={'city': CityFactory.create(geom=self.geom_district)})
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertIn(project_in, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_in_district(self):
        filter = ProjectFilterSet(data={'district': DistrictFactory.create(geom=self.geom_district)})
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertIn(project_in, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_out_city(self):
        filter = ProjectFilterSet(data={'city': CityFactory.create(geom=self.geom_district)})
        project_out = ProjectFactory.create()
        project_out.interventions.add(self.intervention_out)
        self.assertEqual(len(filter.qs), 0)

    def test_filter_out_district(self):
        filter = ProjectFilterSet(data={'district': DistrictFactory.create(geom=self.geom_district)})
        project_out = ProjectFactory.create()
        project_out.interventions.add(self.intervention_out)
        self.assertEqual(len(filter.qs), 0)
