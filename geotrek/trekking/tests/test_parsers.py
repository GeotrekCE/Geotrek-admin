import json
import os
from copy import copy
from datetime import date
from io import StringIO
from unittest import mock, skipIf
from unittest.mock import Mock
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.gis.geos import LineString, MultiLineString, Point, WKTWriter
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase
from django.test.utils import override_settings

from geotrek.common.models import (
    Attachment,
    FileType,
    Label,
    License,
    RecordSource,
    Theme,
)
from geotrek.common.parsers import DownloadImportError
from geotrek.common.tests.mixins import GeotrekParserTestMixin
from geotrek.common.utils import testdata
from geotrek.core.tests.factories import PathFactory
from geotrek.trekking.models import (
    POI,
    DifficultyLevel,
    OrderedTrekChild,
    POIType,
    Practice,
    Route,
    Service,
    Trek,
)
from geotrek.trekking.parsers import (
    ApidaePOIParser,
    ApidaeTrekParser,
    ApidaeTrekThemeParser,
    GeotrekPOIParser,
    GeotrekServiceParser,
    GeotrekTrekParser,
    OpenStreetMapPOIParser,
    RowImportError,
    SchemaRandonneeParser,
    TrekParser,
    _prepare_attachment_from_apidae_illustration,
)
from geotrek.trekking.tests.factories import RouteFactory


class TrekParserFilterDurationTests(TestCase):
    def setUp(self):
        self.parser = TrekParser()

    def test_standard(self):
        self.assertEqual(self.parser.filter_duration("duration", "0 h 30"), 0.5)
        self.assertFalse(self.parser.warnings)

    def test_upper_h(self):
        self.assertEqual(self.parser.filter_duration("duration", "1 H 06"), 1.1)
        self.assertFalse(self.parser.warnings)

    def test_spaceless(self):
        self.assertEqual(self.parser.filter_duration("duration", "2h45"), 2.75)
        self.assertFalse(self.parser.warnings)

    def test_no_minutes(self):
        self.assertEqual(self.parser.filter_duration("duration", "3 h"), 3.0)
        self.assertFalse(self.parser.warnings)

    def test_no_hours(self):
        self.assertEqual(self.parser.filter_duration("duration", "h 12"), None)
        self.assertTrue(self.parser.warnings)

    def test_spacefull(self):
        self.assertEqual(
            self.parser.filter_duration("duration", "\n \t  4     h\t9\r\n"), 4.15
        )
        self.assertFalse(self.parser.warnings)

    def test_float(self):
        self.assertEqual(self.parser.filter_duration("duration", "5.678"), 5.678)
        self.assertFalse(self.parser.warnings)

    def test_coma(self):
        self.assertEqual(self.parser.filter_duration("duration", "6,7"), 6.7)
        self.assertFalse(self.parser.warnings)

    def test_integer(self):
        self.assertEqual(self.parser.filter_duration("duration", "7"), 7.0)
        self.assertFalse(self.parser.warnings)

    def test_negative_number(self):
        self.assertEqual(self.parser.filter_duration("duration", "-8"), None)
        self.assertTrue(self.parser.warnings)

    def test_negative_hours(self):
        self.assertEqual(self.parser.filter_duration("duration", "-8 h 00"), None)
        self.assertTrue(self.parser.warnings)

    def test_negative_minutes(self):
        self.assertEqual(self.parser.filter_duration("duration", "8 h -15"), None)
        self.assertTrue(self.parser.warnings)

    def test_min_gte_60(self):
        self.assertEqual(self.parser.filter_duration("duration", "9 h 60"), None)
        self.assertTrue(self.parser.warnings)


class TrekParserFilterGeomTests(TestCase):
    def setUp(self):
        self.parser = TrekParser()

    def test_empty_geom(self):
        self.assertEqual(self.parser.filter_geom("geom", None), None)
        self.assertFalse(self.parser.warnings)

    def test_point(self):
        geom = Point(0, 0)
        with self.assertRaisesRegex(
            RowImportError,
            "Invalid geometry type for field 'geom'. Should be LineString, not Point",
        ):
            self.parser.filter_geom("geom", geom)

    def test_linestring(self):
        geom = LineString((0, 0), (0, 1), (1, 1), (1, 0))
        self.assertEqual(self.parser.filter_geom("geom", geom), geom)
        self.assertFalse(self.parser.warnings)

    def test_multilinestring(self):
        geom = MultiLineString(LineString((0, 0), (0, 1), (1, 1), (1, 0)))
        self.assertEqual(
            self.parser.filter_geom("geom", geom),
            LineString((0, 0), (0, 1), (1, 1), (1, 0)),
        )
        self.assertFalse(self.parser.warnings)

    def test_multilinestring_with_hole(self):
        geom = MultiLineString(
            LineString((0, 0), (0, 1)), LineString((100, 100), (100, 101))
        )
        self.assertEqual(
            self.parser.filter_geom("geom", geom),
            LineString((0, 0), (0, 1), (100, 100), (100, 101)),
        )

        self.assertTrue(self.parser.warnings)


WKT = (
    b"LINESTRING (356392.899 6689612.103, 356466.059 6689740.132, 356411.189 6689868.161, 356566.653 6689904.741, "
    b"356712.972 6689804.146, 356703.827 6689703.552, 356621.523 6689639.537, 356612.378 6689511.508, "
    b"356447.769 6689502.363)"
)


class TrekParserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.difficulty = DifficultyLevel.objects.create(difficulty="Facile")
        cls.route = Route.objects.create(route="Boucle")
        cls.themes = (
            Theme.objects.create(label="Littoral"),
            Theme.objects.create(label="Marais"),
        )
        cls.filetype = FileType.objects.create(type="Photographie")

    def test_create(self):
        filename = os.path.join(os.path.dirname(__file__), "data", "trek.shp")
        call_command(
            "import", "geotrek.trekking.parsers.TrekParser", filename, verbosity=0
        )
        trek = Trek.objects.all().last()
        self.assertEqual(trek.name, "Balade")
        self.assertEqual(trek.difficulty, self.difficulty)
        self.assertEqual(trek.route, self.route)
        self.assertListEqual(
            list(trek.themes.all().values_list("pk", flat=True)),
            [t.pk for t in self.themes],
        )
        self.assertEqual(WKTWriter(precision=3).write(trek.geom), WKT)


WKT_POI = b"POINT (1.5238 43.5294)"


class POIParserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.poi_type_e = POIType.objects.create(label="équipement")
        cls.poi_type_s = POIType.objects.create(label="signaletique")
        cls.filetype = FileType.objects.create(type="Photographie")

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_import_cmd_raises_error_when_no_path(self):
        filename = os.path.join(os.path.dirname(__file__), "data", "poi.shp")
        with self.assertRaisesRegex(
            CommandError, "You need to add a network of paths before importing POIs"
        ):
            call_command(
                "import", "geotrek.trekking.parsers.POIParser", filename, verbosity=0
            )

    def test_import_cmd_raises_wrong_geom_type(self):
        PathFactory.create(geom=LineString((0, 0), (0, 10), srid=4326))
        filename = os.path.join(os.path.dirname(__file__), "data", "trek.shp")
        output = StringIO()
        call_command(
            "import",
            "geotrek.trekking.parsers.POIParser",
            filename,
            verbosity=2,
            stdout=output,
        )
        self.assertEqual(POI.objects.count(), 0)
        self.assertIn(
            "Invalid geometry type for field 'GEOM'. Should be Point, not LineString,",
            output.getvalue(),
        )

    def test_import_cmd_raises_no_geom(self):
        with self.assertLogs(level="WARNING") as log:
            PathFactory.create(geom=LineString((0, 0), (0, 10), srid=4326))
            filename = os.path.join(
                os.path.dirname(__file__), "data", "empty_geom.geojson"
            )
            output = StringIO()
            call_command(
                "import",
                "geotrek.trekking.parsers.POIParser",
                filename,
                verbosity=2,
                stdout=output,
            )
            self.assertEqual(POI.objects.count(), 0)
            self.assertIn("Invalid geometry", log.output[-1])

    def test_create(self):
        PathFactory.create(geom=LineString((0, 0), (0, 10), srid=4326))
        filename = os.path.join(os.path.dirname(__file__), "data", "poi.shp")
        call_command(
            "import", "geotrek.trekking.parsers.POIParser", filename, verbosity=0
        )
        poi = POI.objects.all().last()
        self.assertEqual(poi.name, "pont")
        poi.reload()
        self.assertEqual(WKTWriter(precision=4).write(poi.geom), WKT_POI)
        self.assertEqual(poi.geom, poi.geom_3d)


class TestGeotrekTrekParser(GeotrekTrekParser):
    url = "https://test.fr"
    provider = "geotrek1"
    field_options = {
        "difficulty": {
            "create": True,
        },
        "route": {
            "create": True,
        },
        "themes": {"create": True},
        "practice": {"create": True},
        "accessibilities": {"create": True},
        "networks": {"create": True},
        "geom": {"required": True},
        "labels": {"create": True},
        "source": {"create": True},
        "structure": {
            "create": True,
        },
    }


class TestGeotrek2TrekParser(GeotrekTrekParser):
    url = "https://test.fr"

    field_options = {
        "geom": {"required": True},
    }
    provider = "geotrek2"


class TestGeotrekPOIParser(GeotrekPOIParser):
    url = "https://test.fr"

    field_options = {
        "type": {
            "create": True,
        },
        "structure": {
            "create": True,
        },
        "geom": {"required": True},
    }


class TestGeotrekServiceParser(GeotrekServiceParser):
    url = "https://test.fr"

    field_options = {
        "type": {
            "create": True,
        },
        "structure": {
            "create": True,
        },
        "geom": {"required": True},
    }


@override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class TrekGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids.json"),
            ("trekking", "trek.json"),
            ("trekking", "trek_children.json"),
            ("trekking", "trek_published_step.json"),
            ("trekking", "trek_unpublished_step.json"),
            ("trekking", "trek_unpublished_structure.json"),
            ("trekking", "trek_unpublished_practice.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=0,
        )
        self.assertEqual(Trek.objects.count(), 6)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name_it, "Foo bar")
        self.assertEqual(trek.name_es, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.published, True)
        self.assertEqual(trek.published_fr, True)
        self.assertEqual(trek.published_en, True)
        self.assertEqual(trek.published_it, False)
        self.assertEqual(trek.published_es, False)
        self.assertEqual(str(trek.difficulty), "Très facile")
        self.assertEqual(str(trek.structure), "Struct1")
        self.assertEqual(str(trek.practice), "Cheval")
        self.assertAlmostEqual(trek.geom[0][0], 569946.9850365581, places=5)
        self.assertAlmostEqual(trek.geom[0][1], 6190964.893167565, places=5)
        self.assertEqual(trek.children.first().name, "Foo")
        self.assertEqual(trek.children.last().name, "Etape non publiée")
        self.assertEqual(trek.children.last().practice.name, "Pratique non publiée")
        self.assertEqual(trek.labels.count(), 3)
        self.assertEqual(trek.source.first().name, "Une source numero 2")
        self.assertEqual(
            trek.source.first().website, "https://www.ecrins-parcnational.fr"
        )
        self.assertEqual(trek.labels.first().name, "Chien autorisé")
        self.assertEqual(Attachment.objects.filter(object_id=trek.pk).count(), 3)
        self.assertEqual(
            Attachment.objects.get(
                object_id=trek.pk, license__isnull=False
            ).license.label,
            "License",
        )

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    def test_create_multiple_page(self, mocked_head, mocked_get):
        class MockResponse:
            mock_json_order = [
                ("trekking", "structure.json"),
                ("trekking", "trek_difficulty.json"),
                ("trekking", "trek_route.json"),
                ("trekking", "trek_theme.json"),
                ("trekking", "trek_practice.json"),
                ("trekking", "trek_accessibility.json"),
                ("trekking", "trek_network.json"),
                ("trekking", "trek_label.json"),
                ("trekking", "sources.json"),
                ("trekking", "sources.json"),
                ("trekking", "trek_ids.json"),
                ("trekking", "trek.json"),
                ("trekking", "trek_children.json"),
                ("trekking", "trek_published_step.json"),
                ("trekking", "trek_unpublished_step.json"),
                ("trekking", "trek_unpublished_structure.json"),
                ("trekking", "trek_unpublished_practice.json"),
                ("trekking", "trek_children.json"),
                ("trekking", "trek_published_step.json"),
                ("trekking", "trek_unpublished_step.json"),
                ("trekking", "trek_unpublished_structure.json"),
                ("trekking", "trek_unpublished_practice.json"),
            ]
            mock_time = 0
            total_mock_response = 1

            def __init__(self, status_code):
                self.status_code = status_code

            def json(self):
                filename = os.path.join(
                    "geotrek",
                    self.mock_json_order[self.mock_time][0],
                    "tests",
                    "data",
                    "geotrek_parser_v2",
                    self.mock_json_order[self.mock_time][1],
                )
                with open(filename) as f:
                    data_json = json.load(f)
                    if self.mock_json_order[self.mock_time] == "trek.json":
                        data_json["count"] = 10
                        if self.total_mock_response == 1:
                            self.total_mock_response += 1
                            data_json["next"] = "foo"
                    self.mock_time += 1
                    return data_json

            @property
            def content(self):
                return b""

        # Mock GET
        mocked_get.return_value = MockResponse(200)
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=0,
        )
        self.assertEqual(Trek.objects.count(), 6)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name_it, "Foo bar")
        self.assertEqual(str(trek.difficulty), "Très facile")
        self.assertEqual(str(trek.practice), "Cheval")
        self.assertAlmostEqual(trek.geom[0][0], 569946.9850365581, places=5)
        self.assertAlmostEqual(trek.geom[0][1], 6190964.893167565, places=5)
        self.assertEqual(trek.children.first().name, "Foo")
        self.assertEqual(trek.labels.count(), 3)
        self.assertEqual(trek.labels.first().name, "Chien autorisé")
        self.assertEqual(Attachment.objects.filter(object_id=trek.pk).count(), 3)
        self.assertEqual(
            Attachment.objects.get(
                object_id=trek.pk, license__isnull=False
            ).license.label,
            "License",
        )

    @override_settings(PAPERCLIP_MAX_BYTES_SIZE_IMAGE=1)
    @mock.patch("requests.get")
    @mock.patch("requests.head")
    def test_create_attachment_max_size(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids.json"),
            ("trekking", "trek.json"),
            ("trekking", "trek_children.json"),
            ("trekking", "trek_published_step.json"),
            ("trekking", "trek_unpublished_step.json"),
            ("trekking", "trek_unpublished_structure.json"),
            ("trekking", "trek_unpublished_practice.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b"11"
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=0,
        )
        self.assertEqual(Trek.objects.count(), 6)
        self.assertEqual(Attachment.objects.count(), 0)

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    def test_update_attachment(self, mocked_head, mocked_get):
        class MockResponse:
            mock_json_order = [
                ("trekking", "structure.json"),
                ("trekking", "trek_difficulty.json"),
                ("trekking", "trek_route.json"),
                ("trekking", "trek_theme.json"),
                ("trekking", "trek_practice.json"),
                ("trekking", "trek_accessibility.json"),
                ("trekking", "trek_network.json"),
                ("trekking", "trek_label.json"),
                ("trekking", "sources.json"),
                ("trekking", "sources.json"),
                ("trekking", "trek_ids.json"),
                ("trekking", "trek.json"),
                ("trekking", "trek_children.json"),
                ("trekking", "trek_published_step.json"),
                ("trekking", "trek_unpublished_step.json"),
                ("trekking", "trek_unpublished_structure.json"),
                ("trekking", "trek_unpublished_practice.json"),
            ]
            mock_time = 0
            a = 0

            def __init__(self, status_code):
                self.status_code = status_code

            def json(self):
                if len(self.mock_json_order) <= self.mock_time:
                    self.mock_time = 0
                filename = os.path.join(
                    "geotrek",
                    self.mock_json_order[self.mock_time][0],
                    "tests",
                    "data",
                    "geotrek_parser_v2",
                    self.mock_json_order[self.mock_time][1],
                )

                self.mock_time += 1
                with open(filename) as f:
                    return json.load(f)

            @property
            def content(self):
                # We change content of attachment every time
                self.a += 1
                return bytes(f"{self.a}", "utf-8")

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value = MockResponse(200)
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=0,
        )
        self.assertEqual(Trek.objects.count(), 6)
        trek = Trek.objects.all().first()
        self.assertEqual(Attachment.objects.filter(object_id=trek.pk).count(), 3)
        self.assertEqual(Attachment.objects.first().attachment_file.read(), b"20")
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=0,
        )
        self.assertEqual(Trek.objects.count(), 6)
        trek.refresh_from_db()
        self.assertEqual(Attachment.objects.filter(object_id=trek.pk).count(), 3)
        self.assertEqual(Attachment.objects.first().attachment_file.read(), b"35")

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
    def test_create_multiple_fr(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids.json"),
            ("trekking", "trek.json"),
            ("trekking", "trek_children.json"),
            ("trekking", "trek_published_step.json"),
            ("trekking", "trek_unpublished_step.json"),
            ("trekking", "trek_unpublished_structure.json"),
            ("trekking", "trek_unpublished_practice.json"),
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids_2.json"),
            ("trekking", "trek_2.json"),
            ("trekking", "trek_no_children.json"),
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids_2.json"),
            ("trekking", "trek_2_after.json"),
            ("trekking", "trek_no_children.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=0,
        )
        self.assertEqual(Trek.objects.count(), 6)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name_en, "Loop of the pic of 3 lords")
        self.assertEqual(trek.name_fr, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(str(trek.difficulty), "Très facile")
        self.assertEqual(str(trek.practice), "Cheval")
        self.assertAlmostEqual(trek.geom[0][0], 569946.9850365581, places=5)
        self.assertAlmostEqual(trek.geom[0][1], 6190964.893167565, places=5)
        self.assertEqual(trek.children.first().name, "Foo")
        self.assertEqual(trek.labels.count(), 3)
        self.assertEqual(trek.labels.first().name, "Chien autorisé")
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrek2TrekParser",
            verbosity=0,
        )
        self.assertEqual(Trek.objects.count(), 7)
        trek = Trek.objects.get(name_fr="Étangs du Picot")
        self.assertEqual(trek.description_teaser_fr, "Chapeau")
        self.assertEqual(trek.description_teaser_it, "Cappello")
        self.assertEqual(trek.description_teaser_es, "Chapeau")
        self.assertEqual(trek.description_teaser_en, "Cap")
        self.assertEqual(trek.description_teaser, "Chapeau")
        self.assertEqual(trek.published, True)
        self.assertEqual(trek.published_fr, True)
        self.assertEqual(trek.published_en, False)
        self.assertEqual(trek.published_it, False)
        self.assertEqual(trek.published_es, False)
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrek2TrekParser",
            verbosity=0,
        )
        trek.refresh_from_db()
        self.assertEqual(Trek.objects.count(), 7)
        self.assertEqual(trek.description_teaser_fr, "Chapeau 2")
        self.assertEqual(trek.description_teaser_it, "Cappello 2")
        self.assertEqual(trek.description_teaser_es, "Sombrero 2")
        self.assertEqual(trek.description_teaser_en, "Cap 2")
        self.assertEqual(trek.description_teaser, "Chapeau 2")
        self.assertEqual(trek.published, True)
        self.assertEqual(trek.published_fr, True)
        self.assertEqual(trek.published_en, False)
        self.assertEqual(trek.published_it, False)
        self.assertEqual(trek.published_es, False)

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="en", LANGUAGE_CODE="en")
    def test_create_multiple_en(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids.json"),
            ("trekking", "trek.json"),
            ("trekking", "trek_children.json"),
            ("trekking", "trek_published_step.json"),
            ("trekking", "trek_unpublished_step.json"),
            ("trekking", "trek_unpublished_structure.json"),
            ("trekking", "trek_unpublished_practice.json"),
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids_2.json"),
            ("trekking", "trek_2.json"),
            ("trekking", "trek_no_children.json"),
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids_2.json"),
            ("trekking", "trek_2_after.json"),
            ("trekking", "trek_no_children.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=0,
        )
        self.assertEqual(Trek.objects.count(), 6)
        trek = Trek.objects.get(name_fr="Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name, "Loop of the pic of 3 lords")
        self.assertEqual(trek.name_en, "Loop of the pic of 3 lords")
        self.assertEqual(trek.name_fr, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(str(trek.difficulty), "Very easy")
        self.assertEqual(str(trek.difficulty.difficulty_en), "Very easy")
        self.assertEqual(str(trek.practice), "Horse")
        self.assertAlmostEqual(trek.geom[0][0], 569946.9850365581, places=5)
        self.assertAlmostEqual(trek.geom[0][1], 6190964.893167565, places=5)
        self.assertEqual(trek.children.first().name, "Bar")
        self.assertEqual(trek.labels.count(), 3)
        self.assertEqual(trek.labels.first().name, "Dogs are great")
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrek2TrekParser",
            verbosity=0,
        )
        self.assertEqual(Trek.objects.count(), 7)
        trek = Trek.objects.get(name_fr="Étangs du Picot")
        self.assertEqual(trek.description_teaser_fr, "Chapeau")
        self.assertEqual(trek.description_teaser_it, "Cappello")
        self.assertEqual(trek.description_teaser_es, "Cap")
        self.assertEqual(trek.description_teaser_en, "Cap")
        self.assertEqual(trek.description_teaser, "Cap")
        self.assertEqual(trek.published, False)
        self.assertEqual(trek.published_fr, True)
        self.assertEqual(trek.published_en, False)
        self.assertEqual(trek.published_it, False)
        self.assertEqual(trek.published_es, False)
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrek2TrekParser",
            verbosity=0,
        )
        trek.refresh_from_db()
        self.assertEqual(Trek.objects.count(), 7)
        self.assertEqual(trek.description_teaser_fr, "Chapeau 2")
        self.assertEqual(trek.description_teaser_it, "Cappello 2")
        self.assertEqual(trek.description_teaser_es, "Sombrero 2")
        self.assertEqual(trek.description_teaser_en, "Cap 2")
        self.assertEqual(trek.description_teaser, "Cap 2")
        self.assertEqual(trek.published, False)
        self.assertEqual(trek.published_fr, True)
        self.assertEqual(trek.published_en, False)
        self.assertEqual(trek.published_it, False)
        self.assertEqual(trek.published_es, False)

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    def test_children_do_not_exist(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids.json"),
            ("trekking", "trek.json"),
            ("trekking", "trek_children_do_not_exist.json"),
            ("trekking", "trek_published_step.json"),
            ("trekking", "trek_unpublished_step.json"),
            ("trekking", "trek_unpublished_structure.json"),
            ("trekking", "trek_unpublished_practice_not_found.json"),
            ("trekking", "trek_published_step_2.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200
        output = StringIO()
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=2,
            stdout=output,
        )
        self.assertIn(
            "Trying to retrieve children for missing trek : could not find trek with UUID b2aea666-5e6e-4daa-a750-7d2ee52d3fe1",
            output.getvalue(),
        )
        treks = Trek.objects.all()
        self.assertEqual(len(treks), 7)
        actual_uuids = treks.values_list("eid", flat=True)
        expected_steps_uuids = [
            "c9567576-2934-43ab-979e-e13d02c671a9",
            "9e70b294-1134-4c50-9c56-d722720cace6",
            # Checking that this step has been parsed even though the previous one
            # (child of b2aea666-5e6e-4daa-a750-7d2ee52d3fe1) failed:
            "c9567576-2934-43ab-979e-e13d02c671a8",
        ]
        self.assertTrue(set(expected_steps_uuids).issubset(set(actual_uuids)))

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    def test_wrong_children_error(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids.json"),
            ("trekking", "trek.json"),
            ("trekking", "trek_children.json"),
            ("trekking", "trek_not_found.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200
        output = StringIO()

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=2,
            stdout=output,
        )
        self.assertIn(
            "An error occurred in children generation: DownloadImportError",
            output.getvalue(),
        )

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
    def test_updated(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids.json"),
            ("trekking", "trek.json"),
            ("trekking", "trek_children.json"),
            ("trekking", "trek_published_step.json"),
            ("trekking", "trek_unpublished_step.json"),
            ("trekking", "trek_unpublished_structure.json"),
            ("trekking", "trek_unpublished_practice.json"),
            ("trekking", "structure.json"),
            ("trekking", "trek_difficulty.json"),
            ("trekking", "trek_route.json"),
            ("trekking", "trek_theme.json"),
            ("trekking", "trek_practice.json"),
            ("trekking", "trek_accessibility.json"),
            ("trekking", "trek_network.json"),
            ("trekking", "trek_label.json"),
            ("trekking", "sources.json"),
            ("trekking", "sources.json"),
            ("trekking", "trek_ids_2.json"),
            ("trekking", "trek_2.json"),
            ("trekking", "trek_children.json"),
            ("trekking", "trek_published_step.json"),
            ("trekking", "trek_unpublished_step.json"),
            ("trekking", "trek_unpublished_structure.json"),
            ("trekking", "trek_unpublished_practice.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=0,
        )
        self.assertEqual(Trek.objects.count(), 6)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name_fr, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name_en, "Loop of the pic of 3 lords")
        self.assertEqual(str(trek.difficulty), "Très facile")
        self.assertEqual(str(trek.practice), "Cheval")
        self.assertAlmostEqual(trek.geom[0][0], 569946.9850365581, places=5)
        self.assertAlmostEqual(trek.geom[0][1], 6190964.893167565, places=5)
        self.assertEqual(trek.children.first().name, "Foo")
        self.assertEqual(trek.labels.count(), 3)
        self.assertEqual(trek.labels.first().name, "Chien autorisé")
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser",
            verbosity=0,
        )
        # Trek 2 is still in ids (trek_ids_2) => it's not removed, and neither are its children
        self.assertEqual(Trek.objects.count(), 4)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name, "Boucle du Pic des Trois Seigneurs")


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class POIGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = "trekking"

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="en")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("trekking", "structure.json"),
            ("trekking", "poi_type.json"),
            ("trekking", "poi_ids.json"),
            ("trekking", "poi.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekPOIParser",
            verbosity=0,
        )
        self.assertEqual(POI.objects.count(), 2)
        poi = POI.objects.all().first()
        self.assertEqual(poi.name, "Peak of the Three Lords")
        self.assertEqual(poi.name_fr, "Pic des Trois Seigneurs")
        self.assertEqual(poi.name_en, "Peak of the Three Lords")
        self.assertEqual(poi.name_it, "Picco dei Tre Signori")
        self.assertEqual(poi.name_es, "Peak of the Three Lords")
        self.assertEqual(poi.name_es, "Peak of the Three Lords")
        self.assertEqual(poi.published, False)
        self.assertEqual(poi.published_fr, True)
        self.assertEqual(poi.published_en, False)
        self.assertEqual(poi.published_it, False)
        self.assertEqual(poi.published_es, False)
        self.assertEqual(str(poi.structure), "Struct3")
        self.assertEqual(str(poi.type), "Peak")
        self.assertAlmostEqual(poi.geom.x, 572298.7056448072, places=5)
        self.assertAlmostEqual(poi.geom.y, 6193580.839504813, places=5)


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class ServiceGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = "trekking"

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("trekking", "structure.json"),
            ("trekking", "service_type.json"),
            ("trekking", "service_ids.json"),
            ("trekking", "service.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestGeotrekServiceParser",
            verbosity=0,
        )
        self.assertEqual(Service.objects.count(), 2)
        service = Service.objects.all().first()
        self.assertEqual(str(service.type), "Eau potable")
        self.assertEqual(str(service.structure), "Struct3")
        self.assertAlmostEqual(service.geom.x, 572096.2266745908, places=5)
        self.assertAlmostEqual(service.geom.y, 6192330.15779677, places=5)


def make_dummy_apidae_get(parser_class, test_data_dir, data_filename):
    """Returns a mocked_get. The mocked_get may return:
    - `data_filename` content on call to APIDAE API,
    - Geometric data file content (the filename is taken from the request's path),
    - a dummy jpg content if a jpg file is requested.

    parser_class: the class of the parser instance which will call this mocked_get
    test_data_dir: the path of the directory containing test data relative to the python project root
    data_filename: the data to return as get response when the parser calls APIDAE API
    """

    def dummy_get(url, *args, **kwargs):
        rv = Mock()
        rv.status_code = 200
        if url == parser_class.url:
            filename = os.path.join(test_data_dir, data_filename)
            with open(filename) as f:
                json_payload = f.read()
            data = json.loads(json_payload)
            rv.json = lambda: data
        else:
            parsed_url = urlparse(url)
            url_path = parsed_url.path
            extension = url_path.split(".")[1]
            if extension == "jpg":
                rv.content = copy(testdata.IMG_FILE)
            elif extension in ["gpx", "kml"]:
                filename = os.path.join(test_data_dir, url_path.lstrip("/"))
                with open(filename) as f:
                    geodata = f.read()
                rv.content = bytes(geodata, "utf-8")
            elif extension == "kmz":
                filename = os.path.join(test_data_dir, url_path.lstrip("/"))
                with open(filename, "rb") as f:
                    geodata = f.read()
                rv.content = geodata
        return rv

    return dummy_get


class TestApidaeTrekParser(ApidaeTrekParser):
    url = "https://example.net/fake/api/"
    api_key = "ABCDEF"
    project_id = 1234
    selection_id = 654321


class TestApidaeTrekSameValueDefaultLanguageDifferentTranslationParser(
    TestApidaeTrekParser
):
    def filter_description(self, src, val):
        description = super().filter_description(src, val)
        self.set_value("description_fr", src, "FOOBAR")
        return description


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class ApidaeTrekParserTests(TestCase):
    @staticmethod
    def make_dummy_get(apidae_data_file):
        return make_dummy_apidae_get(
            parser_class=TestApidaeTrekParser,
            test_data_dir="geotrek/trekking/tests/data/apidae_trek_parser",
            data_filename=apidae_data_file,
        )

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    def test_trek_is_imported(self, mocked_get):
        RouteFactory(route="Boucle")
        mocked_get.side_effect = self.make_dummy_get("a_trek.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name_fr, "Une belle randonnée de test")
        self.assertEqual(trek.name_en, "A great hike to test")
        self.assertEqual(
            trek.description_teaser_fr, "La description courte en français."
        )
        self.assertEqual(
            trek.description_teaser_en, "The short description in english."
        )
        self.assertEqual(trek.ambiance_fr, "La description détaillée en français.")
        self.assertEqual(trek.ambiance_en, "The longer description in english.")
        expected_fr_description = (
            "<p>Départ : du parking de la Chapelle Saint Michel </p>"
            "<p>1/ Suivre le chemin qui part à droite, traversant le vallon.</p>"
            "<p>2/ Au carrefour tourner à droite et suivre la rivière</p>"
            "<p>3/ Retour à la chapelle en passant à travers le petit bois.</p>"
            "<p>Ouvert toute l'année</p>"
            "<p>Fermeture exceptionnelle en cas de pluie forte</p>"
            "<p>Suivre le balisage GR (blanc/rouge) ou GRP (jaune/rouge).</p>"
            "<p>Montée en télésiège payante. 2 points de vente - télésiège Frastaz et Bois Noir.</p>"
            "<p><strong>Site web (URL):</strong>https://example.com/ma_rando.html<br>"
            "<strong>Téléphone:</strong>01 23 45 67 89<br>"
            "<strong>Mél:</strong>accueil-rando@example.com<br>"
            "<strong>Signaux de fumée:</strong>1 gros nuage suivi de 2 petits</p>"
        )
        self.assertEqual(trek.description_fr, expected_fr_description)
        expected_en_description = (
            "<p>Start: from the parking near the Chapelle Saint Michel </p>"
            "<p>1/ Follow the path starting at right-hand, cross the valley.</p>"
            "<p>2/ At the crossroad turn left and follow the river.</p>"
            "<p>3/ Back to the chapelle by the woods.</p>"
            "<p>Open all year long</p>"
            "<p>Exceptionally closed during heavy rain</p>"
            "<p>Follow the GR (white / red) or GRP (yellow / red) markings.</p>"
            "<p>Ski lift ticket office: 2 shops - Frastaz and Bois Noir ski lifts.</p>"
            "<p><strong>Website:</strong>https://example.com/ma_rando.html<br>"
            "<strong>Telephone:</strong>01 23 45 67 89<br>"
            "<strong>e-mail:</strong>accueil-rando@example.com<br>"
            "<strong>Smoke signals:</strong>1 gros nuage suivi de 2 petits</p>"
        )
        self.assertEqual(trek.description_en, expected_en_description)
        self.assertEqual(trek.advised_parking_fr, "Parking sur la place du village")
        self.assertEqual(trek.advised_parking_en, "Parking sur la place du village")
        self.assertEqual(trek.departure_fr, "Sallanches")
        self.assertEqual(trek.departure_en, "Sallanches")
        self.assertEqual(
            trek.access_fr, "En voiture, rejoindre le village de Salanches."
        )
        self.assertEqual(trek.access_en, "By car, go to the village of Sallanches.")
        self.assertEqual(trek.access_it, "In auto, andare al villaggio di Sallances.")
        self.assertEqual(len(trek.source.all()), 1)
        self.assertEqual(trek.source.first().name, "Office de tourisme de Sallanches")
        self.assertEqual(
            trek.source.first().website, "https://www.example.net/ot-sallanches"
        )
        self.assertEqual(trek.structure.name, "Office de tourisme de Sallanches")

        self.assertTrue(trek.difficulty is not None)
        self.assertEqual(trek.difficulty.difficulty_en, "Level red – hard")

        self.assertTrue(trek.practice is not None)
        self.assertEqual(trek.practice.name, "Pédestre")

        self.assertEqual(trek.networks.count(), 2)
        networks = trek.networks.all()
        self.assertIn("Hiking itinerary", [n.network for n in networks])
        self.assertIn("Pedestrian sports", [n.network for n in networks])

        self.assertEqual(Attachment.objects.count(), 1)
        photo = Attachment.objects.first()
        self.assertEqual(photo.author, "The author of the picture")
        self.assertEqual(photo.legend, "The legend of the picture")
        self.assertEqual(photo.attachment_file.size, len(testdata.IMG_FILE))
        self.assertEqual(photo.title, "The title of the picture")

        self.assertTrue(trek.duration is not None)
        self.assertAlmostEqual(trek.duration, 2.5)

        self.assertEqual(trek.advice, "Avoid after heavy rain.")
        self.assertEqual(trek.advice_fr, "À éviter après de grosses pluies.")

        self.assertEqual(trek.route.route, "Boucle")

        self.assertEqual(trek.accessibilities.count(), 1)
        accessibility = trek.accessibilities.first()
        self.assertEqual(accessibility.name, "Suitable for all terrain strollers")

        self.assertIn("Rock", trek.accessibility_covering)
        self.assertIn("Ground", trek.accessibility_covering)
        self.assertIn("Rocher", trek.accessibility_covering_fr)
        self.assertIn("Terre", trek.accessibility_covering_fr)

        self.assertTrue(trek.gear is not None)
        self.assertIn("Map IGN3531OT Top 25", trek.gear)
        self.assertIn("Guidebook sold at the tourist board", trek.gear)
        self.assertIn("TOP 25 IGN 3531 OT", trek.gear_fr)
        self.assertIn("Cartoguide en vente à l'Office de Tourisme", trek.gear_fr)

        # Import an updated trek
        mocked_get.side_effect = self.make_dummy_get(
            "a_trek_with_updated_limit_date.json"
        )
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Attachment.objects.count(), 0)

    @mock.patch("requests.get")
    def test_trek_import_multiple_time(self, mocked_get):
        RouteFactory(route="Boucle")
        mocked_get.side_effect = self.make_dummy_get("a_trek.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        old_description_en = trek.description_en
        old_description = trek.description
        description_fr = (
            "<p>Départ : du parking de la Chapelle Saint Michel </p>"
            "<p>1/ Suivre le chemin qui part à droite, traversant le vallon.</p>"
            "<p>2/ Au carrefour tourner à droite et suivre la rivière</p>"
            "<p>3/ Retour à la chapelle en passant à travers le petit bois.</p>"
            "<p>Ouvert toute l'année</p>"
            "<p>Fermeture exceptionnelle en cas de pluie forte</p>"
            "<p>Suivre le balisage GR (blanc/rouge) ou GRP (jaune/rouge).</p>"
            "<p>Montée en télésiège payante. 2 points de vente - télésiège Frastaz et Bois Noir.</p>"
            "<p><strong>Site web (URL):</strong>https://example.com/ma_rando.html<br>"
            "<strong>Téléphone:</strong>01 23 45 67 89<br>"
            "<strong>Mél:</strong>accueil-rando@example.com<br>"
            "<strong>Signaux de fumée:</strong>1 gros nuage suivi de 2 petits</p>"
        )
        self.assertEqual(trek.description_fr, description_fr)
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekSameValueDefaultLanguageDifferentTranslationParser",
            verbosity=0,
        )
        trek.refresh_from_db()
        self.assertEqual(trek.description_fr, "FOOBAR")
        self.assertEqual(old_description_en, trek.description_en)
        self.assertEqual(old_description, trek.description)

    @mock.patch("requests.get")
    def test_trek_geometry_can_be_imported_from_gpx(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get("a_trek.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.geom.srid, 2154)
        self.assertEqual(len(trek.geom.coords), 13)
        first_point = trek.geom.coords[0]
        self.assertAlmostEqual(first_point[0], 977776.9, delta=0.1)
        self.assertAlmostEqual(first_point[1], 6547354.8, delta=0.1)

    @mock.patch("requests.get")
    def test_trek_geometry_can_be_imported_from_kml(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get("trek_with_kml_trace.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.geom.srid, 2154)
        self.assertEqual(len(trek.geom.coords), 61)

    @mock.patch("requests.get")
    def test_trek_geometry_can_be_imported_from_kmz(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get("trek_with_kmz_trace.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.geom.srid, 2154)
        self.assertEqual(len(trek.geom.coords), 61)

    @mock.patch("requests.get")
    def test_trek_not_imported_when_no_supported_format(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get(
            "trek_no_supported_plan_format_error.json"
        )

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=2,
            stdout=output_stdout,
        )

        self.assertEqual(Trek.objects.count(), 0)
        self.assertIn(
            'has no attached "PLAN" in a supported format', output_stdout.getvalue()
        )

    @mock.patch("requests.get")
    def test_trek_plan_without_extension_property(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get(
            "trek_with_plan_without_extension_prop.json"
        )

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=2,
            stdout=output_stdout,
        )

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.geom.srid, 2154)
        self.assertEqual(len(trek.geom.coords), 61)

    @mock.patch("requests.get")
    def test_trek_plan_with_no_extension_at_all(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get(
            "trek_with_plan_with_no_extension_at_all.json"
        )

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=2,
            stdout=output_stdout,
        )

        self.assertEqual(Trek.objects.count(), 0)
        self.assertIn(
            'has no attached "PLAN" in a supported format', output_stdout.getvalue()
        )

    @mock.patch("requests.get")
    def test_trek_not_imported_when_no_plan_attached(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get("trek_no_plan_error.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=2,
            stdout=output_stdout,
        )

        self.assertEqual(Trek.objects.count(), 0)
        self.assertIn('no attachment with the type "PLAN"', output_stdout.getvalue())

    @mock.patch("requests.get")
    def test_trek_not_imported_when_bad_geometry(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get("a_trek_with_bad_geom.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=2,
            stdout=output_stdout,
        )

        self.assertEqual(Trek.objects.count(), 0)
        self.assertIn(
            "Geometries from various features cannot be converted to a single continuous LineString feature,",
            output_stdout.getvalue(),
        )

    @mock.patch("requests.get")
    def test_trek_not_imported_when_no_plan(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get("trek_no_plan_error.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=2,
            stdout=output_stdout,
        )

        self.assertEqual(Trek.objects.count(), 0)
        self.assertIn(
            'has no attachment with the type "PLAN"', output_stdout.getvalue()
        )

    @mock.patch("requests.get")
    def test_trek_not_imported_when_no_multimedia_attachments(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get(
            "trek_no_multimedia_attachments_error.json"
        )

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=2,
            stdout=output_stdout,
        )

        self.assertEqual(Trek.objects.count(), 0)
        self.assertIn(
            "missing required field 'multimedias'", output_stdout.getvalue().lower()
        )

    @mock.patch("requests.get")
    def test_trek_linked_entities_are_imported(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get("a_trek.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Theme.objects.count(), 2)
        themes = Theme.objects.all()
        for theme in themes:
            self.assertIn(theme.label, ["Geology", "Historic"])
        self.assertEqual(Label.objects.count(), 3)
        labels = Label.objects.all()
        for label in labels:
            self.assertIn(
                label.name,
                ["In the country", "Not recommended in bad weather", "Listed PDIPR"],
            )

    @mock.patch("requests.get")
    def test_trek_theme_with_unknown_id_is_not_imported(self, mocked_get):
        assert 12341234 not in ApidaeTrekParser.typologies_sitra_ids_as_themes

        mocked_get.side_effect = self.make_dummy_get("trek_with_unknown_theme.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Trek.objects.count(), 1)
        self.assertEqual(Theme.objects.count(), 0)

    @mock.patch("requests.get")
    def test_links_to_child_treks_are_set(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get("related_treks.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Trek.objects.count(), 3)
        parent_trek = Trek.objects.get(eid="123123")
        child_trek = Trek.objects.get(eid="123124")
        child_trek_2 = Trek.objects.get(eid="123125")
        self.assertIn(parent_trek, child_trek.parents.all())
        self.assertIn(parent_trek, child_trek_2.parents.all())
        self.assertEqual(
            list(parent_trek.children.values_list("eid", flat=True).all()),
            ["123124", "123125"],
        )

        mocked_get.side_effect = self.make_dummy_get("related_treks_updated.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Trek.objects.count(), 4)
        parent_trek = Trek.objects.get(eid="123123")
        child_trek = Trek.objects.get(eid="123124")
        child_trek_2 = Trek.objects.get(eid="123125")
        child_trek_3 = Trek.objects.get(eid="321321")
        self.assertIn(parent_trek, child_trek.parents.all())
        self.assertIn(parent_trek, child_trek_2.parents.all())
        self.assertIn(parent_trek, child_trek_3.parents.all())
        self.assertEqual(
            list(parent_trek.children.values_list("eid", flat=True).all()),
            ["123124", "321321", "123125"],
        )

    @mock.patch("requests.get")
    def test_it_handles_not_imported_child_trek(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get(
            "related_treks_with_one_not_imported.json"
        )

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Trek.objects.count(), 2)
        Trek.objects.filter(eid="123123").exists()
        Trek.objects.filter(eid="123124").exists()

    @mock.patch("requests.get")
    def test_links_to_child_treks_are_set_with_changed_order_in_data(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get("related_treks_another_order.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )

        self.assertEqual(Trek.objects.count(), 3)
        parent_trek = Trek.objects.get(eid="123123")
        child_trek = Trek.objects.get(eid="123124")
        child_trek_2 = Trek.objects.get(eid="123125")
        self.assertIn(parent_trek, child_trek.parents.all())
        self.assertIn(parent_trek, child_trek_2.parents.all())
        self.assertEqual(
            list(parent_trek.children.values_list("eid", flat=True).all()),
            ["123124", "123125"],
        )

    @mock.patch("requests.get")
    def test_trek_illustration_is_not_imported_on_missing_file_metadata(
        self, mocked_get
    ):
        mocked_get.side_effect = self.make_dummy_get(
            "trek_with_not_complete_illustration.json"
        )
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekParser",
            verbosity=0,
        )
        self.assertEqual(Attachment.objects.count(), 0)


class TestApidaeTrekThemeParser(ApidaeTrekThemeParser):
    url = "https://example.net/fake/api/"
    api_key = "ABCDEF"
    project_id = 1234
    element_reference_ids = [6157]


class ApidaeTrekThemeParserTests(TestCase):
    def mocked_get_func(self, url, params, *args, **kwargs):
        self.assertEqual(url, TestApidaeTrekThemeParser.url)
        expected_query_param = {
            "apiKey": TestApidaeTrekThemeParser.api_key,
            "projetId": TestApidaeTrekThemeParser.project_id,
            "elementReferenceIds": TestApidaeTrekThemeParser.element_reference_ids,
        }
        self.assertDictEqual(json.loads(params["query"]), expected_query_param)

        rv = Mock()
        rv.status_code = 200
        with open(
            "geotrek/trekking/tests/data/apidae_trek_parser/trek_theme.json"
        ) as f:
            json_payload = f.read()
        data = json.loads(json_payload)
        rv.json = lambda: data

        return rv

    @mock.patch("requests.get")
    def test_theme_is_created_with_configured_languages(self, mocked_get):
        mocked_get.side_effect = self.mocked_get_func

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekThemeParser",
            verbosity=0,
        )

        self.assertEqual(len(Theme.objects.all()), 1)
        theme = Theme.objects.first()
        self.assertEqual(theme.label_fr, "Géologie")
        self.assertEqual(theme.label_en, "Geology")
        self.assertEqual(theme.label_es, "Geología")
        self.assertEqual(theme.label_it, "Geologia")

    @mock.patch("requests.get")
    def test_theme_is_identified_with_default_language_on_update(self, mocked_get):
        mocked_get.side_effect = self.mocked_get_func
        theme = Theme(
            label_en="Geology", label_fr="Géologie (cette valeur sera écrasée)"
        )
        theme.save()

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekThemeParser",
            verbosity=0,
        )

        self.assertEqual(len(Theme.objects.all()), 1)
        theme = Theme.objects.first()
        self.assertEqual(theme.label_en, "Geology")
        self.assertEqual(theme.label_fr, "Géologie")
        self.assertEqual(theme.label_es, "Geología")
        self.assertEqual(theme.label_it, "Geologia")

    @mock.patch("requests.get")
    def test_another_theme_is_created_when_default_language_name_changes(
        self, mocked_get
    ):
        mocked_get.side_effect = self.mocked_get_func
        theme = Theme(
            label_en="With interesting rocks",
            label_fr="Géologie",
            label_it="Geologia",
            label_es="Geologia",
        )
        theme.save()

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaeTrekThemeParser",
            verbosity=0,
        )

        self.assertEqual(len(Theme.objects.all()), 2)


class MakeDescriptionTests(SimpleTestCase):
    def setUp(self):
        self.ouverture = {
            "periodeEnClair": {
                "libelleFr": "Ouvert toute l'année\n\nFermeture exceptionnelle en cas de pluie forte",
                "libelleEn": "Open all year long\n\nExceptionally closed during heavy rain",
            }
        }
        self.descriptifs = [
            {
                "theme": {
                    "id": 6527,
                    "libelleFr": "Topo/pas à pas",
                    "libelleEn": "Guidebook with maps/step-by-step",
                },
                "description": {
                    "libelleFr": "Départ : du parking de la Chapelle Saint Michel \r\n"
                    "1/ Suivre le chemin qui part à droite, traversant le vallon.\r\n"
                    "2/ Au carrefour tourner à droite et suivre la rivière\r\n"
                    "3/ Retour à la chapelle en passant à travers le petit bois.",
                    "libelleEn": "Start: from the parking near the Chapelle Saint Michel \r\n"
                    "1/ Follow the path starting at right-hand, cross the valley.\r\n"
                    "2/ At the crossroad turn left and follow the river.\r\n"
                    "3/ Back to the chapelle by the woods.",
                },
            }
        ]
        self.itineraire = {
            "itineraireBalise": "BALISE",
            "precisionsBalisage": {
                "libelleFr": "Suivre le balisage GR (blanc/rouge) ou GRP (jaune/rouge).",
                "libelleEn": "Follow the GR (white / red) or GRP (yellow / red) markings.",
            },
        }

    def test_it_returns_the_right_elements_in_description(self):
        description = ApidaeTrekParser._make_description(
            self.ouverture, self.descriptifs, self.itineraire
        )
        expected_fr_description = (
            "<p>Départ : du parking de la Chapelle Saint Michel </p>"
            "<p>1/ Suivre le chemin qui part à droite, traversant le vallon.</p>"
            "<p>2/ Au carrefour tourner à droite et suivre la rivière</p>"
            "<p>3/ Retour à la chapelle en passant à travers le petit bois.</p>"
            "<p>Ouvert toute l'année</p>"
            "<p>Fermeture exceptionnelle en cas de pluie forte</p>"
            "<p>Suivre le balisage GR (blanc/rouge) ou GRP (jaune/rouge).</p>"
        )
        self.assertEqual(description.to_dict()["fr"], expected_fr_description)
        expected_en_description = (
            "<p>Start: from the parking near the Chapelle Saint Michel </p>"
            "<p>1/ Follow the path starting at right-hand, cross the valley.</p>"
            "<p>2/ At the crossroad turn left and follow the river.</p>"
            "<p>3/ Back to the chapelle by the woods.</p>"
            "<p>Open all year long</p>"
            "<p>Exceptionally closed during heavy rain</p>"
            "<p>Follow the GR (white / red) or GRP (yellow / red) markings.</p>"
        )
        self.assertEqual(description.to_dict()["en"], expected_en_description)

    def test_it_places_temporary_closed_warning_first(self):
        temporary_closed = {
            "periodeEnClair": {
                "libelleFr": "Fermé temporairement.",
                "libelleEn": "Closed temporarily.",
            },
            "fermeTemporairement": "FERME_TEMPORAIREMENT",
        }
        description = ApidaeTrekParser._make_description(
            temporary_closed, self.descriptifs, self.itineraire
        )
        expected_fr_description = (
            "<p>Fermé temporairement.</p>"
            "<p>Départ : du parking de la Chapelle Saint Michel </p>"
            "<p>1/ Suivre le chemin qui part à droite, traversant le vallon.</p>"
            "<p>2/ Au carrefour tourner à droite et suivre la rivière</p>"
            "<p>3/ Retour à la chapelle en passant à travers le petit bois.</p>"
            "<p>Suivre le balisage GR (blanc/rouge) ou GRP (jaune/rouge).</p>"
        )
        self.assertEqual(description.to_dict()["fr"], expected_fr_description)
        expected_en_description = (
            "<p>Closed temporarily.</p>"
            "<p>Start: from the parking near the Chapelle Saint Michel </p>"
            "<p>1/ Follow the path starting at right-hand, cross the valley.</p>"
            "<p>2/ At the crossroad turn left and follow the river.</p>"
            "<p>3/ Back to the chapelle by the woods.</p>"
            "<p>Follow the GR (white / red) or GRP (yellow / red) markings.</p>"
        )
        self.assertEqual(description.to_dict()["en"], expected_en_description)


class MakeMarkingDescriptionTests(SimpleTestCase):
    def test_it_returns_default_text_when_not_marked(self):
        itineraire = {"itineraireBalise": None}
        description = ApidaeTrekParser._make_marking_description(itineraire)
        self.assertDictEqual(description, ApidaeTrekParser.trek_no_marking_description)

    def test_it_returns_given_text(self):
        precisions = {
            "libelleFr": "fr-marked itinerary",
            "libelleEn": "en-marked itinerary",
            "libelleEs": "es-marked itinerary",
            "libelleIt": "it-marked itinerary",
        }
        itineraire = {"itineraireBalise": "BALISE", "precisionsBalisage": precisions}
        description = ApidaeTrekParser._make_marking_description(itineraire)
        self.assertDictEqual(description, precisions)

    def test_it_returns_given_partial_text_mixed_with_default(self):
        partial_precisions = {
            "libelleEn": "en-marked itinerary",
            "libelleEs": "es-marked itinerary",
            "libelleIt": "it-marked itinerary",
        }
        itineraire = {
            "itineraireBalise": "BALISE",
            "precisionsBalisage": partial_precisions,
        }
        description = ApidaeTrekParser._make_marking_description(itineraire)
        expected = {
            "libelleFr": ApidaeTrekParser.default_trek_marking_description["libelleFr"],
            "libelleEn": "en-marked itinerary",
            "libelleEs": "es-marked itinerary",
            "libelleIt": "it-marked itinerary",
        }
        self.assertDictEqual(description, expected)

    def test_it_returns_default_text_when_no_details(self):
        itineraire = {
            "itineraireBalise": "BALISE",
        }
        description = ApidaeTrekParser._make_marking_description(itineraire)
        self.assertDictEqual(
            description, ApidaeTrekParser.default_trek_marking_description
        )


class GetPracticeNameFromActivities(SimpleTestCase):
    def test_it_considers_specific_activity_before_default_activity(self):
        practice_name = ApidaeTrekParser._get_practice_name_from_activities(
            [
                3113,  # Sports cyclistes
                3284,  # Itinéraire VTT
            ]
        )
        self.assertEqual(practice_name, "VTT")

    def test_it_takes_default_activity_if_no_specific_match(self):
        not_mapped_activity_id = 12341234
        practice_name = ApidaeTrekParser._get_practice_name_from_activities(
            [
                not_mapped_activity_id,
                3113,  # Sports cyclistes
            ]
        )
        self.assertEqual(practice_name, "Vélo")


class IsStillPublishableOn(SimpleTestCase):
    def test_it_returns_true(self):
        illustration = {"dateLimiteDePublication": "2020-06-28T00:00:00.000+0000"}
        a_date_before_that = date(year=2020, month=3, day=10)
        self.assertTrue(
            ApidaeTrekParser._is_still_publishable_on(illustration, a_date_before_that)
        )

    def test_it_returns_false(self):
        illustration = {"dateLimiteDePublication": "2020-06-28T00:00:00.000+0000"}
        a_date_after_that = date(year=2020, month=8, day=10)
        self.assertFalse(
            ApidaeTrekParser._is_still_publishable_on(illustration, a_date_after_that)
        )

    def test_it_considers_date_limite_is_not_included(self):
        illustration = {"dateLimiteDePublication": "2020-06-28T00:00:00.000+0000"}
        that_same_date = date(year=2020, month=6, day=28)
        self.assertFalse(
            ApidaeTrekParser._is_still_publishable_on(illustration, that_same_date)
        )


class MakeDurationTests(SimpleTestCase):
    def test_it_returns_correct_duration_from_duration_in_minutes(self):
        self.assertAlmostEqual(
            ApidaeTrekParser._make_duration(duration_in_minutes=90), 1.5
        )

    def test_it_returns_correct_duration_from_duration_in_days(self):
        self.assertAlmostEqual(
            ApidaeTrekParser._make_duration(duration_in_days=3), 72.0
        )

    def test_giving_both_duration_arguments_only_duration_in_days_is_considered(self):
        self.assertAlmostEqual(
            ApidaeTrekParser._make_duration(duration_in_minutes=90, duration_in_days=2),
            48.0,
        )

    def test_it_rounds_output_to_two_decimal_places(self):
        self.assertEqual(ApidaeTrekParser._make_duration(duration_in_minutes=20), 0.33)

    def test_it_returns_none_when_no_duration_is_provided(self):
        self.assertEqual(
            ApidaeTrekParser._make_duration(
                duration_in_minutes=None, duration_in_days=None
            ),
            None,
        )


class TestApidaePOIParser(ApidaePOIParser):
    url = "https://example.net/fake/api/"
    api_key = "ABCDEF"
    project_id = 1234
    selection_id = 654321


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class ApidaePOIParserTests(TestCase):
    @staticmethod
    def make_dummy_get(apidae_data_file):
        return make_dummy_apidae_get(
            parser_class=TestApidaePOIParser,
            test_data_dir="geotrek/trekking/tests/data/apidae_poi_parser",
            data_filename=apidae_data_file,
        )

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    def test_POI_is_imported(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get("a_poi.json")

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaePOIParser",
            verbosity=0,
        )

        self.assertEqual(POI.objects.count(), 1)
        poi = POI.objects.all().first()
        self.assertEqual(poi.name_fr, "Un point d'intérêt")
        self.assertEqual(poi.name_en, "A point of interest")
        self.assertEqual(poi.description_fr, "La description courte en français.")
        self.assertEqual(poi.description_en, "The short description in english.")

        self.assertEqual(poi.geom.srid, settings.SRID)
        self.assertAlmostEqual(poi.geom.coords[0], 729136.5, delta=0.1)
        self.assertAlmostEqual(poi.geom.coords[1], 6477050.1, delta=0.1)

        self.assertEqual(Attachment.objects.count(), 1)
        photo = Attachment.objects.first()
        self.assertEqual(photo.author, "The author of the picture")
        self.assertEqual(photo.legend, "The legend of the picture")
        self.assertEqual(photo.attachment_file.size, len(testdata.IMG_FILE))
        self.assertEqual(photo.title, "The title of the picture")

        self.assertEqual(poi.type.label_en, "Patrimoine culturel")
        self.assertEqual(poi.type.label_fr, None)

    @mock.patch("requests.get")
    def test_trek_illustration_is_not_imported_on_missing_file_metadata(
        self, mocked_get
    ):
        mocked_get.side_effect = self.make_dummy_get(
            "poi_with_not_complete_illustration.json"
        )
        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestApidaePOIParser",
            verbosity=0,
        )
        self.assertEqual(Attachment.objects.count(), 0)


class PrepareAttachmentFromIllustrationTests(TestCase):
    def setUp(self):
        self.illustration = {
            "nom": {"libelleEn": "The title of the picture"},
            "legende": {"libelleEn": "The legend of the picture"},
            "copyright": {"libelleEn": "The author of the picture"},
            "traductionFichiers": [{"url": "https://example.net/a_picture.jpg"}],
        }

    def test_given_full_illustration_it_returns_attachment_info(self):
        expected_result = (
            "https://example.net/a_picture.jpg",
            "The legend of the picture",
            "The author of the picture",
            "The title of the picture",
        )
        self.assertEqual(
            _prepare_attachment_from_apidae_illustration(
                self.illustration, "libelleEn"
            ),
            expected_result,
        )

    def test_it_returns_empty_strings_for_missing_info(self):
        del self.illustration["legende"]
        del self.illustration["copyright"]
        del self.illustration["nom"]
        expected_result = ("https://example.net/a_picture.jpg", "", "", "")
        self.assertEqual(
            _prepare_attachment_from_apidae_illustration(
                self.illustration, "libelleEn"
            ),
            expected_result,
        )

    def test_it_substitutes_name_to_missing_legend(self):
        del self.illustration["legende"]
        self.illustration["nom"] = {
            "libelleEn": "The title of the picture which will also be the legend"
        }
        expected_result = (
            "https://example.net/a_picture.jpg",
            "The title of the picture which will also be the legend",
            "The author of the picture",
            "The title of the picture which will also be the legend",
        )
        self.assertEqual(
            _prepare_attachment_from_apidae_illustration(
                self.illustration, "libelleEn"
            ),
            expected_result,
        )

    def test_it_returns_empty_strings_if_translation_not_found(self):
        self.illustration["legende"] = {}
        self.illustration["copyright"] = {}
        self.illustration["nom"] = {}
        expected_result = ("https://example.net/a_picture.jpg", "", "", "")
        self.assertEqual(
            _prepare_attachment_from_apidae_illustration(
                self.illustration, "libelleEn"
            ),
            expected_result,
        )


class SchemaRandonneeParserWithURL(SchemaRandonneeParser):
    url = "https://test.com"


class SchemaRandonneeParserWithLicenseCreation(SchemaRandonneeParser):
    field_options = {"attachments": {"create_license": True}}


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, "Test without dynamic segmentation only")
class SchemaRandonneeParserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        FileType.objects.create(type="Photographie")
        Practice.objects.create(name="Pédestre")
        RecordSource.objects.create(name="Producer 1")
        License.objects.create(label="License 1")
        License.objects.create(label="License 2")

    def call_import_command_with_file(self, filename, **kwargs):
        filename = os.path.join(
            os.path.dirname(__file__), "data", "schema_randonnee_parser", filename
        )
        call_command(
            "import",
            "geotrek.trekking.parsers.SchemaRandonneeParser",
            filename,
            stdout=kwargs.get("output"),
        )

    def mocked_url(self, url=None, verb=None):
        if url and "jpg" in url:
            return Mock(
                status_code=200,
                content=b"mocked content jpg",
                headers={"content-length": 18},
            )
        elif url and "png" in url:
            return Mock(
                status_code=200,
                content=b"mocked content png",
                headers={"content-length": 18},
            )
        elif url and "none" in url:
            return Mock(status_code=200, content=None, headers={"content-length": 0})
        elif url and "404" in url:
            msg = "mock error message"
            raise DownloadImportError(msg)
        response = {
            "type": "FeatureCollection",
            "name": "sql_statement",
            "crs": {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"},
            },
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "id_local": "1",
                        "producteur": "Producer 1",
                        "nom_itineraire": "Trek 1",
                        "pratique": "pédestre",
                        "depart": "Departure 1",
                        "arrivee": "Arrival 1",
                        "instructions": "Instructions 1",
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [6.449592517966364, 44.733424655086957],
                            [6.449539623508488, 44.733394939411369],
                        ],
                    },
                }
            ],
        }
        return Mock(json=lambda: response)

    @mock.patch("geotrek.common.parsers.Parser.request_or_retry")
    def test_parse_from_url(self, mocked_request_or_retry):
        mocked_request_or_retry.return_value = self.mocked_url()
        call_command(
            "import", "geotrek.trekking.tests.test_parsers.SchemaRandonneeParserWithURL"
        )
        self.assertEqual(Trek.objects.count(), 1)

    def test_create_basic_trek(self):
        self.call_import_command_with_file("correct_trek.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.eid, "be5851a9-87d4-467c-ba95-16d474480976")
        self.assertEqual(trek.geom.srid, settings.SRID)
        self.assertEqual(trek.geom.geom_type, "LineString")
        self.assertEqual(trek.geom.num_coords, 2)
        self.assertEqual(trek.parking_location.srid, settings.SRID)
        self.assertEqual(trek.parking_location.geom_type, "Point")
        self.assertEqual(
            trek.description,
            "Instructions 1\n\n<a href=https://test.com>https://test.com</a>",
        )

    @mock.patch("geotrek.common.parsers.Parser.request_or_retry")
    def test_parse_attachments(self, mocked_request_or_retry):
        mocked_request_or_retry.side_effect = self.mocked_url
        output = StringIO()
        self.call_import_command_with_file("with_medias.geojson", output=output)
        self.assertEqual(Trek.objects.count(), 1)
        output_value = output.getvalue()
        trek = Trek.objects.get()
        self.assertEqual(trek.attachments.count(), 1)
        attachment = trek.attachments.get()
        self.assertEqual(attachment.title, "Title 5")
        self.assertEqual(attachment.author, "Author 1")
        self.assertEqual(attachment.license.label, "License 1")
        self.assertIn("Failed to load attachment: mock error message", output_value)

    def test_medias_is_null(self):
        self.call_import_command_with_file("with_null_medias.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.attachments.count(), 0)

    @mock.patch("geotrek.common.parsers.Parser.request_or_retry")
    def test_update_of_attachments_info(self, mocked_request_or_retry):
        mocked_request_or_retry.side_effect = self.mocked_url
        self.call_import_command_with_file("mod_medias_info_before_update.geojson")
        self.call_import_command_with_file("mod_medias_info_after_update.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.attachments.count(), 2)
        attachment_1 = trek.attachments.get(title="Title 1.2")
        self.assertIsNotNone(attachment_1)
        self.assertEqual(attachment_1.author, "Author 1.2")
        self.assertEqual(attachment_1.license.label, "License 2")
        attachment_2 = trek.attachments.get(title="Title 2.2")
        self.assertIsNotNone(attachment_2)
        self.assertEqual(attachment_2.author, "Author 2.2")
        self.assertEqual(attachment_2.license.label, "License 2")

    @mock.patch("geotrek.common.parsers.Parser.request_or_retry")
    def test_add_attachment_info(self, mocked_request_or_retry):
        mocked_request_or_retry.side_effect = self.mocked_url
        self.call_import_command_with_file("add_medias_info_before_update.geojson")
        self.call_import_command_with_file("add_medias_info_after_update.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.attachments.count(), 3)
        attachment_1 = trek.attachments.get(title="Title 1.2")
        self.assertIsNotNone(attachment_1)
        self.assertEqual(attachment_1.author, "Author 1.2")
        self.assertEqual(attachment_1.license.label, "License 2")
        attachment_2 = trek.attachments.get(title="Title 2.2")
        self.assertIsNotNone(attachment_2)
        self.assertEqual(attachment_2.author, "Author 2.2")
        self.assertEqual(attachment_2.license.label, "License 2")
        attachment_3 = trek.attachments.get(title="Title 3.2")
        self.assertIsNotNone(attachment_3)
        self.assertEqual(attachment_3.author, "Author 3.2")
        self.assertEqual(attachment_3.license.label, "License 2")

    @mock.patch("geotrek.common.parsers.Parser.request_or_retry")
    def test_mod_attachment_url(self, mocked_request_or_retry):
        mocked_request_or_retry.side_effect = self.mocked_url
        self.call_import_command_with_file("mod_medias_url_before_update.geojson")
        self.call_import_command_with_file("mod_medias_url_after_update.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.attachments.count(), 1)
        attachment = trek.attachments.get()
        with attachment.attachment_file.file.open() as f:
            self.assertEqual(f.read(), b"mocked content png")
        self.assertEqual(attachment.title, "Title 1")
        self.assertEqual(attachment.author, "Author 1")
        self.assertEqual(attachment.license.label, "License 1")

    @mock.patch("geotrek.common.parsers.Parser.request_or_retry")
    def test_del_attachment_info(self, mocked_request_or_retry):
        mocked_request_or_retry.side_effect = self.mocked_url
        self.call_import_command_with_file("del_medias_info_before_update.geojson")
        self.call_import_command_with_file("del_medias_info_after_update.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.attachments.count(), 2)
        attachments = trek.attachments.all()
        self.assertEqual(attachments[0].title, "")
        self.assertEqual(attachments[1].title, "")
        self.assertEqual(attachments[0].author, "")
        self.assertEqual(attachments[1].author, "")
        self.assertIsNone(attachments[0].license)
        self.assertIsNone(attachments[1].license)

    @mock.patch("geotrek.common.parsers.Parser.request_or_retry")
    def test_license_does_not_exist(self, mocked_request_or_retry):
        mocked_request_or_retry.side_effect = self.mocked_url
        output = StringIO()
        self.call_import_command_with_file("license_not_created.geojson", output=output)
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.attachments.count(), 1)
        output_value = output.getvalue()
        self.assertIn(
            "License 'New license' does not exist in Geotrek-Admin. Please add it",
            output_value,
        )

    @mock.patch("geotrek.common.parsers.Parser.request_or_retry")
    def test_license_has_been_created(self, mocked_request_or_retry):
        mocked_request_or_retry.side_effect = self.mocked_url
        output = StringIO()
        parser_name = "geotrek.trekking.tests.test_parsers.SchemaRandonneeParserWithLicenseCreation"
        filename = os.path.join(
            os.path.dirname(__file__),
            "data",
            "schema_randonnee_parser",
            "license_not_created.geojson",
        )
        call_command("import", parser_name, filename, stdout=output)
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.attachments.count(), 1)
        attachment = trek.attachments.get()
        self.assertEqual(attachment.license.label, "New license")
        output_value = output.getvalue()
        self.assertIn(
            "License 'New license' did not exist in Geotrek-Admin and was automatically created",
            output_value,
        )

    def test_create_related_treks(self):
        self.call_import_command_with_file("related_treks.geojson")
        self.assertEqual(Trek.objects.count(), 3)
        self.assertEqual(OrderedTrekChild.objects.count(), 2)
        parent_trek = Trek.objects.get(name="Trek 1")
        child_trek_1 = Trek.objects.get(name="Trek 2")
        child_trek_2 = Trek.objects.get(name="Trek 3")
        self.assertTrue(
            OrderedTrekChild.objects.filter(
                parent=parent_trek.pk, child=child_trek_1.pk
            ).exists()
        )
        self.assertTrue(
            OrderedTrekChild.objects.filter(
                parent=parent_trek.pk, child=child_trek_2.pk
            ).exists()
        )

    def test_related_treks_parent_does_not_exist(self):
        self.call_import_command_with_file(
            "related_treks_parent_does_not_exist.geojson"
        )
        self.assertEqual(Trek.objects.count(), 1)
        self.assertEqual(OrderedTrekChild.objects.count(), 0)

    def test_trek_without_uuid(self):
        self.call_import_command_with_file("no_uuid.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.eid, "1")

    def test_no_geom(self):
        output = StringIO()
        self.call_import_command_with_file("no_geom.geojson", output=output)
        self.assertEqual(Trek.objects.count(), 0)
        output_value = output.getvalue()
        self.assertIn("Trek geometry is None", output_value)

    def test_incorrect_geoms(self):
        output = StringIO()
        self.call_import_command_with_file("incorrect_geoms.geojson", output=output)
        self.assertEqual(Trek.objects.count(), 0)
        output_value = output.getvalue()
        self.assertIn(
            "Invalid geometry type for field 'geometry'. Should be LineString, not MultiLineString",
            output_value,
        )
        self.assertIn(
            "Invalid geometry type for field 'geometry'. Should be LineString, not None",
            output_value,
        )
        self.assertIn(
            "Invalid geometry for field 'geometry'. Should contain coordinates",
            output_value,
        )

    def test_no_parking_location(self):
        self.call_import_command_with_file("no_parking_location.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertIsNone(trek.parking_location)

    def test_incorrect_parking_location(self):
        output = StringIO()
        self.call_import_command_with_file(
            "incorrect_parking_location.geojson", output=output
        )
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertIsNone(trek.parking_location)
        self.assertIn(
            "Bad value for parking geometry: should be a Point", output.getvalue()
        )

    def test_description_and_url(self):
        self.call_import_command_with_file("description_and_url.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(
            trek.description,
            "Instructions 1\n\n<a href=https://test.com>https://test.com</a>",
        )

    def test_description_no_url(self):
        self.call_import_command_with_file("description_no_url.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.description, "Instructions 1")

    def test_url_no_description(self):
        self.call_import_command_with_file("url_no_description.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(
            trek.description, "<a href=https://test.com>https://test.com</a>"
        )

    def test_no_description_no_url(self):
        self.call_import_command_with_file("no_description_no_url.geojson")
        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.get()
        self.assertEqual(trek.description, "")

    def test_update_url(self):
        self.call_import_command_with_file("update_url_before.geojson")
        self.call_import_command_with_file("update_url_after.geojson")
        trek1 = Trek.objects.get(eid="1")
        self.assertEqual(
            trek1.description, "<a href=https://test.com>https://test.com</a>"
        )
        trek2 = Trek.objects.get(eid="2")
        self.assertEqual(
            trek2.description,
            "Instructions 2\n\n<a href=https://test2.com>https://test2.com</a>",
        )


class TestPOIOpenStreetMapParser(OpenStreetMapPOIParser):
    provider = "OpenStreetMap"
    tags = [
        {"natural": "peak"},
        {"natural": "arete"},
        {"natural": "saddle"},
        {"natural": "wood"},
        {"tourism": "alpine_hut"},
        {"mountain_pass": "yes"},
    ]
    default_fields_values = {"name": "Test"}
    type = "Test"


class OpenStreetMapPOIParser(TestCase):
    @classmethod
    @mock.patch("geotrek.common.parsers.requests.get")
    def import_POI(cls, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "osm_poi_parser", "POI_OSM.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json

        call_command(
            "import",
            "geotrek.trekking.tests.test_parsers.TestPOIOpenStreetMapParser",
        )

    @classmethod
    def setUpTestData(cls):
        cls.type = POIType.objects.create(label="Test")
        cls.path = PathFactory.create(
            geom=LineString((5.8394587, 44.6918860), (5.9527022, 44.7752786), srid=4326)
        )
        cls.import_POI()
        cls.objects = POI.objects.all()

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_import_cmd_raises_error_when_no_path(self):
        self.path.delete()
        with self.assertRaisesRegex(
            CommandError, "You need to add a network of paths before importing POIs"
        ):
            call_command(
                "import",
                "geotrek.trekking.tests.test_parsers.TestPOIOpenStreetMapParser",
                verbosity=0,
            )

    def test_create_POI_OSM(self):
        self.assertEqual(self.objects.count(), 4)

    def test_POI_eid_filter_OSM(self):
        poi_eid = self.objects.all().values_list("eid", flat=True)
        self.assertListEqual(list(poi_eid), ["N1", "W2", "W3", "R4"])
        self.assertNotEqual(poi_eid, ["1", "2", "3", "4"])

    def test_default_name(self):
        poi1 = self.objects.get(eid="N1")
        self.assertEqual(poi1.name, "Grande Tête de l'Obiou")

        poi3 = self.objects.get(eid="W3")
        self.assertEqual(poi3.name, "Test")

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_topology_point(self):
        poi = self.objects.get(eid="N1")
        self.assertAlmostEqual(poi.topo_object.offset, 6437.493262796821)
        self.assertEqual(poi.topo_object.paths.count(), 1)
        poi_path = poi.topo_object.paths.get()
        self.assertEqual(poi_path, self.path)
        self.assertEqual(poi.topo_object.kind, "POI")

    def test_topology_point_no_dynamic_segmentation(self):
        poi = self.objects.get(eid="N1")
        self.assertAlmostEqual(poi.geom.x, 924596.692586552)
        self.assertAlmostEqual(poi.geom.y, 6412498.122749874)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_topology_way(self):
        poi = self.objects.get(eid="W2")
        self.assertAlmostEqual(poi.topo_object.offset, -1401.0373646193946)
        poi_path = poi.topo_object.paths.get()
        self.assertEqual(poi_path, self.path)
        self.assertEqual(poi.topo_object.kind, "POI")

    def test_topology_way_no_dynamic_segmentation(self):
        poi = self.objects.get(eid="W2")
        self.assertAlmostEqual(poi.geom.x, 926882.1207550302)
        self.assertAlmostEqual(poi.geom.y, 6403317.111114113)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_topology_polygon(self):
        poi = self.objects.get(eid="W3")
        self.assertAlmostEqual(poi.topo_object.offset, -1398.870241563602)
        poi_path = poi.topo_object.paths.get()
        self.assertEqual(poi_path, self.path)
        self.assertEqual(poi.topo_object.kind, "POI")

    def test_topology_polygon_no_dynamic_segmentation(self):
        poi = self.objects.get(eid="W3")
        self.assertAlmostEqual(poi.geom.x, 933501.2402840604)
        self.assertAlmostEqual(poi.geom.y, 6410680.482150642)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_topology_relation(self):
        poi = self.objects.get(eid="R4")
        self.assertAlmostEqual(poi.topo_object.offset, 2589.2357898722626)
        poi_path = poi.topo_object.paths.get()
        self.assertEqual(poi_path, self.path)
        self.assertEqual(poi.topo_object.kind, "POI")

    def test_topology_relation_no_dynamic_segmentation(self):
        poi = self.objects.get(eid="R4")
        self.assertAlmostEqual(poi.geom.x, 930902.9339307954)
        self.assertAlmostEqual(poi.geom.y, 6406011.138417606)

    def test_multiple_import(self):
        poi1 = self.objects.get(eid="N1")
        poi2 = self.objects.get(eid="W2")

        id1 = poi1.id
        id2 = poi2.id

        self.import_POI()

        poi1_bis = self.objects.get(eid="N1")
        poi2_bis = self.objects.get(eid="W2")

        self.assertEqual(poi1_bis.id, id1)
        self.assertEqual(poi2_bis.id, id2)
        self.assertEqual(self.objects.count(), 4)
