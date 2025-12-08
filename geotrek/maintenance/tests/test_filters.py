from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import (
    GeometryCollection,
    LineString,
    MultiPolygon,
    Point,
    Polygon,
)
from django.test import TestCase

from geotrek.core.tests.factories import (
    PathFactory,
    TopologyFactory,
    getRandomLineStringInBounds,
)
from geotrek.feedback.tests.factories import ReportFactory

# Make sure dynamic filters are set up when testing
from geotrek.land import filters  # noqa
from geotrek.land.tests.factories import (
    CompetenceEdgeFactory,
    LandEdgeFactory,
    PhysicalEdgeFactory,
    SignageManagementEdgeFactory,
    WorkManagementEdgeFactory,
)
from geotrek.maintenance.filters import InterventionFilterSet, ProjectFilterSet
from geotrek.maintenance.tests.factories import (
    ContractorFactory,
    InterventionFactory,
    ProjectFactory,
)
from geotrek.outdoor.tests.factories import CourseFactory, SiteFactory
from geotrek.signage.tests.factories import BladeFactory, SignageFactory
from geotrek.zoning.tests.factories import (
    CityFactory,
    DistrictFactory,
    RestrictedAreaFactory,
    RestrictedAreaTypeFactory,
)


class InterventionFilteringByBboxTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.seek_path = PathFactory(geom=getRandomLineStringInBounds())
        seek_topo = TopologyFactory.create(paths=[cls.seek_path])
        cls.seek_inter = InterventionFactory.create(target=seek_topo)

    def test_in_bbox(self):
        xmin, ymin, xmax, ymax = self.seek_inter.geom.transform(
            settings.API_SRID, clone=True
        ).extent
        bbox = Polygon(
            [
                [xmin - 1, ymin - 1],
                [xmin - 1, ymax + 1],
                [xmax + 1, ymax + 1],
                [xmax + 1, ymin - 1],
                [xmin - 1, ymin - 1],
            ]
        )
        qs = InterventionFilterSet({"bbox": bbox.wkt}).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    def test_out_bbox(self):
        xmin, ymin, xmax, ymax = self.seek_inter.geom.transform(
            settings.API_SRID, clone=True
        ).extent
        bbox = Polygon(
            [
                [xmax + 1, ymax + 1],
                [xmax + 1, ymax + 2],
                [xmax + 2, ymax + 2],
                [xmax + 2, ymax + 1],
                [xmax + 1, ymax + 1],
            ]
        )
        qs = InterventionFilterSet({"bbox": bbox.wkt}).qs
        self.assertEqual(len(qs), 0)


class InterventionZoningFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.geom_1_wkt = (
            "SRID=2154;MULTIPOLYGON(((200000 300000, 900000 300000, 900000 1200000, 200000 1200000, "
            "200000 300000)))"
        )
        cls.geom_2_wkt = (
            "SRID=2154;MULTIPOLYGON(((1200000 300000, 1300000 300000, 1300000 1200000, 1200000 1200000, "
            "1200000 300000)))"
        )
        cls.city = CityFactory.create(name="city_in", geom=cls.geom_1_wkt)
        cls.city_2 = CityFactory.create(name="city_out", geom=cls.geom_2_wkt)
        cls.district = DistrictFactory.create(name="district_in", geom=cls.geom_1_wkt)
        cls.district_2 = DistrictFactory.create(
            name="district_out", geom=cls.geom_2_wkt
        )
        cls.area = RestrictedAreaFactory.create(name="area_in", geom=cls.geom_1_wkt)
        cls.area_2 = RestrictedAreaFactory.create(name="area_out", geom=cls.geom_2_wkt)
        cls.area_type_3 = RestrictedAreaTypeFactory.create()
        if not settings.TREKKING_TOPOLOGY_ENABLED:
            seek_topo = TopologyFactory.create(
                geom="SRID=2154;LINESTRING(200000 300000, 1100000 1200000)"
            )
        else:
            cls.path = PathFactory.create(
                geom="SRID=2154;LINESTRING(200000 300000, 1100000 1200000)"
            )
            seek_topo = TopologyFactory.create(paths=[cls.path])
        cls.seek_inter = InterventionFactory.create(target=seek_topo)

    def test_filter_zoning_city(self):
        filter = InterventionFilterSet(
            data={
                "city": [
                    self.city,
                ]
            }
        )

        self.assertIn(self.seek_inter, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = InterventionFilterSet(
            data={
                "city": [
                    self.city_2,
                ]
            }
        )

        self.assertEqual(len(filter.qs), 0)

    def test_filter_zoning_district(self):
        filter = InterventionFilterSet(
            data={
                "district": [
                    self.district,
                ]
            }
        )

        self.assertIn(self.seek_inter, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = InterventionFilterSet(
            data={
                "district": [
                    self.district_2,
                ]
            }
        )

        self.assertEqual(len(filter.qs), 0)

    def test_filter_zoning_area_type(self):
        filter = InterventionFilterSet(
            data={
                "area_type": [
                    self.area.area_type,
                ]
            }
        )

        self.assertIn(self.seek_inter, filter.qs)
        self.assertEqual(len(filter.qs), 1)

        filter = InterventionFilterSet(
            data={
                "area_type": [
                    self.area_2.area_type,
                ]
            }
        )
        self.assertEqual(len(filter.qs), 0)

        filter = InterventionFilterSet(
            data={
                "area_type": [
                    self.area_type_3,
                ]
            }
        )
        self.assertEqual(len(filter.qs), 0)


class InterventionDateFilterTest(TestCase):
    def test_filter_year_without_end_date(self):
        InterventionFactory(name="intervention1", begin_date="2020-07-30")
        InterventionFactory(name="intervention1", begin_date="2021-07-30")
        InterventionFactory(name="intervention1", begin_date="2022-07-30")
        intervention_filter = InterventionFilterSet({"year": [2021]})
        self.assertEqual(intervention_filter.qs.count(), 1)

    def test_filter_year_with_range(self):
        InterventionFactory(
            name="intervention1", begin_date="2020-07-30", end_date="2024-07-30"
        )
        InterventionFactory(name="intervention1", begin_date="2021-07-30")
        InterventionFactory(
            name="intervention1", begin_date="2022-07-30", end_date="2024-07-30"
        )
        intervention_filter = InterventionFilterSet({"year": [2022]})
        self.assertEqual(intervention_filter.qs.count(), 2)

    def test_filter_year_with_end_date(self):
        InterventionFactory(
            name="intervention1", begin_date="2020-07-30", end_date="2023-07-30"
        )
        InterventionFactory(name="intervention1", begin_date="2021-07-30")
        InterventionFactory(
            name="intervention1", begin_date="2022-07-30", end_date="2024-07-30"
        )
        intervention_filter = InterventionFilterSet({"year": [2023, 2024]})
        self.assertEqual(intervention_filter.qs.count(), 2)


class InterventionContractorsFilterTest(TestCase):
    def test_filter_without_contractors(self):
        project = ProjectFactory.create()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            InterventionFactory.create(project=project)
        else:
            InterventionFactory.create(
                project=project, geom="SRID=2154;POINT (700000 6600000)"
            )

        project_filter = ProjectFilterSet({})

        self.assertEqual(project_filter.qs.count(), 1)

    def test_filter_with_project_contractors(self):
        contractor = ContractorFactory.create()
        project = ProjectFactory.create()
        project.contractors.set([contractor])

        if settings.TREKKING_TOPOLOGY_ENABLED:
            InterventionFactory.create(project=project)
        else:
            InterventionFactory.create(
                project=project, geom="SRID=2154;POINT (700000 6600000)"
            )

        project_filter = ProjectFilterSet({"contractors": [contractor]})
        self.assertEqual(project_filter.qs.count(), 1)

    def test_filter_with_intervention_contractors(self):
        contractor = ContractorFactory.create()
        contractor_2 = ContractorFactory.create()
        project = ProjectFactory.create()
        project.contractors.set([contractor_2])

        if settings.TREKKING_TOPOLOGY_ENABLED:
            inter = InterventionFactory.create(project=project)
        else:
            inter = InterventionFactory.create(
                project=project, geom="SRID=2154;POINT (700000 6600000)"
            )
        inter.contractors.set([contractor])

        project_filter = ProjectFilterSet({"contractors": [contractor]})
        self.assertEqual(project_filter.qs.count(), 1)

    def test_filter_with_project_and_intervention_contractors(self):
        contractor = ContractorFactory.create()
        contractor_2 = ContractorFactory.create()
        ContractorFactory.create()
        project = ProjectFactory.create()
        project.contractors.set([contractor_2])

        if settings.TREKKING_TOPOLOGY_ENABLED:
            inter = InterventionFactory.create(project=project)
        else:
            inter = InterventionFactory.create(
                project=project, geom="SRID=2154;POINT (700000 6600000)"
            )
        inter.contractors.set([contractor])

        project_filter = ProjectFilterSet({"contractors": [contractor, contractor_2]})
        self.assertEqual(project_filter.qs.count(), 1)

    def test_filter_with_project_and_intervention_contractors_not_match(self):
        contractor = ContractorFactory.create()
        contractor_2 = ContractorFactory.create()
        contractor_3 = ContractorFactory.create()
        project = ProjectFactory.create()
        project.contractors.set([contractor_2])

        if settings.TREKKING_TOPOLOGY_ENABLED:
            inter = InterventionFactory.create(project=project)
        else:
            inter = InterventionFactory.create(
                project=project, geom="SRID=2154;POINT (700000 6600000)"
            )
        inter.contractors.set([contractor])

        project_filter = ProjectFilterSet({"contractors": [contractor_3]})
        self.assertEqual(project_filter.qs.count(), 0)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class InterventionFilteringByLandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        p1 = PathFactory()
        cls.seek_path = PathFactory(geom=getRandomLineStringInBounds())

        topo_1 = TopologyFactory.create(paths=[p1])
        seek_topo = TopologyFactory.create(paths=[cls.seek_path])

        InterventionFactory.create(target=topo_1)
        cls.seek_inter = InterventionFactory.create(target=seek_topo)

        if "geotrek.outdoor" in settings.INSTALLED_APPS:
            site = SiteFactory()
            cls.seek_site = InterventionFactory.create(target=site)

            outdoor = CourseFactory()
            cls.seek_course = InterventionFactory.create(target=outdoor)

    def test_filter_by_physical_edge(self):
        edge = PhysicalEdgeFactory(paths=[self.seek_path])

        # filter by physical type
        data = {"physical_type": [edge.physical_type.pk]}

        qs = InterventionFilterSet(data=data).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    def test_filter_by_land_edge(self):
        edge = LandEdgeFactory(paths=[self.seek_path])

        # filter by land type
        data = {"land_type": [edge.land_type.pk]}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    def test_filter_by_competence_edge(self):
        edge = CompetenceEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {"competence": [edge.organization.pk]}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    def test_filter_by_work_management_edge(self):
        edge = WorkManagementEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {"work": [edge.organization.pk]}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    def test_filter_by_signage_management_edge(self):
        edge = SignageManagementEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {"signage": [edge.organization.pk]}

        qs = InterventionFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_inter)

    @skipIf(
        "geotrek.outdoor" not in settings.INSTALLED_APPS, "Outdoor module not installed"
    )
    def test_filter_by_target_site(self):
        # filter by target
        data = {"on": "site"}
        qs = InterventionFilterSet(data=data).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_site)

    @skipIf(
        "geotrek.outdoor" not in settings.INSTALLED_APPS, "Outdoor module not installed"
    )
    def test_filter_by_target_course(self):
        # filter by target
        data = {"on": "course"}
        qs = InterventionFilterSet(data=data).qs
        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_course)


class ProjectFilteringByYearTest(TestCase):
    def test_filter_by_year(self):
        project = ProjectFactory.create(begin_year=2015, end_year=2017)
        ProjectFactory.create(begin_year=2011, end_year=2013)
        filterset = ProjectFilterSet(data={"year": [2016]})
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertEqual(len(filterset.qs), 1)
        self.assertEqual(filterset.qs[0], project)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
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
        data = {"physical_type": [edge.physical_type.pk]}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_proj)

    def test_filter_by_land_edge(self):
        edge = LandEdgeFactory(paths=[self.seek_path])

        # filter by land type
        data = {"land_type": [edge.land_type.pk]}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_proj)

    def test_filter_by_competence_edge(self):
        edge = CompetenceEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {"competence": [edge.organization.pk]}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_proj)

    def test_filter_by_work_management_edge(self):
        edge = WorkManagementEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {"work": [edge.organization.pk]}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_proj)

    def test_filter_by_signage_management_edge(self):
        edge = SignageManagementEdgeFactory(paths=[self.seek_path])

        # filter by organization
        data = {"signage": [edge.organization.pk]}

        qs = ProjectFilterSet(data=data).qs

        self.assertEqual(len(qs), 1)
        self.assertEqual(qs[0], self.seek_proj)


class InterventionIntersectionFilterZoningTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.path_in_1 = PathFactory.create(
                geom=LineString((0, 0), (2, 1), srid=settings.SRID)
            )
            cls.path_in_2 = PathFactory.create(
                geom=LineString((5, 5), (4, 4), srid=settings.SRID)
            )
            cls.topo_in_1 = TopologyFactory.create(paths=[cls.path_in_1])
            cls.topo_in_2 = TopologyFactory.create(paths=[cls.path_in_2])
            signage_in_1 = SignageFactory.create(paths=[cls.path_in_1])
            signage_in_2 = SignageFactory.create(paths=[cls.path_in_2])
        else:
            cls.topo_in_1 = TopologyFactory.create(
                geom=LineString((0, 0), (2, 1), srid=settings.SRID)
            )
            cls.topo_in_2 = TopologyFactory.create(
                geom=LineString((5, 5), (4, 4), srid=settings.SRID)
            )
            signage_in_1 = SignageFactory.create(geom=Point(1, 1, srid=settings.SRID))
            signage_in_2 = SignageFactory.create(geom=Point(5, 5, srid=settings.SRID))
        cls.intervention_topology_in_1 = InterventionFactory.create(
            target=cls.topo_in_1
        )
        cls.intervention_topology_in_2 = InterventionFactory.create(
            target=cls.topo_in_2
        )

        cls.site_in_1 = SiteFactory.create(
            geom=GeometryCollection(Point(1, 1), srid=settings.SRID)
        )
        cls.intervention_site_in_1 = InterventionFactory.create(target=cls.site_in_1)

        cls.course_in_1 = CourseFactory.create(
            parent_sites=[cls.site_in_1.pk],
            geom=GeometryCollection(Point(1, 1), srid=settings.SRID),
        )
        cls.intervention_course_in_1 = InterventionFactory.create(
            target=cls.course_in_1
        )

        cls.site_in_2 = SiteFactory.create(
            geom=GeometryCollection(Point(5, 5), srid=settings.SRID)
        )
        cls.intervention_site_in_2 = InterventionFactory.create(target=cls.site_in_2)

        cls.course_in_2 = CourseFactory.create(
            parent_sites=[cls.site_in_2.pk],
            geom=GeometryCollection(Point(5, 5), srid=settings.SRID),
        )
        cls.intervention_course_in_2 = InterventionFactory.create(
            target=cls.course_in_2
        )
        cls.report_in_1 = ReportFactory.create(geom=Point(1, 1, srid=settings.SRID))
        cls.intervention_report_in_1 = InterventionFactory.create(
            target=cls.report_in_1
        )

        cls.report_in_2 = ReportFactory.create(geom=Point(5, 5, srid=settings.SRID))
        cls.intervention_report_in_2 = InterventionFactory.create(
            target=cls.report_in_2
        )

        report_deleted = ReportFactory.create(geom=Point(1, 1, srid=settings.SRID))
        cls.intervention_report_deleted = InterventionFactory.create(
            target=report_deleted
        )
        report_deleted.delete()

        course_deleted = CourseFactory.create(
            geom=GeometryCollection(Point(1, 1), srid=settings.SRID)
        )
        cls.intervention_course_deleted = InterventionFactory.create(
            target=course_deleted
        )
        course_deleted.delete()

        site_deleted = SiteFactory.create(
            geom=GeometryCollection(Point(1, 1), srid=settings.SRID)
        )
        cls.intervention_site_deleted = InterventionFactory.create(target=site_deleted)
        site_deleted.delete()

        cls.blade_in_1 = BladeFactory.create(signage=signage_in_1)
        cls.intervention_blade_in_1 = InterventionFactory.create(target=cls.blade_in_1)

        cls.blade_in_2 = BladeFactory.create(signage=signage_in_2)
        cls.intervention_blade_in_2 = InterventionFactory.create(target=cls.blade_in_2)

        cls.geom_in_1 = MultiPolygon(
            Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
        )
        cls.geom_in_2 = MultiPolygon(
            Polygon(((4, 4), (5, 4), (5, 5), (4, 5), (4, 4)), srid=settings.SRID)
        )
        cls.geom_out = MultiPolygon(
            Polygon(((6, 6), (10, 6), (10, 10), (6, 10), (6, 6)), srid=settings.SRID)
        )

    def test_filter_in_1_city(self):
        """
        We should have 1 interventions on topologies, 1 intervention on sites, 1 intervention on courses,
        1 intervention on blade
        """
        filter = InterventionFilterSet(
            data={"city": [CityFactory.create(geom=self.geom_in_1)]}
        )
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_1,
                self.intervention_site_in_1,
                self.intervention_course_in_1,
                self.intervention_blade_in_1,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_1,
            },
        )
        self.assertEqual(len(filter.qs), 7)

    def test_filter_in_2_city(self):
        """
        We should have 1 interventions on topologies, 1 intervention on sites, 1 intervention on courses,
        1 intervention on blade
        """
        filter = InterventionFilterSet(
            data={"city": [CityFactory.create(geom=self.geom_in_2)]}
        )
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_2,
                self.intervention_site_in_2,
                self.intervention_course_in_2,
                self.intervention_blade_in_2,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_2,
            },
        )
        self.assertEqual(len(filter.qs), 7)

    def test_filter_in_1_and_2_city(self):
        """
        We should have 2 interventions on topologies, 2 interventions on sites, 2 interventions on courses,
        2 interventions on blade
        """
        filter = InterventionFilterSet(
            data={
                "city": [
                    CityFactory.create(geom=self.geom_in_2),
                    CityFactory.create(geom=self.geom_in_1),
                ]
            }
        )
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_2,
                self.intervention_site_in_2,
                self.intervention_course_in_2,
                self.intervention_blade_in_2,
                self.intervention_topology_in_1,
                self.intervention_site_in_1,
                self.intervention_course_in_1,
                self.intervention_blade_in_1,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_1,
                self.intervention_report_in_2,
            },
        )
        self.assertEqual(len(filter.qs), 12)

    def test_filter_out_city(self):
        """
        We should not have any interventions
        """
        filter = InterventionFilterSet(
            data={"city": [CityFactory.create(geom=self.geom_out)]}
        )
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 2)

    def test_filter_in_1_district(self):
        """
        We should have 1 interventions on topologies, 1 intervention on sites, 1 intervention on courses,
        1 intervention on blade
        """
        filter = InterventionFilterSet(
            data={"district": [DistrictFactory.create(geom=self.geom_in_1)]}
        )
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_1,
                self.intervention_site_in_1,
                self.intervention_course_in_1,
                self.intervention_blade_in_1,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_1,
            },
        )
        self.assertEqual(len(filter.qs), 7)

    def test_filter_in_2_district(self):
        """
        We should have 1 interventions on topologies, 1 intervention on sites, 1 intervention on courses,
        1 intervention on blade
        """
        filter = InterventionFilterSet(
            data={"district": [DistrictFactory.create(geom=self.geom_in_2)]}
        )
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_2,
                self.intervention_site_in_2,
                self.intervention_course_in_2,
                self.intervention_blade_in_2,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_2,
            },
        )
        self.assertEqual(len(filter.qs), 7)

    def test_filter_in_1_and_2_district(self):
        """
        We should have 2 interventions on topologies, 2 interventions on sites, 2 interventions on courses,
        2 interventions on blade
        """
        filter = InterventionFilterSet(
            data={
                "district": [
                    DistrictFactory.create(geom=self.geom_in_1),
                    DistrictFactory.create(geom=self.geom_in_2),
                ]
            }
        )
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_2,
                self.intervention_site_in_2,
                self.intervention_course_in_2,
                self.intervention_blade_in_2,
                self.intervention_topology_in_1,
                self.intervention_site_in_1,
                self.intervention_course_in_1,
                self.intervention_blade_in_1,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_1,
                self.intervention_report_in_2,
            },
        )
        self.assertEqual(len(filter.qs), 12)

    def test_filter_out_district(self):
        """
        We should not have any interventions
        """
        filter = InterventionFilterSet(
            data={"district": [DistrictFactory.create(geom=self.geom_out)]}
        )
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 2)

    def test_filter_in_1_restricted_area(self):
        """
        We should have 1 interventions on topologies, 1 intervention on sites, 1 intervention on courses,
        1 intervention on blade
        """
        filter = InterventionFilterSet(
            data={"area": [RestrictedAreaFactory.create(geom=self.geom_in_1)]}
        )
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_1,
                self.intervention_site_in_1,
                self.intervention_course_in_1,
                self.intervention_blade_in_1,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_1,
            },
        )
        self.assertEqual(len(filter.qs), 7)

    def test_filter_in_2_restricted_area(self):
        """
        We should have 1 interventions on topologies, 1 intervention on sites, 1 intervention on courses,
        1 intervention on blade
        """
        filter = InterventionFilterSet(
            data={"area": [RestrictedAreaFactory.create(geom=self.geom_in_2)]}
        )
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_2,
                self.intervention_site_in_2,
                self.intervention_course_in_2,
                self.intervention_blade_in_2,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_2,
            },
        )
        self.assertEqual(len(filter.qs), 7)

    def test_filter_in_1_and_2_restricted_area(self):
        """
        We should have 2 interventions on topologies, 2 interventions on sites, 2 interventions on courses,
        2 interventions on blade
        """
        filter = InterventionFilterSet(
            data={
                "area": [
                    RestrictedAreaFactory.create(geom=self.geom_in_1),
                    RestrictedAreaFactory.create(geom=self.geom_in_2),
                ]
            }
        )
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_2,
                self.intervention_site_in_2,
                self.intervention_course_in_2,
                self.intervention_blade_in_2,
                self.intervention_topology_in_1,
                self.intervention_site_in_1,
                self.intervention_course_in_1,
                self.intervention_blade_in_1,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_1,
                self.intervention_report_in_2,
            },
        )
        self.assertEqual(len(filter.qs), 12)

    def test_filter_out_restricted_area(self):
        """
        We should not have any interventions
        """
        filter = InterventionFilterSet(
            data={"area": [RestrictedAreaFactory.create(geom=self.geom_out)]}
        )
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 2)

    def test_filter_in_1_restricted_area_type(self):
        """
        We should have 1 interventions on topologies, 1 intervention on sites, 1 intervention on courses,
        1 intervention on blade
        """
        restricted_area_type = RestrictedAreaTypeFactory.create()
        RestrictedAreaFactory.create(
            geom=self.geom_in_1, area_type=restricted_area_type
        )
        filter = InterventionFilterSet(data={"area_type": [restricted_area_type.pk]})
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_1,
                self.intervention_site_in_1,
                self.intervention_course_in_1,
                self.intervention_blade_in_1,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_1,
            },
        )
        self.assertEqual(len(filter.qs), 7)

    def test_filter_in_2_restricted_area_type(self):
        """
        We should have 1 interventions on topologies, 1 intervention on sites, 1 intervention on courses,
        1 intervention on blade
        """
        restricted_area_type = RestrictedAreaTypeFactory.create()
        RestrictedAreaFactory.create(
            geom=self.geom_in_2, area_type=restricted_area_type
        )
        filter = InterventionFilterSet(data={"area_type": [restricted_area_type.pk]})
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_2,
                self.intervention_site_in_2,
                self.intervention_course_in_2,
                self.intervention_blade_in_2,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_2,
            },
        )
        self.assertEqual(len(filter.qs), 7)

    def test_filter_in_1_and_in_2_restricted_area_type(self):
        """
        We should have 2 interventions on topologies, 2 interventions on sites, 2 interventions on courses,
        2 interventions on blade
        """
        restricted_area_type_1 = RestrictedAreaTypeFactory.create()
        restricted_area_type_2 = RestrictedAreaTypeFactory.create()

        RestrictedAreaFactory.create(
            geom=self.geom_in_1, area_type=restricted_area_type_1
        )
        RestrictedAreaFactory.create(
            geom=self.geom_in_2, area_type=restricted_area_type_2
        )
        filter = InterventionFilterSet(
            data={"area_type": [restricted_area_type_1.pk, restricted_area_type_2.pk]}
        )
        self.assertTrue(filter.is_valid())
        self.assertSetEqual(
            set(filter.qs),
            {
                self.intervention_topology_in_2,
                self.intervention_site_in_2,
                self.intervention_course_in_2,
                self.intervention_blade_in_2,
                self.intervention_topology_in_1,
                self.intervention_site_in_1,
                self.intervention_course_in_1,
                self.intervention_blade_in_1,
                self.intervention_site_deleted,
                self.intervention_course_deleted,
                self.intervention_report_in_1,
                self.intervention_report_in_2,
            },
        )
        self.assertEqual(len(filter.qs), 12)

    def test_filter_out_restricted_area_type(self):
        """
        We should not have any interventions
        """
        restricted_area_type = RestrictedAreaTypeFactory.create()
        RestrictedAreaFactory.create(geom=self.geom_out, area_type=restricted_area_type)
        filter = InterventionFilterSet(data={"area_type": [restricted_area_type.pk]})
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 2)

    def test_filter_restricted_area_type_without_restricted_area(self):
        """
        We should not have any interventions
        """
        restricted_area_type = RestrictedAreaTypeFactory.create()
        filter = ProjectFilterSet(data={"area_type": [restricted_area_type.pk]})
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)


class ProjectIntersectionFilterZoningTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.path_in = PathFactory.create(
                geom=LineString((0, 0), (2, 1), srid=settings.SRID)
            )
            cls.path_out = PathFactory.create(
                geom=LineString((5, 5), (4, 4), srid=settings.SRID)
            )
            cls.topo_in = TopologyFactory.create(paths=[cls.path_in])
            cls.topo_out = TopologyFactory.create(paths=[cls.path_out])
        else:
            cls.topo_in = TopologyFactory.create(
                geom=LineString((0, 0), (2, 1), srid=settings.SRID)
            )
            cls.topo_out = TopologyFactory.create(
                geom=LineString((5, 5), (4, 4), srid=settings.SRID)
            )
        cls.intervention_in = InterventionFactory.create(target=cls.topo_in)
        cls.intervention_out = InterventionFactory.create(target=cls.topo_out)
        cls.geom_zoning = MultiPolygon(
            Polygon(((0, 0), (2, 0), (2, 2), (0, 2), (0, 0)), srid=settings.SRID)
        )

    def test_filter_in_city(self):
        filter = ProjectFilterSet(
            data={"city": [CityFactory.create(geom=self.geom_zoning)]}
        )
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertTrue(filter.is_valid())
        self.assertIn(project_in, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_in_district(self):
        filter = ProjectFilterSet(
            data={"district": [DistrictFactory.create(geom=self.geom_zoning)]}
        )
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertTrue(filter.is_valid())
        self.assertIn(project_in, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_out_city(self):
        filter = ProjectFilterSet(
            data={"city": [CityFactory.create(geom=self.geom_zoning)]}
        )
        project_out = ProjectFactory.create()
        project_out.interventions.add(self.intervention_out)
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)

    def test_filter_out_district(self):
        filter = ProjectFilterSet(
            data={"district": [DistrictFactory.create(geom=self.geom_zoning)]}
        )
        project_out = ProjectFactory.create()
        project_out.interventions.add(self.intervention_out)
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)

    def test_filter_in_restricted_area(self):
        filter = ProjectFilterSet(
            data={"area": [RestrictedAreaFactory.create(geom=self.geom_zoning)]}
        )
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertTrue(filter.is_valid())
        self.assertIn(project_in, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_in_restricted_area_type(self):
        restricted_area_type = RestrictedAreaTypeFactory.create()
        RestrictedAreaFactory.create(
            geom=self.geom_zoning, area_type=restricted_area_type
        )
        filter = ProjectFilterSet(data={"area_type": [restricted_area_type.pk]})
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertTrue(filter.is_valid())
        self.assertIn(project_in, filter.qs)
        self.assertEqual(len(filter.qs), 1)

    def test_filter_out_restricted_area(self):
        filter = ProjectFilterSet(
            data={"area": [RestrictedAreaFactory.create(geom=self.geom_zoning)]}
        )
        project_out = ProjectFactory.create()
        project_out.interventions.add(self.intervention_out)
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)

    def test_filter_out_restricted_area_type(self):
        restricted_area_type = RestrictedAreaTypeFactory.create()
        RestrictedAreaFactory.create(
            geom=self.geom_zoning, area_type=restricted_area_type
        )
        filter = ProjectFilterSet(data={"area_type": [restricted_area_type.pk]})
        project_out = ProjectFactory.create()
        project_out.interventions.add(self.intervention_out)
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)

    def test_filter_restricted_area_type_without_restricted_area(self):
        restricted_area_type = RestrictedAreaTypeFactory.create()
        filter = ProjectFilterSet(data={"area_type": [restricted_area_type.pk]})
        project_in = ProjectFactory.create()
        project_in.interventions.add(self.intervention_in)
        self.assertTrue(filter.is_valid())
        self.assertEqual(len(filter.qs), 0)
