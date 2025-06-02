import json
import os
from io import StringIO
from unittest import mock, skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString, Point, Polygon
from django.contrib.gis.geos.collections import GeometryCollection, MultiPoint
from django.core.management import call_command
from django.test import TestCase

from geotrek.common.models import Attachment, FileType, TargetPortal
from geotrek.common.tests.mixins import GeotrekParserTestMixin
from geotrek.outdoor.models import (
    ChildSitesExistError,
    Course,
    OrderedCourseChild,
    Practice,
    Rating,
    RatingScale,
    Sector,
    Site,
    SiteType,
)
from geotrek.outdoor.parsers import OpenStreetMapOutdoorSiteParser


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class MappingOutdoorGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    def test_geotrek_aggregator_parser_mapping(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("outdoor", "structure.json"),
            ("outdoor", "theme.json"),
            ("outdoor", "label.json"),
            ("outdoor", "source.json"),
            ("outdoor", "organism.json"),
            ("outdoor", "source.json"),
            ("outdoor", "structure.json"),
            ("outdoor", "theme.json"),
            ("outdoor", "label.json"),
            ("outdoor", "source.json"),
            ("outdoor", "organism.json"),
            ("outdoor", "source.json"),
            ("outdoor", "outdoor_site_ids.json"),
            ("outdoor", "outdoor_sector.json"),
            ("outdoor", "outdoor_practice.json"),
            ("outdoor", "outdoor_ratingscale.json"),
            ("outdoor", "outdoor_rating.json"),
            ("outdoor", "outdoor_sitetype.json"),
            ("outdoor", "outdoor_site.json"),
            ("outdoor", "outdoor_course_ids.json"),
            ("outdoor", "outdoor_sector.json"),
            ("outdoor", "outdoor_practice.json"),
            ("outdoor", "outdoor_ratingscale.json"),
            ("outdoor", "outdoor_rating.json"),
            ("outdoor", "outdoor_coursetype.json"),
            ("outdoor", "outdoor_course.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        output = StringIO()
        filename = os.path.join(
            os.path.dirname(__file__),
            "data",
            "geotrek_parser_v2",
            "config_aggregator_mapping.json",
        )
        call_command(
            "import",
            "geotrek.common.parsers.GeotrekAggregatorParser",
            filename=filename,
            verbosity=2,
            stdout=output,
        )
        self.assertEqual(Site.objects.count(), 6)
        self.assertEqual(SiteType.objects.count(), 1)
        self.assertEqual(Course.objects.count(), 7)
        site = Site.objects.get(name_fr="Racine", name_en="Root")
        self.assertEqual(str(site.practice.sector), "Renamed Sector")
        self.assertEqual(str(site.practice), "Renamed Practice")
        self.assertEqual(site.ratings.count(), 1)
        self.assertEqual(
            str(site.ratings.first()), "Renamed Rating Scale : Renamed Rating"
        )
        self.assertEqual(
            str(site.ratings.first().scale), "Renamed Rating Scale (Renamed Practice)"
        )
        self.assertEqual(str(site.type), "Renamed Site Type")


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class OutdoorGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")
        Site.objects.create(
            name="To delete", provider="URL_1", geom="GEOMETRYCOLLECTION(POINT(0 0))"
        )

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    def test_create_sites_and_courses(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("outdoor", "structure.json"),
            ("outdoor", "theme.json"),
            ("outdoor", "label.json"),
            ("outdoor", "source.json"),
            ("outdoor", "organism.json"),
            ("outdoor", "source.json"),
            ("outdoor", "structure.json"),
            ("outdoor", "theme.json"),
            ("outdoor", "label.json"),
            ("outdoor", "source.json"),
            ("outdoor", "organism.json"),
            ("outdoor", "source.json"),
            ("outdoor", "outdoor_site_ids.json"),
            ("outdoor", "outdoor_sector.json"),
            ("outdoor", "outdoor_practice.json"),
            ("outdoor", "outdoor_ratingscale.json"),
            ("outdoor", "outdoor_rating.json"),
            ("outdoor", "outdoor_sitetype.json"),
            ("outdoor", "outdoor_site.json"),
            ("outdoor", "outdoor_course_ids.json"),
            ("outdoor", "outdoor_sector.json"),
            ("outdoor", "outdoor_practice.json"),
            ("outdoor", "outdoor_ratingscale.json"),
            ("outdoor", "outdoor_rating.json"),
            ("outdoor", "outdoor_coursetype.json"),
            ("outdoor", "outdoor_course.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        output = StringIO()
        filename = os.path.join(
            os.path.dirname(__file__),
            "data",
            "geotrek_parser_v2",
            "config_aggregator_simple.json",
        )
        call_command(
            "import",
            "geotrek.common.parsers.GeotrekAggregatorParser",
            filename=filename,
            verbosity=2,
            stdout=output,
        )

        # Sites
        self.assertEqual(Site.objects.count(), 6)
        self.assertEqual(Sector.objects.count(), 2)
        self.assertEqual(RatingScale.objects.count(), 1)
        self.assertEqual(Rating.objects.count(), 3)
        self.assertEqual(Practice.objects.count(), 1)
        site = Site.objects.get(name_fr="Racine", name_en="Root")
        self.assertEqual(site.published, True)
        self.assertEqual(site.published_fr, True)
        self.assertEqual(site.published_en, True)
        self.assertEqual(site.published_it, False)
        self.assertEqual(site.published_es, False)
        self.assertEqual(str(site.practice.sector), "Vertical")
        self.assertEqual(str(site.practice), "Climbing")
        self.assertEqual(str(site.labels.first()), "Label en")
        self.assertEqual(site.ratings.count(), 3)
        self.assertEqual(str(site.ratings.first()), "Class : 3+")
        self.assertEqual(site.ratings.first().description, "A description")
        self.assertEqual(site.ratings.first().order, 302)
        self.assertEqual(site.ratings.first().color, "#D9D9D8")
        self.assertEqual(str(site.ratings.first().scale), "Class (Climbing)")
        self.assertEqual(str(site.type), "School")
        self.assertEqual(str(site.type.practice), "Climbing")
        self.assertAlmostEqual(site.geom[0][0][0][0], 970023.8976707931, places=5)
        self.assertAlmostEqual(site.geom[0][0][0][1], 6308806.903248067, places=5)
        self.assertAlmostEqual(site.geom[0][0][1][0], 967898.282139539, places=5)
        self.assertAlmostEqual(site.geom[0][0][1][1], 6358768.657410889, places=5)
        self.assertEqual(str(site.labels.first()), "Label en")
        self.assertEqual(str(site.source.first()), "Source")
        self.assertEqual(str(site.themes.first()), "Test thème en")
        self.assertEqual(str(site.managers.first()), "Organisme")
        self.assertEqual(str(site.structure), "Struct1")
        self.assertEqual(site.description_teaser, "Test en")
        self.assertEqual(site.description_teaser_fr, "Test fr")
        self.assertEqual(site.description, "Test descr en")
        self.assertEqual(site.description_fr, "Test descr fr")
        self.assertEqual(site.advice, "Test reco en")
        self.assertEqual(site.accessibility, "Test access en")
        self.assertEqual(site.period, "Test période en")
        self.assertEqual(site.orientation, ["NE", "S"])
        self.assertEqual(site.ambiance, "Test ambiance en")
        self.assertEqual(site.ambiance_fr, "Test ambiance fr")
        self.assertEqual(site.wind, ["N", "E"])
        self.assertEqual(str(site.structure), "Struct1")
        # TODO ; self.assertEqual(site.information_desks.count(), 1)
        # TODO : self.assertEqual(site.weblink.count(), 1)
        # TODO : self.assertEqual(site.excluded_pois.count(), 1)
        self.assertEqual(site.eid, "57a8fb52-213d-4dce-8224-bc997f892aae")
        self.assertEqual(Attachment.objects.filter(object_id=site.pk).count(), 1)
        attachment = Attachment.objects.filter(object_id=site.pk).first()
        self.assertIsNotNone(attachment.attachment_file.url)
        self.assertEqual(attachment.legend, "Arrien-en-Bethmale, vue du village")
        child_site = Site.objects.get(name_fr="Noeud 1", name_en="Node")
        self.assertEqual(child_site.parent, site)
        self.assertEqual(Site.objects.filter(name="To delete").count(), 0)

        # Courses
        self.assertEqual(Course.objects.count(), 7)
        course = Course.objects.get(name_fr="Feuille 1", name_en="Leaf 1")
        self.assertEqual(str(course.type), "Type 1 en")
        self.assertEqual(course.published, True)
        self.assertEqual(course.published_fr, True)
        self.assertEqual(course.published_en, True)
        self.assertEqual(course.published_it, False)
        self.assertEqual(course.published_es, False)
        self.assertEqual(course.ratings.count(), 1)
        self.assertEqual(str(course.ratings.first()), "Class : 3+")
        self.assertEqual(course.ratings.first().description, "A description")
        self.assertEqual(course.ratings.first().order, 302)
        self.assertEqual(course.ratings.first().color, "#D9D9D8")
        self.assertEqual(str(course.ratings.first().scale), "Class (Climbing)")
        self.assertAlmostEqual(course.geom.coords[0][0], 994912.1442530667, places=5)
        self.assertAlmostEqual(course.geom.coords[0][1], 6347387.846494712, places=5)
        self.assertEqual(str(course.structure), "Struct1")
        self.assertEqual(course.description, "Test descr en")
        self.assertEqual(course.description_fr, "Test descr fr")
        self.assertEqual(course.ratings_description, "Test descr en")
        self.assertEqual(course.ratings_description_fr, "Test descr fr")
        self.assertEqual(course.equipment, "Test équipement en")
        self.assertEqual(course.equipment_fr, "Test équipement fr")
        self.assertEqual(course.gear, "Test matériel en")
        self.assertEqual(course.gear_fr, "Test matériel fr")
        self.assertEqual(course.advice, "Test reco en")
        self.assertEqual(course.duration, 100)
        self.assertEqual(course.height, 100)
        self.assertEqual(course.accessibility, "Test access en")
        self.assertEqual(str(course.structure), "Struct1")
        # TODO : self.assertEqual(course.excluded_pois.count(), 1)
        self.assertEqual(course.eid, "840f4cf7-dbe0-4aa1-835f-c1219c45dd7a")
        self.assertEqual(Attachment.objects.filter(object_id=course.pk).count(), 1)
        attachment = Attachment.objects.filter(object_id=course.pk).first()
        self.assertIsNotNone(attachment.attachment_file.url)
        self.assertEqual(attachment.legend, "Arrien-en-Bethmale, vue du village")
        parent_site = Site.objects.get(name_fr="Noeud 2 bis")
        self.assertEqual(course.parent_sites.count(), 1)
        self.assertEqual(course.parent_sites.first(), parent_site)
        self.assertEqual(type(course.points_reference), MultiPoint)
        self.assertEqual(str(course.parent_sites.first().practice), "Climbing")
        child_course_1 = Course.objects.get(name="Step 1")
        child_course_2 = Course.objects.get(name="Step 2")
        child_course_3 = Course.objects.get(name="Step 3")
        self.assertTrue(
            OrderedCourseChild.objects.filter(
                parent=course, child=child_course_1, order=0
            ).exists()
        )
        self.assertTrue(
            OrderedCourseChild.objects.filter(
                parent=course, child=child_course_2, order=1
            ).exists()
        )
        self.assertTrue(
            OrderedCourseChild.objects.filter(
                parent=course, child=child_course_3, order=2
            ).exists()
        )


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class OutdoorGeotrekParserWrongChildrenTests(GeotrekParserTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    def test_create_sites_and_courses_with_wrong_children(
        self, mocked_head, mocked_get
    ):
        self.mock_time = 0
        self.mock_json_order = [
            ("outdoor", "structure.json"),
            ("outdoor", "theme.json"),
            ("outdoor", "label.json"),
            ("outdoor", "source.json"),
            ("outdoor", "organism.json"),
            ("outdoor", "source.json"),
            ("outdoor", "structure.json"),
            ("outdoor", "theme.json"),
            ("outdoor", "label.json"),
            ("outdoor", "source.json"),
            ("outdoor", "organism.json"),
            ("outdoor", "source.json"),
            ("outdoor", "outdoor_site_ids.json"),
            ("outdoor", "outdoor_sector.json"),
            ("outdoor", "outdoor_practice.json"),
            ("outdoor", "outdoor_ratingscale.json"),
            ("outdoor", "outdoor_rating.json"),
            ("outdoor", "outdoor_sitetype.json"),
            ("outdoor", "outdoor_site_wrong_children.json"),
            ("outdoor", "outdoor_course_ids.json"),
            ("outdoor", "outdoor_sector.json"),
            ("outdoor", "outdoor_practice.json"),
            ("outdoor", "outdoor_ratingscale.json"),
            ("outdoor", "outdoor_rating.json"),
            ("outdoor", "outdoor_coursetype.json"),
            ("outdoor", "outdoor_course_wrong_children.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        output = StringIO()
        filename = os.path.join(
            os.path.dirname(__file__),
            "data",
            "geotrek_parser_v2",
            "config_aggregator_simple.json",
        )
        call_command(
            "import",
            "geotrek.common.parsers.GeotrekAggregatorParser",
            filename=filename,
            verbosity=2,
            stdout=output,
        )
        outputs = output.getvalue()
        self.assertIn(
            "Trying to retrieve missing parent Site (UUID: 5c0d656b-2691-4c45-903c-9ce1050ff9ea) for child Course (UUID: 840f4cf7-dbe0-4aa1-835f-c1219c45dd7a)",
            outputs,
        )
        self.assertIn(
            "Trying to retrieve missing parent (UUID: 57a8fb53-214d-4dce-8224-bc997f892aae) for child Site (UUID: 67ca9363-2f5c-4a15-b124-46674a54f08d)",
            outputs,
        )
        self.assertIn(
            "Trying to retrieve missing child Course (UUID: 43ce927d-9236-4a62-ac7f-799d1c024b5a) for parent Course (UUID: 0dce3b07-4e50-42f1-9af9-2d3ea0bcdbbc)",
            outputs,
        )


class TestOpenStreetMapOutdoorParser(OpenStreetMapOutdoorSiteParser):
    practice = "Foo"
    themes = ["test theme1", "test theme2"]
    portal = "test portal1"
    source = ["test source1", "test source2"]
    tags = [{"sport": "climbing"}]
    default_fields_values = {"name": "test_default"}
    field_options = {
        "themes": {"create": True},
        "source": {"create": True},
    }


class OpenStreetMapOutdoorSiteParserTests(TestCase):
    @classmethod
    @mock.patch("requests.get")
    def import_outdoor_site(cls, mocked, output_available):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "outdoor_OSM.json"
            )
            with open(filename) as f:
                return json.load(f)

        def mocked_polygons_valid(decode):
            wkt_polygon = "SRID=4326;POLYGON ((6.25876177 44.90539914, 6.25944969 44.90610886, 6.25807932 44.90434684, 6.25876177 44.90539914))"
            return wkt_polygon

        def mocked_polygons_not_valid(decode):
            wkt_polygon = "SRID=4326;POLYGON ((6.25876177 44.90539914, 6.25944969 44.90610886, 6.25807932 44.90434684))"
            return wkt_polygon

        def mocked_multipolygons_valid(decode):
            wkt_polygon = "SRID=4326;MULTIPOLYGON (((6.25876177 44.90539914, 6.25944969 44.90610886, 6.25807932 44.90434684, 6.25876177 44.90539914)), ((6.15876177 44.80539914, 6.15944969 44.80610886, 6.15807932 44.80434684, 6.15876177 44.80539914)))"
            return wkt_polygon

        def mocked_multipolygons_not_valid(decode):
            wkt_polygon = "SRID=4326;MULTIPOLYGON (((6.25876177 44.90539914, 6.25944969 44.90610886, 6.25807932 44.90434684, 6.25876177 44.90539914)), ((6.25876177 44.90539914, 6.25944969 44.90610886, 6.25807932 44.90434684, 6.25876177 44.90539914)))"
            return wkt_polygon

        mock_overpass = mock.Mock()
        mock_overpass.status_code = 200
        mock_overpass.json = mocked_json

        mock_polygons_valid = mock.Mock()
        mock_polygons_valid.status_code = 200
        mock_polygons_valid.content.decode = mocked_polygons_valid

        mock_polygons_not_valid = mock.Mock()
        mock_polygons_not_valid.status_code = 200
        mock_polygons_not_valid.content.decode = mocked_polygons_not_valid

        mock_API_error = mock.Mock()
        mock_API_error.status_code = 404
        mock_API_error.url = "https//polygons.openstreetmap.fr"

        mock_multipolygons_valid = mock.Mock()
        mock_multipolygons_valid.status_code = 200
        mock_multipolygons_valid.content.decode = mocked_multipolygons_valid

        mock_multipolygons_not_valid = mock.Mock()
        mock_multipolygons_not_valid.status_code = 200
        mock_multipolygons_not_valid.content.decode = mocked_multipolygons_not_valid

        mocked.side_effect = [
            mock_overpass,
            mock_polygons_valid,
            mock_polygons_not_valid,
            mock_API_error,
            mock_API_error,
            mock_multipolygons_valid,
            mock_multipolygons_not_valid,
            mock_API_error,
            mock_API_error,
            mock_API_error,
        ]

        output = StringIO()
        call_command(
            "import",
            "geotrek.outdoor.tests.test_parsers.TestOpenStreetMapOutdoorParser",
            stdout=output,
        )

        if output_available:
            cls.output = output.getvalue()

    @classmethod
    def setUpTestData(cls):
        Practice.objects.create(name="Foo")
        TargetPortal.objects.create(name="test portal1")
        FileType.objects.create(type="Photographie")

        cls.import_outdoor_site(output_available=True)

        cls.objects = Site.objects

    def test_create_outdoor_site_OSM(self):
        self.assertEqual(self.objects.count(), 14)

    def test_practice_outdoor_site_OSM(self):
        outdoor_site = self.objects.get(eid="N1")
        self.assertEqual(outdoor_site.practice.name, "Foo")

    def test_themes_outdoor_site_OSM(self):
        outdoor_site = self.objects.get(eid="N1")
        self.assertEqual(outdoor_site.themes.all().count(), 2)
        self.assertEqual(outdoor_site.themes.first().label, "test theme1")
        warnings = [
            "Theme 'test theme1' did not exist in Geotrek-Admin and was automatically created",
            "Theme 'test theme2' did not exist in Geotrek-Admin and was automatically created",
        ]
        self.assertIn(warnings[0], self.output)
        self.assertIn(warnings[1], self.output)

    def test_portal_outdoor_site_OSM(self):
        outdoor_site = self.objects.get(eid="N1")
        self.assertEqual(outdoor_site.portal.all().count(), 1)
        self.assertEqual(outdoor_site.portal.first().name, "test portal1")

    def test_source_outdoor_site_OSM(self):
        outdoor_site = self.objects.get(eid="N1")
        self.assertEqual(outdoor_site.source.all().count(), 2)
        self.assertEqual(outdoor_site.source.first().name, "test source1")
        warnings = [
            "Record Source 'test source1' did not exist in Geotrek-Admin and was automatically created",
            "Record Source 'test source2' did not exist in Geotrek-Admin and was automatically created",
        ]
        self.assertIn(warnings[0], self.output)
        self.assertIn(warnings[1], self.output)

    def test_indoor_practice_filter(self):
        with self.assertRaises(Site.DoesNotExist):
            self.objects.get(eid="W1000")

        self.assertIn("This object is an indoor site", self.output)

    def test_geom_transform(self):
        outdoor_site = self.objects.get(eid="W3")
        geom = outdoor_site.geom[0]
        self.assertAlmostEqual(geom.coords[0][0][0], 957149.000, places=2)
        self.assertAlmostEqual(geom.coords[0][0][1], 6428219.000, places=2)
        self.assertAlmostEqual(geom.coords[0][1][0], 957200.000, places=2)
        self.assertAlmostEqual(geom.coords[0][1][1], 6428300.000, places=2)
        self.assertAlmostEqual(geom.coords[0][2][0], 957100.000, places=2)
        self.assertAlmostEqual(geom.coords[0][2][1], 6428100.000, places=2)

    def test_geom_point(self):
        outdoor_site = self.objects.get(eid="N1")
        geom = outdoor_site.geom[0]
        self.assertEqual(type(geom), Point)

    def test_geom_way_linestring(self):
        outdoor_site = self.objects.get(eid="W2")
        geom = outdoor_site.geom[0]
        self.assertEqual(type(geom), LineString)
        self.assertEqual(len(geom.coords[0]), 2)

    def test_geom_way_polygon(self):
        outdoor_site = self.objects.get(eid="W3")
        geom = outdoor_site.geom[0]
        self.assertEqual(type(geom), Polygon)
        self.assertEqual(len(geom.coords[0]), 4)

    def test_geom_relation_polygon_API_valid(self):
        outdoor_site = self.objects.get(eid="R4")
        geom = outdoor_site.geom[0]
        self.assertEqual(type(geom), Polygon)
        self.assertEqual(len(geom.coords[0]), 4)

    def test_geom_relation_polygon_API_not_valid(self):
        outdoor_site = self.objects.get(eid="R5")
        self.assertEqual(len(outdoor_site.geom), 2)
        self.assertEqual(type(outdoor_site.geom[0]), LineString)
        self.assertEqual(type(outdoor_site.geom[1]), LineString)
        self.assertEqual(len(outdoor_site.geom[0][0]), 2)
        self.assertEqual(len(outdoor_site.geom[1][0]), 2)

    def test_geom_relation_multipoint(self):
        outdoor_site = self.objects.get(eid="R6")
        self.assertEqual(len(outdoor_site.geom), 2)
        self.assertEqual(type(outdoor_site.geom[0]), Point)
        self.assertEqual(type(outdoor_site.geom[1]), Point)

    def test_geom_relation_multilinestring(self):
        outdoor_site = self.objects.get(eid="R7")
        self.assertEqual(len(outdoor_site.geom), 2)
        self.assertEqual(type(outdoor_site.geom[0]), LineString)
        self.assertEqual(type(outdoor_site.geom[1]), LineString)

    def test_geom_relation_multipolygon_API_valid(self):
        outdoor_site = self.objects.get(eid="R8")
        geom = outdoor_site.geom
        self.assertEqual(type(geom[0]), Polygon)
        self.assertEqual(len(geom[0].coords[0]), 4)
        self.assertEqual(type(geom[1]), Polygon)
        self.assertEqual(len(geom[1].coords[0]), 4)

    def test_geom_relation_multipolygon_API_not_valid(self):
        outdoor_site = self.objects.get(eid="R9")
        geom = outdoor_site.geom[0]
        self.assertEqual(type(geom), Polygon)
        self.assertEqual(len(geom.coords[0]), 4)

    def test_geom_relation_multipolygon_valid(self):
        outdoor_site = self.objects.get(eid="R10")
        geom = outdoor_site.geom
        self.assertEqual(type(geom[0]), Polygon)
        self.assertEqual(len(geom[0].coords[0]), 4)
        self.assertEqual(type(geom[1]), Polygon)
        self.assertEqual(len(geom[1].coords[0]), 4)

    def test_geom_relation_point_way(self):
        outdoor_site = self.objects.get(eid="R11")
        geom = outdoor_site.geom
        self.assertEqual(type(geom[0]), Point)
        self.assertEqual(type(geom[1]), LineString)
        self.assertEqual(len(geom[1].coords[0]), 2)

    def test_geom_relation_point_polygon(self):
        outdoor_site = self.objects.get(eid="R12")
        geom = outdoor_site.geom
        self.assertEqual(type(geom[0]), Point)
        self.assertEqual(type(geom[1]), Polygon)
        self.assertEqual(len(geom[1].coords[0]), 4)

    def test_geom_relation_linestring_polygon(self):
        outdoor_site = self.objects.get(eid="R13")
        geom = outdoor_site.geom
        self.assertEqual(type(geom[0]), LineString)
        self.assertEqual(len(geom[0].coords[0]), 2)
        self.assertEqual(type(geom[1]), Polygon)
        self.assertEqual(len(geom[1].coords[0]), 4)

    def test_hierarchy_osm_site_sync(self):
        outdoor_site = self.objects.get(eid="N1001")
        self.assertEqual(outdoor_site.parent, None)

        # synchronisation
        self.import_outdoor_site(output_available=False)

        outdoor_site = self.objects.get(eid="N1001")
        self.assertEqual(outdoor_site.parent, None)

    def test_hierarchy_osm_sector_sync(self):
        geom = GeometryCollection(Point(0, 0))
        geom.srid = 2154

        site = Site.objects.create(name="site", eid="1", geom=geom)

        outdoor_sector = self.objects.get(eid="N1001")
        outdoor_sector.parent = site
        outdoor_sector.save(update_fields=["parent"])

        self.assertEqual(outdoor_sector.parent.name, "site")

        # synchronisation
        self.import_outdoor_site(output_available=False)

        outdoor_sector = self.objects.get(eid="N1001")
        self.assertEqual(outdoor_sector.parent.name, "site")

    def test_hierarchy_osm_sector_delete_site(self):
        geom = GeometryCollection(Point(0, 0))
        geom.srid = 2154

        site = Site.objects.create(name="site", eid="1", geom=geom)

        outdoor_sector = self.objects.get(eid="N1001")
        outdoor_sector.parent = site
        outdoor_sector.save(update_fields=["parent"])

        self.assertEqual(outdoor_sector.parent.name, "site")

        # delete site
        with self.assertRaises(ChildSitesExistError):
            site.delete()

    def test_hierarchy_osm_site_with_course_sync(self):
        geom = GeometryCollection(Point(0, 0))
        geom.srid = 2154

        course = Course.objects.create(eid="3", geom=geom)

        outdoor_site = self.objects.get(eid="N1001")
        course.parent_sites.set([outdoor_site])

        self.assertEqual(outdoor_site.parent, None)
        self.assertEqual(course.parent_sites.first().eid, "N1001")

        # synchronisation
        self.import_outdoor_site(output_available=False)

        outdoor_site = self.objects.get(eid="N1001")
        self.assertEqual(outdoor_site.parent, None)
        self.assertEqual(course.parent_sites.first().eid, "N1001")

    def test_hierarchy_osm_site_with_course_delete_course(self):
        geom = GeometryCollection(Point(0, 0))
        geom.srid = 2154

        course = Course.objects.create(eid="3", geom=geom)

        outdoor_site = self.objects.get(eid="N1001")
        course.parent_sites.set([outdoor_site])

        self.assertEqual(outdoor_site.parent, None)
        self.assertEqual(course.parent_sites.first().eid, "N1001")

        # delete course
        course.delete()

        outdoor_site = self.objects.get(eid="N1001")
        self.assertEqual(outdoor_site.parent, None)

    def test_hierarchy_osm_sector_with_site_and_course_sync(self):
        geom = GeometryCollection(Point(0, 0))
        geom.srid = 2154

        site = Site.objects.create(name="site", eid="1", geom=geom)
        course = Course.objects.create(eid="3", geom=geom)

        outdoor_sector = self.objects.get(eid="N1001")
        course.parent_sites.set([outdoor_sector])
        outdoor_sector.parent = site
        outdoor_sector.save(update_fields=["parent"])

        self.assertEqual(outdoor_sector.parent.name, "site")
        self.assertEqual(course.parent_sites.first().eid, "N1001")

        # synchronisation
        self.import_outdoor_site(output_available=False)

        outdoor_sector = self.objects.get(eid="N1001")
        self.assertEqual(outdoor_sector.parent.name, "site")
        self.assertEqual(course.parent_sites.first().eid, "N1001")

    def test_hierarchy_osm_sector_with_site_and_course_delete_course(self):
        geom = GeometryCollection(Point(0, 0))
        geom.srid = 2154

        site = Site.objects.create(name="site", eid="1", geom=geom)
        course = Course.objects.create(eid="3", geom=geom)

        outdoor_sector = self.objects.get(eid="N1001")
        course.parent_sites.set([outdoor_sector])
        outdoor_sector.parent = site
        outdoor_sector.save(update_fields=["parent"])

        self.assertEqual(outdoor_sector.parent.name, "site")
        self.assertEqual(course.parent_sites.first().eid, "N1001")

        # delete course
        course.delete()

        outdoor_sector = self.objects.get(eid="N1001")
        self.assertEqual(outdoor_sector.parent.name, "site")

    def test_hierarchy_osm_sector_with_site_and_course_delete_site(self):
        geom = GeometryCollection(Point(0, 0))
        geom.srid = 2154

        site = Site.objects.create(name="site", eid="1", geom=geom)
        course = Course.objects.create(eid="3", geom=geom)

        outdoor_sector = self.objects.get(eid="N1001")
        course.parent_sites.set([outdoor_sector])
        outdoor_sector.parent = site
        outdoor_sector.save(update_fields=["parent"])

        self.assertEqual(outdoor_sector.parent.name, "site")
        self.assertEqual(course.parent_sites.first().eid, "N1001")

        # delete site
        with self.assertRaises(ChildSitesExistError):
            site.delete()

    def test_hierarchy_osm_site_with_sector_sync(self):
        geom = GeometryCollection(Point(0, 0))
        geom.srid = 2154

        sector = Site.objects.create(name="sector", eid="2", geom=geom)

        outdoor_site = self.objects.get(eid="N1001")
        sector.parent = outdoor_site
        sector.save(update_fields=["parent"])

        self.assertEqual(outdoor_site.parent, None)
        self.assertEqual(sector.parent.eid, "N1001")

        # synchronisation
        self.import_outdoor_site(output_available=False)

        outdoor_site = self.objects.get(eid="N1001")
        self.assertEqual(outdoor_site.parent, None)
        self.assertEqual(sector.parent.eid, "N1001")

    def test_hierarchy_osm_site_with_sector_delete_sector(self):
        geom = GeometryCollection(Point(0, 0))
        geom.srid = 2154

        sector = Site.objects.create(name="sector", eid="2", geom=geom)

        outdoor_site = self.objects.get(eid="N1001")
        sector.parent = outdoor_site
        sector.save(update_fields=["parent"])

        self.assertEqual(outdoor_site.parent, None)
        self.assertEqual(sector.parent.eid, "N1001")

        # delete sector
        sector.delete()

        outdoor_site = self.objects.get(eid="N1001")
        self.assertEqual(outdoor_site.parent, None)
