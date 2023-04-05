from datetime import date
import json
import os
from copy import copy
from io import StringIO
from unittest import mock
from unittest import skipIf
from unittest.mock import Mock
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.gis.geos import Point, LineString, MultiLineString, WKTWriter
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, SimpleTestCase
from django.test.utils import override_settings

from geotrek.common.utils import testdata
from geotrek.common.models import Theme, FileType, Attachment, Label
from geotrek.common.tests.mixins import GeotrekParserTestMixin
from geotrek.core.tests.factories import PathFactory
from geotrek.trekking.tests.factories import RouteFactory
from geotrek.trekking.models import POI, POIType, Service, Trek, DifficultyLevel, Route
from geotrek.trekking.parsers import (
    TrekParser, GeotrekPOIParser, GeotrekServiceParser, GeotrekTrekParser, ApidaeTrekParser, ApidaeTrekThemeParser,
    ApidaePOIParser, _prepare_attachment_from_apidae_illustration, RowImportError
)


class TrekParserFilterDurationTests(TestCase):
    def setUp(self):
        self.parser = TrekParser()

    def test_standard(self):
        self.assertEqual(self.parser.filter_duration('duration', '0 h 30'), 0.5)
        self.assertFalse(self.parser.warnings)

    def test_upper_h(self):
        self.assertEqual(self.parser.filter_duration('duration', '1 H 06'), 1.1)
        self.assertFalse(self.parser.warnings)

    def test_spaceless(self):
        self.assertEqual(self.parser.filter_duration('duration', '2h45'), 2.75)
        self.assertFalse(self.parser.warnings)

    def test_no_minutes(self):
        self.assertEqual(self.parser.filter_duration('duration', '3 h'), 3.)
        self.assertFalse(self.parser.warnings)

    def test_no_hours(self):
        self.assertEqual(self.parser.filter_duration('duration', 'h 12'), None)
        self.assertTrue(self.parser.warnings)

    def test_spacefull(self):
        self.assertEqual(self.parser.filter_duration('duration', '\n \t  4     h\t9\r\n'), 4.15)
        self.assertFalse(self.parser.warnings)

    def test_float(self):
        self.assertEqual(self.parser.filter_duration('duration', '5.678'), 5.678)
        self.assertFalse(self.parser.warnings)

    def test_coma(self):
        self.assertEqual(self.parser.filter_duration('duration', '6,7'), 6.7)
        self.assertFalse(self.parser.warnings)

    def test_integer(self):
        self.assertEqual(self.parser.filter_duration('duration', '7'), 7.)
        self.assertFalse(self.parser.warnings)

    def test_negative_number(self):
        self.assertEqual(self.parser.filter_duration('duration', '-8'), None)
        self.assertTrue(self.parser.warnings)

    def test_negative_hours(self):
        self.assertEqual(self.parser.filter_duration('duration', '-8 h 00'), None)
        self.assertTrue(self.parser.warnings)

    def test_negative_minutes(self):
        self.assertEqual(self.parser.filter_duration('duration', '8 h -15'), None)
        self.assertTrue(self.parser.warnings)

    def test_min_gte_60(self):
        self.assertEqual(self.parser.filter_duration('duration', '9 h 60'), None)
        self.assertTrue(self.parser.warnings)


class TrekParserFilterGeomTests(TestCase):
    def setUp(self):
        self.parser = TrekParser()

    def test_empty_geom(self):
        self.assertEqual(self.parser.filter_geom('geom', None), None)
        self.assertFalse(self.parser.warnings)

    def test_point(self):
        geom = Point(0, 0)
        with self.assertRaisesRegex(RowImportError,
                                    "Invalid geometry type for field 'geom'. Should be LineString, not Point"):
            self.parser.filter_geom('geom', geom)

    def test_linestring(self):
        geom = LineString((0, 0), (0, 1), (1, 1), (1, 0))
        self.assertEqual(self.parser.filter_geom('geom', geom), geom)
        self.assertFalse(self.parser.warnings)

    def test_multilinestring(self):
        geom = MultiLineString(LineString((0, 0), (0, 1), (1, 1), (1, 0)))
        self.assertEqual(self.parser.filter_geom('geom', geom),
                         LineString((0, 0), (0, 1), (1, 1), (1, 0)))
        self.assertFalse(self.parser.warnings)

    def test_multilinestring_with_hole(self):
        geom = MultiLineString(LineString((0, 0), (0, 1)), LineString((100, 100), (100, 101)))
        self.assertEqual(self.parser.filter_geom('geom', geom),
                         LineString((0, 0), (0, 1), (100, 100), (100, 101)))

        self.assertTrue(self.parser.warnings)


WKT = (
    b'LINESTRING (356392.8993 6689612.1026, 356466.0588 6689740.1317, 356411.1892 6689868.1609, '
    b'356566.6531 6689904.7406, 356712.9721 6689804.1463, 356703.8271 6689703.5520, 356621.5227 6689639.5374, '
    b'356612.3778 6689511.5083, 356447.7689 6689502.3634)'
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
        filename = os.path.join(os.path.dirname(__file__), 'data', 'trek.shp')
        call_command('import', 'geotrek.trekking.parsers.TrekParser', filename, verbosity=0)
        trek = Trek.objects.all().last()
        self.assertEqual(trek.name, "Balade")
        self.assertEqual(trek.difficulty, self.difficulty)
        self.assertEqual(trek.route, self.route)
        self.assertQuerysetEqual(trek.themes.all(), [repr(t) for t in self.themes], ordered=False)
        self.assertEqual(WKTWriter(precision=4).write(trek.geom), WKT)


WKT_POI = (
    b'POINT (1.5238 43.5294)'
)


class POIParserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.poi_type_e = POIType.objects.create(label="équipement")
        cls.poi_type_s = POIType.objects.create(label="signaletique")
        cls.filetype = FileType.objects.create(type="Photographie")

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_import_cmd_raises_error_when_no_path(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'poi.shp')
        with self.assertRaisesRegex(CommandError, 'You need to add a network of paths before importing POIs'):
            call_command('import', 'geotrek.trekking.parsers.POIParser', filename, verbosity=0)

    def test_import_cmd_raises_wrong_geom_type(self):
        PathFactory.create(geom=LineString((0, 0), (0, 10), srid=4326))
        filename = os.path.join(os.path.dirname(__file__), 'data', 'trek.shp')
        output = StringIO()
        call_command('import', 'geotrek.trekking.parsers.POIParser', filename, verbosity=2, stdout=output)
        self.assertEqual(POI.objects.count(), 0)
        self.assertIn("Invalid geometry type for field 'GEOM'. Should be Point, not LineString,", output.getvalue())

    def test_import_cmd_raises_no_geom(self):
        PathFactory.create(geom=LineString((0, 0), (0, 10), srid=4326))
        filename = os.path.join(os.path.dirname(__file__), 'data', 'empty_geom.geojson')
        output = StringIO()
        call_command('import', 'geotrek.trekking.parsers.POIParser', filename, verbosity=2, stdout=output)
        self.assertEqual(POI.objects.count(), 0)
        self.assertIn("Invalid geometry", output.getvalue())

    def test_create(self):
        PathFactory.create(geom=LineString((0, 0), (0, 10), srid=4326))
        filename = os.path.join(os.path.dirname(__file__), 'data', 'poi.shp')
        call_command('import', 'geotrek.trekking.parsers.POIParser', filename, verbosity=0)
        poi = POI.objects.all().last()
        self.assertEqual(poi.name, "pont")
        poi.reload()
        self.assertEqual(WKTWriter(precision=4).write(poi.geom), WKT_POI)
        self.assertEqual(poi.geom, poi.geom_3d)


class TestGeotrekTrekParser(GeotrekTrekParser):
    url = "https://test.fr"
    provider = 'geotrek1'
    field_options = {
        'difficulty': {'create': True, },
        'route': {'create': True, },
        'themes': {'create': True},
        'practice': {'create': True},
        'accessibilities': {'create': True},
        'networks': {'create': True},
        'geom': {'required': True},
        'labels': {'create': True},
        'source': {'create': True}
    }


class TestGeotrek2TrekParser(GeotrekTrekParser):
    url = "https://test.fr"

    field_options = {
        'geom': {'required': True},
    }
    provider = 'geotrek2'


class TestGeotrekPOIParser(GeotrekPOIParser):
    url = "https://test.fr"

    field_options = {
        'type': {'create': True, },
        'geom': {'required': True},
    }


class TestGeotrekServiceParser(GeotrekServiceParser):
    url = "https://test.fr"

    field_options = {
        'type': {'create': True, },
        'geom': {'required': True},
    }


@override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr")
@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
class TrekGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = 'trekking'

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['trek_difficulty.json', 'trek_route.json', 'trek_theme.json', 'trek_practice.json',
                                'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json', 'trek_ids.json',
                                'trek.json', 'trek_children.json', ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=0)
        self.assertEqual(Trek.objects.count(), 5)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name_it, "Foo bar")
        self.assertEqual(str(trek.difficulty), 'Très facile')
        self.assertEqual(str(trek.practice), 'Cheval')
        self.assertAlmostEqual(trek.geom[0][0], 569946.9850365581, places=5)
        self.assertAlmostEqual(trek.geom[0][1], 6190964.893167565, places=5)
        self.assertEqual(trek.children.first().name, "Foo")
        self.assertEqual(trek.labels.count(), 3)
        self.assertEqual(trek.source.first().name, "Une source numero 2")
        self.assertEqual(trek.labels.first().name, "Chien autorisé")
        self.assertEqual(Attachment.objects.filter(object_id=trek.pk).count(), 3)
        self.assertEqual(Attachment.objects.get(object_id=trek.pk, license__isnull=False).license.label, "License")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_create_multiple_page(self, mocked_head, mocked_get):
        class MockResponse:
            mock_json_order = ['trek_difficulty.json', 'trek_route.json', 'trek_theme.json', 'trek_practice.json',
                               'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json', 'trek_ids.json',
                               'trek.json', 'trek_children.json', 'trek_children.json']
            mock_time = 0
            total_mock_response = 1

            def __init__(self, status_code):
                self.status_code = status_code

            def json(self):
                filename = os.path.join(os.path.dirname(__file__), 'data', 'geotrek_parser_v2',
                                        self.mock_json_order[self.mock_time])
                with open(filename, 'r') as f:
                    data_json = json.load(f)
                    if self.mock_json_order[self.mock_time] == 'trek.json':
                        data_json['count'] = 10
                        if self.total_mock_response == 1:
                            self.total_mock_response += 1
                            data_json['next'] = "foo"
                    self.mock_time += 1
                    return data_json

            @property
            def content(self):
                return b''

        # Mock GET
        mocked_get.return_value = MockResponse(200)
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=0)
        self.assertEqual(Trek.objects.count(), 5)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name_it, "Foo bar")
        self.assertEqual(str(trek.difficulty), 'Très facile')
        self.assertEqual(str(trek.practice), 'Cheval')
        self.assertAlmostEqual(trek.geom[0][0], 569946.9850365581, places=5)
        self.assertAlmostEqual(trek.geom[0][1], 6190964.893167565, places=5)
        self.assertEqual(trek.children.first().name, "Foo")
        self.assertEqual(trek.labels.count(), 3)
        self.assertEqual(trek.labels.first().name, "Chien autorisé")
        self.assertEqual(Attachment.objects.filter(object_id=trek.pk).count(), 3)
        self.assertEqual(Attachment.objects.get(object_id=trek.pk, license__isnull=False).license.label, "License")

    @override_settings(PAPERCLIP_MAX_BYTES_SIZE_IMAGE=1)
    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_create_attachment_max_size(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['trek_difficulty.json', 'trek_route.json', 'trek_theme.json', 'trek_practice.json',
                                'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json', 'trek_ids.json',
                                'trek.json', 'trek_children.json', ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b'11'
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=0)
        self.assertEqual(Trek.objects.count(), 5)
        self.assertEqual(Attachment.objects.count(), 0)

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_update_attachment(self, mocked_head, mocked_get):

        class MockResponse:
            mock_json_order = ['trek_difficulty.json', 'trek_route.json', 'trek_theme.json', 'trek_practice.json',
                               'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json', 'trek_ids.json',
                               'trek.json', 'trek_children.json', ]
            mock_time = 0
            a = 0

            def __init__(self, status_code):
                self.status_code = status_code

            def json(self):
                if len(self.mock_json_order) <= self.mock_time:
                    self.mock_time = 0
                filename = os.path.join(os.path.dirname(__file__), 'data', 'geotrek_parser_v2',
                                        self.mock_json_order[self.mock_time])

                self.mock_time += 1
                with open(filename, 'r') as f:
                    return json.load(f)

            @property
            def content(self):
                # We change content of attachment every time
                self.a += 1
                return bytes(f'{self.a}', 'utf-8')

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value = MockResponse(200)
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=0)
        self.assertEqual(Trek.objects.count(), 5)
        trek = Trek.objects.all().first()
        self.assertEqual(Attachment.objects.filter(object_id=trek.pk).count(), 3)
        self.assertEqual(Attachment.objects.first().attachment_file.read(), b'11')
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=0)
        self.assertEqual(Trek.objects.count(), 5)
        trek.refresh_from_db()
        self.assertEqual(Attachment.objects.filter(object_id=trek.pk).count(), 3)
        self.assertEqual(Attachment.objects.first().attachment_file.read(), b'13')

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr")
    def test_create_multiple_fr(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['trek_difficulty.json', 'trek_route.json', 'trek_theme.json', 'trek_practice.json',
                                'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json', 'trek_ids.json', 'trek.json',
                                'trek_children.json', 'trek_difficulty.json', 'trek_route.json', 'trek_theme.json',
                                'trek_practice.json', 'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json',
                                'trek_ids_2.json', 'trek_2.json', 'trek_children.json', 'trek_difficulty.json', 'trek_route.json', 'trek_theme.json',
                                'trek_practice.json', 'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json',
                                'trek_ids_2.json', 'trek_2_after.json', 'trek_children.json', ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=0)
        self.assertEqual(Trek.objects.count(), 5)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name_en, "Loop of the pic of 3 lords")
        self.assertEqual(trek.name_fr, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(str(trek.difficulty), 'Très facile')
        self.assertEqual(str(trek.practice), 'Cheval')
        self.assertAlmostEqual(trek.geom[0][0], 569946.9850365581, places=5)
        self.assertAlmostEqual(trek.geom[0][1], 6190964.893167565, places=5)
        self.assertEqual(trek.children.first().name, "Foo")
        self.assertEqual(trek.labels.count(), 3)
        self.assertEqual(trek.labels.first().name, "Chien autorisé")
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrek2TrekParser', verbosity=0)
        self.assertEqual(Trek.objects.count(), 6)
        trek = Trek.objects.get(name_fr="Étangs du Picot")
        self.assertEqual(trek.description_teaser_fr, "Chapeau")
        self.assertEqual(trek.description_teaser_it, "Cappello")
        self.assertEqual(trek.description_teaser_es, "Sombrero")
        self.assertEqual(trek.description_teaser_en, "Cap")
        self.assertEqual(trek.description_teaser, "Chapeau")
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrek2TrekParser', verbosity=0)
        trek.refresh_from_db()
        self.assertEqual(Trek.objects.count(), 6)
        self.assertEqual(trek.description_teaser_fr, "Chapeau 2")
        self.assertEqual(trek.description_teaser_it, "Cappello 2")
        self.assertEqual(trek.description_teaser_es, "Sombrero 2")
        self.assertEqual(trek.description_teaser_en, "Cap 2")
        self.assertEqual(trek.description_teaser, "Chapeau 2")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="en")
    def test_create_multiple_en(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['trek_difficulty.json', 'trek_route.json', 'trek_theme.json', 'trek_practice.json',
                                'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json', 'trek_ids.json', 'trek.json',
                                'trek_children.json', 'trek_difficulty.json', 'trek_route.json', 'trek_theme.json',
                                'trek_practice.json', 'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json',
                                'trek_ids_2.json', 'trek_2.json', 'trek_children.json', 'trek_difficulty.json', 'trek_route.json', 'trek_theme.json',
                                'trek_practice.json', 'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json',
                                'trek_ids_2.json', 'trek_2_after.json', 'trek_children.json', ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=0)
        self.assertEqual(Trek.objects.count(), 5)
        trek = Trek.objects.get(name_fr="Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name, "Loop of the pic of 3 lords")
        self.assertEqual(trek.name_en, "Loop of the pic of 3 lords")
        self.assertEqual(trek.name_fr, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(str(trek.difficulty), 'Very easy')
        self.assertEqual(str(trek.difficulty.difficulty_en), 'Very easy')
        self.assertEqual(str(trek.practice), 'Horse')
        self.assertAlmostEqual(trek.geom[0][0], 569946.9850365581, places=5)
        self.assertAlmostEqual(trek.geom[0][1], 6190964.893167565, places=5)
        self.assertEqual(trek.children.first().name, "Bar")
        self.assertEqual(trek.labels.count(), 3)
        self.assertEqual(trek.labels.first().name, "Dogs are great")
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrek2TrekParser', verbosity=0)
        self.assertEqual(Trek.objects.count(), 6)
        trek = Trek.objects.get(name_fr="Étangs du Picot")
        self.assertEqual(trek.description_teaser_fr, "Chapeau")
        self.assertEqual(trek.description_teaser_it, "Cappello")
        self.assertEqual(trek.description_teaser_es, "Sombrero")
        self.assertEqual(trek.description_teaser_en, "Cap")
        self.assertEqual(trek.description_teaser, "Cap")
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrek2TrekParser', verbosity=0)
        trek.refresh_from_db()
        self.assertEqual(Trek.objects.count(), 6)
        self.assertEqual(trek.description_teaser_fr, "Chapeau 2")
        self.assertEqual(trek.description_teaser_it, "Cappello 2")
        self.assertEqual(trek.description_teaser_es, "Sombrero 2")
        self.assertEqual(trek.description_teaser_en, "Cap 2")
        self.assertEqual(trek.description_teaser, "Cap 2")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_children_do_not_exist(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['trek_difficulty.json', 'trek_route.json', 'trek_theme.json', 'trek_practice.json',
                                'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json', 'trek_ids.json',
                                'trek.json', 'trek_children_do_not_exist.json', ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200
        output = StringIO()
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=2,
                     stdout=output)
        self.assertIn("One trek has not be generated for Boucle du Pic des Trois Seigneurs : could not find trek with UUID c9567576-2934-43ab-666e-e13d02c671a9,\n", output.getvalue())
        self.assertIn("Trying to retrieve children for missing trek : could not find trek with UUID b2aea666-5e6e-4daa-a750-7d2ee52d3fe1", output.getvalue())

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_wrong_children_error(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['trek_difficulty.json', 'trek_route.json', 'trek_theme.json', 'trek_practice.json',
                                'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json', 'trek_ids.json',
                                'trek.json', 'trek_wrong_children.json', ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200
        output = StringIO()

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=2,
                     stdout=output)
        self.assertIn("An error occured in children generation : KeyError('steps'", output.getvalue())

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr")
    def test_updated(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['trek_difficulty.json', 'trek_route.json', 'trek_theme.json', 'trek_practice.json',
                                'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json', 'trek_ids.json', 'trek.json',
                                'trek_children.json', 'trek_difficulty.json', 'trek_route.json', 'trek_theme.json',
                                'trek_practice.json', 'trek_accessibility.json', 'trek_network.json', 'trek_label.json', 'sources.json',
                                'trek_ids_2.json', 'trek_2.json', 'trek_children.json', ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=0)
        self.assertEqual(Trek.objects.count(), 5)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name_fr, "Boucle du Pic des Trois Seigneurs")
        self.assertEqual(trek.name_en, "Loop of the pic of 3 lords")
        self.assertEqual(str(trek.difficulty), 'Très facile')
        self.assertEqual(str(trek.practice), 'Cheval')
        self.assertAlmostEqual(trek.geom[0][0], 569946.9850365581, places=5)
        self.assertAlmostEqual(trek.geom[0][1], 6190964.893167565, places=5)
        self.assertEqual(trek.children.first().name, "Foo")
        self.assertEqual(trek.labels.count(), 3)
        self.assertEqual(trek.labels.first().name, "Chien autorisé")
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekTrekParser', verbosity=0)
        # Trek 2 is still in ids (trek_ids_2) => it's not removed
        self.assertEqual(Trek.objects.count(), 2)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name, "Boucle du Pic des Trois Seigneurs")


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
class POIGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = "trekking"

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="en")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['poi_type.json', 'poi_ids.json', 'poi.json']

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekPOIParser', verbosity=0)
        self.assertEqual(POI.objects.count(), 2)
        poi = POI.objects.all().first()
        self.assertEqual(poi.name, "Peak of the Three Lords")
        self.assertEqual(poi.name_fr, "Pic des Trois Seigneurs")
        self.assertEqual(poi.name_en, "Peak of the Three Lords")
        self.assertEqual(poi.name_it, "Picco dei Tre Signori")
        self.assertEqual(str(poi.type), 'Peak')
        self.assertAlmostEqual(poi.geom.x, 572298.7056448072, places=5)
        self.assertAlmostEqual(poi.geom.y, 6193580.839504813, places=5)


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
class ServiceGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = "trekking"

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['service_type.json', 'service_ids.json', 'service.json']

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrekServiceParser', verbosity=0)
        self.assertEqual(Service.objects.count(), 2)
        service = Service.objects.all().first()
        self.assertEqual(str(service.type), 'Eau potable')
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
            with open(filename, 'r') as f:
                json_payload = f.read()
            data = json.loads(json_payload)
            rv.json = lambda: data
        else:
            parsed_url = urlparse(url)
            url_path = parsed_url.path
            extension = url_path.split('.')[1]
            if extension == 'jpg':
                rv.content = copy(testdata.IMG_FILE)
            elif extension in ['gpx', 'kml']:
                filename = os.path.join(test_data_dir, url_path.lstrip('/'))
                with open(filename, 'r') as f:
                    geodata = f.read()
                rv.content = bytes(geodata, 'utf-8')
            elif extension == 'kmz':
                filename = os.path.join(test_data_dir, url_path.lstrip('/'))
                with open(filename, 'rb') as f:
                    geodata = f.read()
                rv.content = geodata
        return rv

    return dummy_get


class TestApidaeTrekParser(ApidaeTrekParser):
    url = 'https://example.net/fake/api/'
    api_key = 'ABCDEF'
    project_id = 1234
    selection_id = 654321


class TestApidaeTrekSameValueDefaultLanguageDifferentTranslationParser(TestApidaeTrekParser):
    def filter_description(self, src, val):
        description = super().filter_description(src, val)
        self.set_value('description_fr', src, "FOOBAR")
        return description


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
class ApidaeTrekParserTests(TestCase):

    @staticmethod
    def make_dummy_get(apidae_data_file):
        return make_dummy_apidae_get(
            parser_class=TestApidaeTrekParser,
            test_data_dir='geotrek/trekking/tests/data/apidae_trek_parser',
            data_filename=apidae_data_file
        )

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch('requests.get')
    def test_trek_is_imported(self, mocked_get):
        RouteFactory(route='Boucle')
        mocked_get.side_effect = self.make_dummy_get('a_trek.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.name_fr, 'Une belle randonnée de test')
        self.assertEqual(trek.name_en, 'A great hike to test')
        self.assertEqual(trek.description_teaser_fr, 'La description courte en français.')
        self.assertEqual(trek.description_teaser_en, 'The short description in english.')
        self.assertEqual(trek.ambiance_fr, 'La description détaillée en français.')
        self.assertEqual(trek.ambiance_en, 'The longer description in english.')
        expected_fr_description = (
            '<p>Départ : du parking de la Chapelle Saint Michel </p>'
            '<p>1/ Suivre le chemin qui part à droite, traversant le vallon.</p>'
            '<p>2/ Au carrefour tourner à droite et suivre la rivière</p>'
            '<p>3/ Retour à la chapelle en passant à travers le petit bois.</p>'
            '<p>Ouvert toute l\'année</p>'
            '<p>Fermeture exceptionnelle en cas de pluie forte</p>'
            '<p>Suivre le balisage GR (blanc/rouge) ou GRP (jaune/rouge).</p>'
            '<p>Montée en télésiège payante. 2 points de vente - télésiège Frastaz et Bois Noir.</p>'
            '<p><strong>Site web (URL):</strong>https://example.com/ma_rando.html<br>'
            '<strong>Téléphone:</strong>01 23 45 67 89<br>'
            '<strong>Mél:</strong>accueil-rando@example.com<br>'
            '<strong>Signaux de fumée:</strong>1 gros nuage suivi de 2 petits</p>'
        )
        self.assertEqual(trek.description_fr, expected_fr_description)
        expected_en_description = (
            '<p>Start: from the parking near the Chapelle Saint Michel </p>'
            '<p>1/ Follow the path starting at right-hand, cross the valley.</p>'
            '<p>2/ At the crossroad turn left and follow the river.</p>'
            '<p>3/ Back to the chapelle by the woods.</p>'
            '<p>Open all year long</p>'
            '<p>Exceptionally closed during heavy rain</p>'
            '<p>Follow the GR (white / red) or GRP (yellow / red) markings.</p>'
            '<p>Ski lift ticket office: 2 shops - Frastaz and Bois Noir ski lifts.</p>'
            '<p><strong>Website:</strong>https://example.com/ma_rando.html<br>'
            '<strong>Telephone:</strong>01 23 45 67 89<br>'
            '<strong>e-mail:</strong>accueil-rando@example.com<br>'
            '<strong>Smoke signals:</strong>1 gros nuage suivi de 2 petits</p>'
        )
        self.assertEqual(trek.description_en, expected_en_description)
        self.assertEqual(trek.advised_parking_fr, 'Parking sur la place du village')
        self.assertEqual(trek.advised_parking_en, 'Parking sur la place du village')
        self.assertEqual(trek.departure_fr, 'Sallanches')
        self.assertEqual(trek.departure_en, 'Sallanches')
        self.assertEqual(trek.access_fr, 'En voiture, rejoindre le village de Salanches.')
        self.assertEqual(trek.access_en, 'By car, go to the village of Sallanches.')
        self.assertEqual(trek.access_it, 'In auto, andare al villaggio di Sallances.')
        self.assertEqual(len(trek.source.all()), 1)
        self.assertEqual(trek.source.first().name, 'Office de tourisme de Sallanches')
        self.assertEqual(trek.source.first().website, 'https://www.example.net/ot-sallanches')

        self.assertTrue(trek.difficulty is not None)
        self.assertEqual(trek.difficulty.difficulty_en, 'Level red – hard')

        self.assertTrue(trek.practice is not None)
        self.assertEqual(trek.practice.name, 'Pédestre')

        self.assertEqual(trek.networks.count(), 2)
        networks = trek.networks.all()
        self.assertIn('Hiking itinerary', [n.network for n in networks])
        self.assertIn('Pedestrian sports', [n.network for n in networks])

        self.assertEqual(Attachment.objects.count(), 1)
        photo = Attachment.objects.first()
        self.assertEqual(photo.author, 'The author of the picture')
        self.assertEqual(photo.legend, 'The legend of the picture')
        self.assertEqual(photo.attachment_file.size, len(testdata.IMG_FILE))
        self.assertEqual(photo.title, 'The title of the picture')

        self.assertTrue(trek.duration is not None)
        self.assertAlmostEqual(trek.duration, 2.5)

        self.assertEqual(trek.advice, "Avoid after heavy rain.")
        self.assertEqual(trek.advice_fr, "À éviter après de grosses pluies.")

        self.assertEqual(trek.route.route, 'Boucle')

        self.assertEqual(trek.accessibilities.count(), 1)
        accessibility = trek.accessibilities.first()
        self.assertEqual(accessibility.name, 'Suitable for all terrain strollers')

        self.assertIn('Rock', trek.accessibility_covering)
        self.assertIn('Ground', trek.accessibility_covering)
        self.assertIn('Rocher', trek.accessibility_covering_fr)
        self.assertIn('Terre', trek.accessibility_covering_fr)

        self.assertTrue(trek.gear is not None)
        self.assertIn("Map IGN3531OT Top 25", trek.gear)
        self.assertIn("Guidebook sold at the tourist board", trek.gear)
        self.assertIn("TOP 25 IGN 3531 OT", trek.gear_fr)
        self.assertIn("Cartoguide en vente à l'Office de Tourisme", trek.gear_fr)

        # Import an updated trek
        mocked_get.side_effect = self.make_dummy_get('a_trek_with_updated_limit_date.json')
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Attachment.objects.count(), 0)

    @mock.patch('requests.get')
    def test_trek_import_multiple_time(self, mocked_get):
        RouteFactory(route='Boucle')
        mocked_get.side_effect = self.make_dummy_get('a_trek.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        old_description_en = trek.description_en
        old_description = trek.description
        description_fr = (
            '<p>Départ : du parking de la Chapelle Saint Michel </p>'
            '<p>1/ Suivre le chemin qui part à droite, traversant le vallon.</p>'
            '<p>2/ Au carrefour tourner à droite et suivre la rivière</p>'
            '<p>3/ Retour à la chapelle en passant à travers le petit bois.</p>'
            '<p>Ouvert toute l\'année</p>'
            '<p>Fermeture exceptionnelle en cas de pluie forte</p>'
            '<p>Suivre le balisage GR (blanc/rouge) ou GRP (jaune/rouge).</p>'
            '<p>Montée en télésiège payante. 2 points de vente - télésiège Frastaz et Bois Noir.</p>'
            '<p><strong>Site web (URL):</strong>https://example.com/ma_rando.html<br>'
            '<strong>Téléphone:</strong>01 23 45 67 89<br>'
            '<strong>Mél:</strong>accueil-rando@example.com<br>'
            '<strong>Signaux de fumée:</strong>1 gros nuage suivi de 2 petits</p>'
        )
        self.assertEqual(trek.description_fr, description_fr)
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekSameValueDefaultLanguageDifferentTranslationParser',
                     verbosity=0)
        trek.refresh_from_db()
        self.assertEqual(trek.description_fr, 'FOOBAR')
        self.assertEqual(old_description_en, trek.description_en)
        self.assertEqual(old_description, trek.description)

    @mock.patch('requests.get')
    def test_trek_geometry_can_be_imported_from_gpx(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('a_trek.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.geom.srid, 2154)
        self.assertEqual(len(trek.geom.coords), 13)
        first_point = trek.geom.coords[0]
        self.assertAlmostEqual(first_point[0], 977776.9, delta=0.1)
        self.assertAlmostEqual(first_point[1], 6547354.8, delta=0.1)

    @mock.patch('requests.get')
    def test_trek_geometry_can_be_imported_from_kml(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('trek_with_kml_trace.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.geom.srid, 2154)
        self.assertEqual(len(trek.geom.coords), 61)

    @mock.patch('requests.get')
    def test_trek_geometry_can_be_imported_from_kmz(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('trek_with_kmz_trace.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Trek.objects.count(), 1)
        trek = Trek.objects.all().first()
        self.assertEqual(trek.geom.srid, 2154)
        self.assertEqual(len(trek.geom.coords), 61)

    @mock.patch('requests.get')
    def test_trek_not_imported_when_no_supported_format(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get('trek_no_supported_plan_format_error.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=2,
                     stdout=output_stdout)

        self.assertEqual(Trek.objects.count(), 0)
        self.assertIn('has no attached "PLAN" in a supported format', output_stdout.getvalue())

    @mock.patch('requests.get')
    def test_trek_not_imported_when_no_plan_attached(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get('trek_no_plan_error.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=2,
                     stdout=output_stdout)

        self.assertEqual(Trek.objects.count(), 0)
        self.assertIn('no attachment with the type "PLAN"', output_stdout.getvalue())

    @mock.patch('requests.get')
    def test_trek_not_imported_when_no_plan(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get('trek_no_plan_error.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=2,
                     stdout=output_stdout)

        self.assertEqual(Trek.objects.count(), 0)
        self.assertIn('has no attachment with the type "PLAN"', output_stdout.getvalue())

    @mock.patch('requests.get')
    def test_trek_not_imported_when_no_multimedia_attachments(self, mocked_get):
        output_stdout = StringIO()
        mocked_get.side_effect = self.make_dummy_get('trek_no_multimedia_attachments_error.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=2,
                     stdout=output_stdout)

        self.assertEqual(Trek.objects.count(), 0)
        self.assertIn('missing required field \'multimedias\'', output_stdout.getvalue().lower())

    @mock.patch('requests.get')
    def test_trek_linked_entities_are_imported(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('a_trek.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Theme.objects.count(), 2)
        themes = Theme.objects.all()
        for theme in themes:
            self.assertIn(theme.label, ['Geology', 'Historic'])
        self.assertEqual(Label.objects.count(), 3)
        labels = Label.objects.all()
        for label in labels:
            self.assertIn(label.name, ['In the country', 'Not recommended in bad weather', 'Listed PDIPR'])

    @mock.patch('requests.get')
    def test_trek_theme_with_unknown_id_is_not_imported(self, mocked_get):
        assert 12341234 not in ApidaeTrekParser.typologies_sitra_ids_as_themes

        mocked_get.side_effect = self.make_dummy_get('trek_with_unknown_theme.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Trek.objects.count(), 1)
        self.assertEqual(Theme.objects.count(), 0)

    @mock.patch('requests.get')
    def test_links_to_child_treks_are_set(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('related_treks.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Trek.objects.count(), 3)
        parent_trek = Trek.objects.get(eid='123123')
        child_trek = Trek.objects.get(eid='123124')
        child_trek_2 = Trek.objects.get(eid='123125')
        self.assertIn(parent_trek, child_trek.parents.all())
        self.assertIn(parent_trek, child_trek_2.parents.all())
        self.assertEqual(list(parent_trek.children.values_list('eid', flat=True).all()), ['123124', '123125'])

        mocked_get.side_effect = self.make_dummy_get('related_treks_updated.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Trek.objects.count(), 4)
        parent_trek = Trek.objects.get(eid='123123')
        child_trek = Trek.objects.get(eid='123124')
        child_trek_2 = Trek.objects.get(eid='123125')
        child_trek_3 = Trek.objects.get(eid='321321')
        self.assertIn(parent_trek, child_trek.parents.all())
        self.assertIn(parent_trek, child_trek_2.parents.all())
        self.assertIn(parent_trek, child_trek_3.parents.all())
        self.assertEqual(list(parent_trek.children.values_list('eid', flat=True).all()), ['123124', '321321', '123125'])

    @mock.patch('requests.get')
    def test_it_handles_not_imported_child_trek(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('related_treks_with_one_not_imported.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Trek.objects.count(), 2)
        Trek.objects.filter(eid='123123').exists()
        Trek.objects.filter(eid='123124').exists()

    @mock.patch('requests.get')
    def test_links_to_child_treks_are_set_with_changed_order_in_data(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('related_treks_another_order.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)

        self.assertEqual(Trek.objects.count(), 3)
        parent_trek = Trek.objects.get(eid='123123')
        child_trek = Trek.objects.get(eid='123124')
        child_trek_2 = Trek.objects.get(eid='123125')
        self.assertIn(parent_trek, child_trek.parents.all())
        self.assertIn(parent_trek, child_trek_2.parents.all())
        self.assertEqual(list(parent_trek.children.values_list('eid', flat=True).all()), ['123124', '123125'])

    @mock.patch('requests.get')
    def test_trek_illustration_is_not_imported_on_missing_file_metadata(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('trek_with_not_complete_illustration.json')
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekParser', verbosity=0)
        self.assertEqual(Attachment.objects.count(), 0)


class TestApidaeTrekThemeParser(ApidaeTrekThemeParser):

    url = 'https://example.net/fake/api/'
    api_key = 'ABCDEF'
    project_id = 1234
    element_reference_ids = [6157]


class ApidaeTrekThemeParserTests(TestCase):

    def mocked_get_func(self, url, params, *args, **kwargs):
        self.assertEqual(url, TestApidaeTrekThemeParser.url)
        expected_query_param = {
            'apiKey': TestApidaeTrekThemeParser.api_key,
            'projetId': TestApidaeTrekThemeParser.project_id,
            'elementReferenceIds': TestApidaeTrekThemeParser.element_reference_ids,
        }
        self.assertDictEqual(json.loads(params['query']), expected_query_param)

        rv = Mock()
        rv.status_code = 200
        with open('geotrek/trekking/tests/data/apidae_trek_parser/trek_theme.json', 'r') as f:
            json_payload = f.read()
        data = json.loads(json_payload)
        rv.json = lambda: data

        return rv

    @mock.patch('requests.get')
    def test_theme_is_created_with_configured_languages(self, mocked_get):
        mocked_get.side_effect = self.mocked_get_func

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekThemeParser', verbosity=0)

        self.assertEqual(len(Theme.objects.all()), 1)
        theme = Theme.objects.first()
        self.assertEqual(theme.label_fr, 'Géologie')
        self.assertEqual(theme.label_en, 'Geology')
        self.assertEqual(theme.label_es, 'Geología')
        self.assertEqual(theme.label_it, 'Geologia')

    @mock.patch('requests.get')
    def test_theme_is_identified_with_default_language_on_update(self, mocked_get):
        mocked_get.side_effect = self.mocked_get_func
        theme = Theme(label_en='Geology', label_fr='Géologie (cette valeur sera écrasée)')
        theme.save()

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekThemeParser', verbosity=0)

        self.assertEqual(len(Theme.objects.all()), 1)
        theme = Theme.objects.first()
        self.assertEqual(theme.label_en, 'Geology')
        self.assertEqual(theme.label_fr, 'Géologie')
        self.assertEqual(theme.label_es, 'Geología')
        self.assertEqual(theme.label_it, 'Geologia')

    @mock.patch('requests.get')
    def test_another_theme_is_created_when_default_language_name_changes(self, mocked_get):
        mocked_get.side_effect = self.mocked_get_func
        theme = Theme(label_en='With interesting rocks', label_fr='Géologie', label_it='Geologia', label_es='Geologia')
        theme.save()

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaeTrekThemeParser', verbosity=0)

        self.assertEqual(len(Theme.objects.all()), 2)


class MakeDescriptionTests(SimpleTestCase):

    def setUp(self):
        self.ouverture = {
            'periodeEnClair': {
                'libelleFr': 'Ouvert toute l\'année\n\nFermeture exceptionnelle en cas de pluie forte',
                'libelleEn': 'Open all year long\n\nExceptionally closed during heavy rain'
            }
        }
        self.descriptifs = [
            {
                'theme': {
                    'id': 6527,
                    'libelleFr': 'Topo/pas à pas',
                    'libelleEn': 'Guidebook with maps/step-by-step'
                },
                'description': {
                    'libelleFr': 'Départ : du parking de la Chapelle Saint Michel \r\n'
                                 '1/ Suivre le chemin qui part à droite, traversant le vallon.\r\n'
                                 '2/ Au carrefour tourner à droite et suivre la rivière\r\n'
                                 '3/ Retour à la chapelle en passant à travers le petit bois.',
                    'libelleEn': 'Start: from the parking near the Chapelle Saint Michel \r\n'
                                 '1/ Follow the path starting at right-hand, cross the valley.\r\n'
                                 '2/ At the crossroad turn left and follow the river.\r\n'
                                 '3/ Back to the chapelle by the woods.'
                }
            }
        ]
        self.itineraire = {
            'itineraireBalise': 'BALISE',
            'precisionsBalisage': {
                'libelleFr': 'Suivre le balisage GR (blanc/rouge) ou GRP (jaune/rouge).',
                'libelleEn': 'Follow the GR (white / red) or GRP (yellow / red) markings.'
            }
        }

    def test_it_returns_the_right_elements_in_description(self):
        description = ApidaeTrekParser._make_description(self.ouverture, self.descriptifs, self.itineraire)
        expected_fr_description = (
            '<p>Départ : du parking de la Chapelle Saint Michel </p>'
            '<p>1/ Suivre le chemin qui part à droite, traversant le vallon.</p>'
            '<p>2/ Au carrefour tourner à droite et suivre la rivière</p>'
            '<p>3/ Retour à la chapelle en passant à travers le petit bois.</p>'
            '<p>Ouvert toute l\'année</p>'
            '<p>Fermeture exceptionnelle en cas de pluie forte</p>'
            '<p>Suivre le balisage GR (blanc/rouge) ou GRP (jaune/rouge).</p>'
        )
        self.assertEqual(description.to_dict()['fr'], expected_fr_description)
        expected_en_description = (
            '<p>Start: from the parking near the Chapelle Saint Michel </p>'
            '<p>1/ Follow the path starting at right-hand, cross the valley.</p>'
            '<p>2/ At the crossroad turn left and follow the river.</p>'
            '<p>3/ Back to the chapelle by the woods.</p>'
            '<p>Open all year long</p>'
            '<p>Exceptionally closed during heavy rain</p>'
            '<p>Follow the GR (white / red) or GRP (yellow / red) markings.</p>'
        )
        self.assertEqual(description.to_dict()['en'], expected_en_description)

    def test_it_places_temporary_closed_warning_first(self):
        temporary_closed = {
            'periodeEnClair': {
                'libelleFr': 'Fermé temporairement.',
                'libelleEn': 'Closed temporarily.'
            },
            'fermeTemporairement': 'FERME_TEMPORAIREMENT'
        }
        description = ApidaeTrekParser._make_description(temporary_closed, self.descriptifs, self.itineraire)
        expected_fr_description = (
            '<p>Fermé temporairement.</p>'
            '<p>Départ : du parking de la Chapelle Saint Michel </p>'
            '<p>1/ Suivre le chemin qui part à droite, traversant le vallon.</p>'
            '<p>2/ Au carrefour tourner à droite et suivre la rivière</p>'
            '<p>3/ Retour à la chapelle en passant à travers le petit bois.</p>'
            '<p>Suivre le balisage GR (blanc/rouge) ou GRP (jaune/rouge).</p>'
        )
        self.assertEqual(description.to_dict()['fr'], expected_fr_description)
        expected_en_description = (
            '<p>Closed temporarily.</p>'
            '<p>Start: from the parking near the Chapelle Saint Michel </p>'
            '<p>1/ Follow the path starting at right-hand, cross the valley.</p>'
            '<p>2/ At the crossroad turn left and follow the river.</p>'
            '<p>3/ Back to the chapelle by the woods.</p>'
            '<p>Follow the GR (white / red) or GRP (yellow / red) markings.</p>'
        )
        self.assertEqual(description.to_dict()['en'], expected_en_description)


class MakeMarkingDescriptionTests(SimpleTestCase):

    def test_it_returns_default_text_when_not_marked(self):
        itineraire = {'itineraireBalise': None}
        description = ApidaeTrekParser._make_marking_description(itineraire)
        self.assertDictEqual(description, ApidaeTrekParser.trek_no_marking_description)

    def test_it_returns_given_text(self):
        precisions = {
            'libelleFr': 'fr-marked itinerary',
            'libelleEn': 'en-marked itinerary',
            'libelleEs': 'es-marked itinerary',
            'libelleIt': 'it-marked itinerary',
        }
        itineraire = {
            'itineraireBalise': 'BALISE',
            'precisionsBalisage': precisions
        }
        description = ApidaeTrekParser._make_marking_description(itineraire)
        self.assertDictEqual(description, precisions)

    def test_it_returns_given_partial_text_mixed_with_default(self):
        partial_precisions = {
            'libelleEn': 'en-marked itinerary',
            'libelleEs': 'es-marked itinerary',
            'libelleIt': 'it-marked itinerary',
        }
        itineraire = {
            'itineraireBalise': 'BALISE',
            'precisionsBalisage': partial_precisions
        }
        description = ApidaeTrekParser._make_marking_description(itineraire)
        expected = {
            'libelleFr': ApidaeTrekParser.default_trek_marking_description['libelleFr'],
            'libelleEn': 'en-marked itinerary',
            'libelleEs': 'es-marked itinerary',
            'libelleIt': 'it-marked itinerary',
        }
        self.assertDictEqual(description, expected)

    def test_it_returns_default_text_when_no_details(self):
        itineraire = {
            'itineraireBalise': 'BALISE',
        }
        description = ApidaeTrekParser._make_marking_description(itineraire)
        self.assertDictEqual(description, ApidaeTrekParser.default_trek_marking_description)


class GpxToGeomTests(SimpleTestCase):

    @staticmethod
    def _get_gpx_from(filename):
        with open(filename, 'r') as f:
            gpx = f.read()
        return bytes(gpx, 'utf-8')

    def test_gpx_with_waypoint_can_be_converted(self):
        gpx = self._get_gpx_from('geotrek/trekking/tests/data/apidae_trek_parser/apidae_test_trek.gpx')

        geom = ApidaeTrekParser._get_geom_from_gpx(gpx)

        self.assertEqual(geom.srid, 2154)
        self.assertEqual(geom.geom_type, 'LineString')
        self.assertEqual(len(geom.coords), 13)
        first_point = geom.coords[0]
        self.assertAlmostEqual(first_point[0], 977776.9, delta=0.1)
        self.assertAlmostEqual(first_point[1], 6547354.8, delta=0.1)

    def test_gpx_with_route_points_can_be_converted(self):
        gpx = self._get_gpx_from('geotrek/trekking/tests/data/apidae_trek_parser/trace_with_route_points.gpx')

        geom = ApidaeTrekParser._get_geom_from_gpx(gpx)

        self.assertEqual(geom.srid, 2154)
        self.assertEqual(geom.geom_type, 'LineString')
        self.assertEqual(len(geom.coords), 13)
        first_point = geom.coords[0]
        self.assertAlmostEqual(first_point[0], 977776.9, delta=0.1)
        self.assertAlmostEqual(first_point[1], 6547354.8, delta=0.1)

    def test_it_raises_an_error_on_not_continuous_segments(self):
        gpx = self._get_gpx_from('geotrek/trekking/tests/data/apidae_trek_parser/trace_with_not_continuous_segments.gpx')

        with self.assertRaises(RowImportError):
            ApidaeTrekParser._get_geom_from_gpx(gpx)

    def test_it_handles_segment_with_single_point(self):
        gpx = self._get_gpx_from(
            'geotrek/trekking/tests/data/apidae_trek_parser/trace_with_single_point_segment.gpx'
        )
        geom = ApidaeTrekParser._get_geom_from_gpx(gpx)

        self.assertEqual(geom.srid, 2154)
        self.assertEqual(geom.geom_type, 'LineString')
        self.assertEqual(len(geom.coords), 13)


class KmlToGeomTests(SimpleTestCase):

    @staticmethod
    def _get_kml_from(filename):
        with open(filename, 'r') as f:
            kml = f.read()
        return bytes(kml, 'utf-8')

    def test_kml_can_be_converted(self):
        kml = self._get_kml_from('geotrek/trekking/tests/data/apidae_trek_parser/trace.kml')

        geom = ApidaeTrekParser._get_geom_from_kml(kml)

        self.assertEqual(geom.srid, 2154)
        self.assertEqual(geom.geom_type, 'LineString')
        self.assertEqual(len(geom.coords), 61)
        first_point = geom.coords[0]
        self.assertAlmostEqual(first_point[0], 973160.8, delta=0.1)
        self.assertAlmostEqual(first_point[1], 6529320.1, delta=0.1)

    def test_it_raises_exception_when_no_linear_data(self):
        kml = self._get_kml_from('geotrek/trekking/tests/data/apidae_trek_parser/trace_with_no_line.kml')

        with self.assertRaises(RowImportError):
            ApidaeTrekParser._get_geom_from_kml(kml)


class GetPracticeNameFromActivities(SimpleTestCase):

    def test_it_considers_specific_activity_before_default_activity(self):
        practice_name = ApidaeTrekParser._get_practice_name_from_activities(
            [
                3113,  # Sports cyclistes
                3284,  # Itinéraire VTT
            ]
        )
        self.assertEqual(practice_name, 'VTT')

    def test_it_takes_default_activity_if_no_specific_match(self):
        not_mapped_activity_id = 12341234
        practice_name = ApidaeTrekParser._get_practice_name_from_activities(
            [
                not_mapped_activity_id,
                3113,  # Sports cyclistes
            ]
        )
        self.assertEqual(practice_name, 'Vélo')


class IsStillPublishableOn(SimpleTestCase):

    def test_it_returns_true(self):
        illustration = {'dateLimiteDePublication': '2020-06-28T00:00:00.000+0000'}
        a_date_before_that = date(year=2020, month=3, day=10)
        self.assertTrue(ApidaeTrekParser._is_still_publishable_on(illustration, a_date_before_that))

    def test_it_returns_false(self):
        illustration = {'dateLimiteDePublication': '2020-06-28T00:00:00.000+0000'}
        a_date_after_that = date(year=2020, month=8, day=10)
        self.assertFalse(ApidaeTrekParser._is_still_publishable_on(illustration, a_date_after_that))

    def test_it_considers_date_limite_is_not_included(self):
        illustration = {'dateLimiteDePublication': '2020-06-28T00:00:00.000+0000'}
        that_same_date = date(year=2020, month=6, day=28)
        self.assertFalse(ApidaeTrekParser._is_still_publishable_on(illustration, that_same_date))


class MakeDurationTests(SimpleTestCase):

    def test_it_returns_correct_duration_from_duration_in_minutes(self):
        self.assertAlmostEqual(ApidaeTrekParser._make_duration(duration_in_minutes=90), 1.5)

    def test_it_returns_correct_duration_from_duration_in_days(self):
        self.assertAlmostEqual(ApidaeTrekParser._make_duration(duration_in_days=3), 72.0)

    def test_giving_both_duration_arguments_only_duration_in_minutes_is_considered(self):
        self.assertAlmostEqual(ApidaeTrekParser._make_duration(duration_in_minutes=90, duration_in_days=0.5), 1.5)

    def test_it_rounds_output_to_two_decimal_places(self):
        self.assertEqual(ApidaeTrekParser._make_duration(duration_in_minutes=20), 0.33)


class TestApidaePOIParser(ApidaePOIParser):
    url = 'https://example.net/fake/api/'
    api_key = 'ABCDEF'
    project_id = 1234
    selection_id = 654321


@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
class ApidaePOIParserTests(TestCase):

    @staticmethod
    def make_dummy_get(apidae_data_file):
        return make_dummy_apidae_get(
            parser_class=TestApidaePOIParser,
            test_data_dir='geotrek/trekking/tests/data/apidae_poi_parser',
            data_filename=apidae_data_file
        )

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch('requests.get')
    def test_POI_is_imported(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('a_poi.json')

        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaePOIParser', verbosity=0)

        self.assertEqual(POI.objects.count(), 1)
        poi = POI.objects.all().first()
        self.assertEqual(poi.name_fr, 'Un point d\'intérêt')
        self.assertEqual(poi.name_en, 'A point of interest')
        self.assertEqual(poi.description_fr, 'La description courte en français.')
        self.assertEqual(poi.description_en, 'The short description in english.')

        self.assertEqual(poi.geom.srid, settings.SRID)
        self.assertAlmostEqual(poi.geom.coords[0], 729136.5, delta=0.1)
        self.assertAlmostEqual(poi.geom.coords[1], 6477050.1, delta=0.1)

        self.assertEqual(Attachment.objects.count(), 1)
        photo = Attachment.objects.first()
        self.assertEqual(photo.author, 'The author of the picture')
        self.assertEqual(photo.legend, 'The legend of the picture')
        self.assertEqual(photo.attachment_file.size, len(testdata.IMG_FILE))
        self.assertEqual(photo.title, 'The title of the picture')

        self.assertEqual(poi.type.label_en, 'Patrimoine culturel')
        self.assertEqual(poi.type.label_fr, None)

    @mock.patch('requests.get')
    def test_trek_illustration_is_not_imported_on_missing_file_metadata(self, mocked_get):
        mocked_get.side_effect = self.make_dummy_get('poi_with_not_complete_illustration.json')
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestApidaePOIParser', verbosity=0)
        self.assertEqual(Attachment.objects.count(), 0)


class PrepareAttachmentFromIllustrationTests(TestCase):

    def setUp(self):
        self.illustration = {
            'nom': {
                'libelleEn': 'The title of the picture'
            },
            'legende': {
                'libelleEn': 'The legend of the picture'
            },
            'copyright': {
                'libelleEn': 'The author of the picture'
            },
            'traductionFichiers': [
                {
                    'url': 'https://example.net/a_picture.jpg'
                }
            ]
        }

    def test_given_full_illustration_it_returns_attachment_info(self):
        expected_result = (
            'https://example.net/a_picture.jpg',
            'The legend of the picture',
            'The author of the picture',
            'The title of the picture'
        )
        self.assertEqual(
            _prepare_attachment_from_apidae_illustration(self.illustration, 'libelleEn'),
            expected_result
        )

    def test_it_returns_empty_strings_for_missing_info(self):
        del self.illustration['legende']
        del self.illustration['copyright']
        del self.illustration['nom']
        expected_result = (
            'https://example.net/a_picture.jpg',
            '',
            '',
            ''
        )
        self.assertEqual(
            _prepare_attachment_from_apidae_illustration(self.illustration, 'libelleEn'),
            expected_result
        )

    def test_it_substitutes_name_to_missing_legend(self):
        del self.illustration['legende']
        self.illustration['nom'] = {'libelleEn': 'The title of the picture which will also be the legend'}
        expected_result = (
            'https://example.net/a_picture.jpg',
            'The title of the picture which will also be the legend',
            'The author of the picture',
            'The title of the picture which will also be the legend'
        )
        self.assertEqual(
            _prepare_attachment_from_apidae_illustration(self.illustration, 'libelleEn'),
            expected_result
        )

    def test_it_returns_empty_strings_if_translation_not_found(self):
        self.illustration['legende'] = {}
        self.illustration['copyright'] = {}
        self.illustration['nom'] = {}
        expected_result = (
            'https://example.net/a_picture.jpg',
            '',
            '',
            ''
        )
        self.assertEqual(
            _prepare_attachment_from_apidae_illustration(self.illustration, 'libelleEn'),
            expected_result
        )
