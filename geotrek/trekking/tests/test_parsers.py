from io import StringIO
from unittest import mock
import json
import os
from unittest import skipIf

from django.conf import settings
from django.contrib.gis.geos import Point, LineString, MultiLineString, WKTWriter
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.common.models import Theme, FileType, Attachment
from geotrek.common.tests.mixins import GeotrekParserTestMixin
from geotrek.trekking.models import POI, Service, Trek, DifficultyLevel, Route
from geotrek.trekking.parsers import TrekParser, GeotrekPOIParser, GeotrekServiceParser, GeotrekTrekParser


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
        self.assertEqual(self.parser.filter_geom('geom', geom), None)
        self.assertTrue(self.parser.warnings)

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
