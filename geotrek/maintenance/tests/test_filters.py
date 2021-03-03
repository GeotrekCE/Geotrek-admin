from unittest import skipIf

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

from geotrek.maintenance.filters import ProjectFilterSet, InterventionFilterSet
from geotrek.maintenance.factories import InterventionFactory, ProjectFactory
from geotrek.zoning.factories import CityFactory, DistrictFactory


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class InterventionFilteringByLandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        p1 = PathFactory()
        cls.seek_path = PathFactory(geom=getRandomLineStringInBounds())

        topo_1 = TopologyFactory.create(paths=[p1])
        seek_topo = TopologyFactory.create(paths=[cls.seek_path])

        InterventionFactory.create(target=topo_1)
        cls.seek_inter = InterventionFactory.create(target=seek_topo)

    def test_filter_by_physical_edge(self):
        edge = PhysicalEdgeFactory(paths=[self.seek_path])

        # filter by physical type
        data = {'physical_type': [edge.physical_type.pk]}

        qs = InterventionFilterSet(data=data).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    def test_filter_by_land_edge(self):
        edge = LandEdgeFactory(paths=[self.seek_path])

        # filter by land type
        data = {'land_type': [edge.land_type.pk]}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    def test_filter_by_competence_edge(self):
        edge = CompetenceEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {'competence': [edge.organization.pk]}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    def test_filter_by_work_management_edge(self):
        edge = WorkManagementEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {'work': [edge.organization.pk]}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    def test_filter_by_signage_management_edge(self):
        edge = SignageManagementEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {'signage': [edge.organization.pk]}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)


class ProjectFilteringByYearTest(TestCase):
    def test_filter_by_year(self):
        project = ProjectFactory.create(begin_year=2015, end_year=2017)
        ProjectFactory.create(begin_year=2011, end_year=2013)
        filterset = ProjectFilterSet(data={'year': [2016]})
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertEqual(len(filterset.qs), 1)
        self.assertEqual(filterset.qs[0], project)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class ProjectFilteringByLandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        p1 = PathFactory()
        cls.seek_path = PathFactory(geom=getRandomLineStringInBounds())

        topo_1 = TopologyFactory.create(paths=[p1])
        seek_topo = TopologyFactory.create(paths=[cls.seek_path])

        it_p1 = InterventionFactory.create(target=topo_1)
        seek_it = InterventionFactory.create(target=seek_topo)

        cls.seek_proj = ProjectFactory.create()
        cls.seek_proj.interventions.add(seek_it)

        proj_1 = ProjectFactory.create()
        proj_1.interventions.add(it_p1)

    def test_filter_by_physical_edge(self):
        edge = PhysicalEdgeFactory(paths=[self.seek_path])

        # filter by physical type
        data = {'physical_type': [edge.physical_type.pk]}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_proj)

    def test_filter_by_land_edge(self):
        edge = LandEdgeFactory(paths=[self.seek_path])

        # filter by land type
        data = {'land_type': [edge.land_type.pk]}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_proj)

    def test_filter_by_competence_edge(self):
        edge = CompetenceEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {'competence': [edge.organization.pk]}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_proj)

    def test_filter_by_work_management_edge(self):
        edge = WorkManagementEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {'work': [edge.organization.pk]}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_proj)

    def test_filter_by_signage_management_edge(self):
        edge = SignageManagementEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {'signage': [edge.organization.pk]}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_proj)


class ProjectIntersectionFilterCityTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.path_in = PathFactory.create(geom=LineString((0, 0), (2, 1), srid=settings.SRID))
            cls.path_out = PathFactory.create(geom=LineString((5, 5), (4, 4), srid=settings.SRID))
            cls.topo_in = TopologyFactory.create(paths=[cls.path_in])
            cls.topo_out = TopologyFactory.create(paths=[cls.path_out])
        else:
            cls.topo_in = TopologyFactory.create(geom=LineString((0, 0), (2, 1), srid=settings.SRID))
            cls.topo_out = TopologyFactory.create(geom=LineString((5, 5), (4, 4), srid=settings.SRID))
        cls.intervention_in = InterventionFactory.create(target=cls.topo_in)
        cls.intervention_out = InterventionFactory.create(target=cls.topo_out)
        cls.geom_zoning = MultiPolygon(Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID))

    def test_filter_in_city(self):
        filter = ProjectFilterSet(data={'city': [CityFactory.create(geom=self.geom_zoning)]})
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertTrue(filter.is_valid())
        self.assertIn(project_in, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_in_district(self):
        filter = ProjectFilterSet(data={'district': [DistrictFactory.create(geom=self.geom_zoning)]})
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertTrue(filter.is_valid())
        self.assertIn(project_in, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_out_city(self):
        filter = ProjectFilterSet(data={'city': [CityFactory.create(geom=self.geom_zoning)]})
        project_out = ProjectFactory.create()
        project_out.interventions.add(self.intervention_out)
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)

    def test_filter_out_district(self):
        filter = ProjectFilterSet(data={'district': [DistrictFactory.create(geom=self.geom_zoning)]})
        project_out = ProjectFactory.create()
        project_out.interventions.add(self.intervention_out)
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)
