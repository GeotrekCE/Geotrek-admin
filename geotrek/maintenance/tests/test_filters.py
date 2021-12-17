from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, MultiPolygon, Polygon
from django.test import TestCase

from geotrek.land.tests.factories import (
    PhysicalEdgeFactory, LandEdgeFactory, CompetenceEdgeFactory,
    WorkManagementEdgeFactory, SignageManagementEdgeFactory
)
from geotrek.core.tests.factories import PathFactory, getRandomLineStringInBounds, TopologyFactory

# Make sure dynamic filters are set up when testing
from geotrek.land import filters  # noqa

from geotrek.maintenance.filters import ProjectFilterSet, InterventionFilterSet
from geotrek.maintenance.tests.factories import InterventionFactory, ProjectFactory
from geotrek.zoning.tests.factories import (CityFactory, DistrictFactory,
                                            RestrictedAreaFactory, RestrictedAreaTypeFactory)

if 'geotrek.outdoor' in settings.INSTALLED_APPS:
    from geotrek.outdoor.tests.factories import SiteFactory, CourseFactory


class InterventionFilteringByBboxTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seek_path = PathFactory(geom=getRandomLineStringInBounds())
        seek_topo = TopologyFactory.create(paths=[cls.seek_path])
        cls.seek_inter = InterventionFactory.create(target=seek_topo)

    def test_in_bbox(self):
        xmin, ymin, xmax, ymax = self.seek_inter.geom.transform(settings.API_SRID, clone=True).extent
        bbox = Polygon([[xmin - 1, ymin - 1], [xmin - 1, ymax + 1], [xmax + 1, ymax + 1], [xmax + 1, ymin - 1], [xmin - 1, ymin - 1]])
        qs = InterventionFilterSet({'bbox': bbox.wkt}).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    def test_out_bbox(self):
        xmin, ymin, xmax, ymax = self.seek_inter.geom.transform(settings.API_SRID, clone=True).extent
        bbox = Polygon([[xmax + 1, ymax + 1], [xmax + 1, ymax + 2], [xmax + 2, ymax + 2], [xmax + 2, ymax + 1], [xmax + 1, ymax + 1]])
        qs = InterventionFilterSet({'bbox': bbox.wkt}).qs
        self.assertEqual(len(qs), 0)


class InterventionZoningFilterTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.geom_1_wkt = 'SRID=2154;MULTIPOLYGON(((200000 300000, 900000 300000, 900000 1200000, 200000 1200000, ' \
                         '200000 300000)))'
        cls.geom_2_wkt = 'SRID=2154;MULTIPOLYGON(((1200000 300000, 1300000 300000, 1300000 1200000, 1200000 1200000, ' \
                         '1200000 300000)))'
        cls.city = CityFactory.create(name='city_in', geom=cls.geom_1_wkt)
        cls.city_2 = CityFactory.create(name='city_out', geom=cls.geom_2_wkt)
        cls.district = DistrictFactory.create(name='district_in', geom=cls.geom_1_wkt)
        cls.district_2 = DistrictFactory.create(name='district_out', geom=cls.geom_2_wkt)
        cls.area = RestrictedAreaFactory.create(name='area_in', geom=cls.geom_1_wkt)
        cls.area_2 = RestrictedAreaFactory.create(name='area_out', geom=cls.geom_2_wkt)
        cls.area_type_3 = RestrictedAreaTypeFactory.create()

    @classmethod
    def setUpTestData(cls):
        if not settings.TREKKING_TOPOLOGY_ENABLED:
            seek_topo = TopologyFactory.create(geom='SRID=2154;LINESTRING(200000 300000, 1100000 1200000)')
        else:
            cls.path = PathFactory.create(geom='SRID=2154;LINESTRING(200000 300000, 1100000 1200000)')
            seek_topo = TopologyFactory.create(paths=[cls.path])
        cls.seek_inter = InterventionFactory.create(target=seek_topo)

    def test_filter_zoning_city(self):
        filter = InterventionFilterSet(data={'city': [self.city, ]})

        self.assertIn(self.seek_inter, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = InterventionFilterSet(data={'city': [self.city_2, ]})

        self.assertEqual(len(filter.qs), 0)

    def test_filter_zoning_district(self):
        filter = InterventionFilterSet(data={'district': [self.district, ]})

        self.assertIn(self.seek_inter, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = InterventionFilterSet(data={'district': [self.district_2, ]})

        self.assertEqual(len(filter.qs), 0)

    def test_filter_zoning_area_type(self):
        filter = InterventionFilterSet(data={'area_type': [self.area.area_type, ]})

        self.assertIn(self.seek_inter, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = InterventionFilterSet(data={'area_type': [self.area_2.area_type, ]})
        self.assertEqual(len(filter.qs), 0)

        filter = InterventionFilterSet(data={'area_type': [self.area_type_3, ]})
        self.assertEqual(len(filter.qs), 0)


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

        if 'geotrek.outdoor' in settings.INSTALLED_APPS:
            site = SiteFactory()
            cls.seek_site = InterventionFactory.create(target=site)

            outdoor = CourseFactory()
            cls.seek_course = InterventionFactory.create(target=outdoor)

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

    @skipIf('geotrek.outdoor' not in settings.INSTALLED_APPS, 'Outdoor module not installed')
    def test_filter_by_target_site(self):
        # filter by target
        data = {'on': 'site'}
        qs = InterventionFilterSet(data=data).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_site)

    @skipIf('geotrek.outdoor' not in settings.INSTALLED_APPS, 'Outdoor module not installed')
    def test_filter_by_target_course(self):
        # filter by target
        data = {'on': 'course'}
        qs = InterventionFilterSet(data=data).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_course)


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


class ProjectIntersectionFilterZoningTest(TestCase):
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

    def test_filter_in_restricted_area(self):
        filter = ProjectFilterSet(data={'area': [RestrictedAreaFactory.create(geom=self.geom_zoning)]})
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertTrue(filter.is_valid())
        self.assertIn(project_in, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_in_restricted_area_type(self):
        restricted_area_type = RestrictedAreaTypeFactory.create()
        RestrictedAreaFactory.create(geom=self.geom_zoning, area_type=restricted_area_type)
        filter = ProjectFilterSet(data={'area_type': [restricted_area_type.pk]})
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertTrue(filter.is_valid())
        self.assertIn(project_in, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_out_restricted_area(self):
        filter = ProjectFilterSet(data={'area': [RestrictedAreaFactory.create(geom=self.geom_zoning)]})
        project_out = ProjectFactory.create()
        project_out.interventions.add(self.intervention_out)
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)

    def test_filter_out_restricted_area_type(self):
        restricted_area_type = RestrictedAreaTypeFactory.create()
        RestrictedAreaFactory.create(geom=self.geom_zoning, area_type=restricted_area_type)
        filter = ProjectFilterSet(data={'area_type': [restricted_area_type.pk]})
        project_out = ProjectFactory.create()
        project_out.interventions.add(self.intervention_out)
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)

    def test_filter_restricted_area_type_without_restricted_area(self):
        restricted_area_type = RestrictedAreaTypeFactory.create()
        filter = ProjectFilterSet(data={'area_type': [restricted_area_type.pk]})
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)
