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
from geotrek.common.models import Organism, Theme, FileType, Attachment, Label
from geotrek.common.tests.mixins import GeotrekParserTestMixin
from geotrek.core.tests.factories import PathFactory
from geotrek.outdoor.models import Site
from geotrek.outdoor.parsers import GeotrekSiteParser
from geotrek.trekking.tests.factories import RouteFactory
from geotrek.trekking.models import POI, POIType, Service, Trek, DifficultyLevel, Route
from geotrek.trekking.parsers import (
    TrekParser, GeotrekPOIParser, GeotrekServiceParser, GeotrekTrekParser, ApidaeTrekParser, ApidaeTrekThemeParser,
    ApidaePOIParser, _prepare_attachment_from_apidae_illustration, RowImportError
)



class TestGeotrekSiteParser(GeotrekSiteParser):
    url = "https://test.fr"
    provider = 'geotrek1'
    field_options = {
        'type': {'create': True, },
        'ratings': {'create': True, },
        'themes': {'create': True},
        'practice': {'create': True},
        'geom': {'required': True},
        'labels': {'create': True},
        'source': {'create': True},
        'managers': {'create': True},
        'structure': {'create': True}
    }


class TestGeotrek2SiteParser(GeotrekSiteParser):
    url = "https://test.fr"

    field_options = {
        'geom': {'required': True},
    }
    provider = 'geotrek2'


# class TestGeotrekPOIParser(GeotrekPOIParser):             # TODO IndoDesk ? WebLink ? 
#     url = "https://test.fr"

#     field_options = {
#         'type': {'create': True, },
#         'geom': {'required': True},
#     }


# class TestGeotrekServiceParser(GeotrekServiceParser):
#     url = "https://test.fr"

#     field_options = {
#         'type': {'create': True, },
#         'geom': {'required': True},
#     }


@override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr")
@skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
class SiteGeotrekParserTests(GeotrekParserTestMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [('outdoor', 'outdoor_practice.json'),
                                ('outdoor', 'outdoor_rating.json'),
                                ('outdoor', 'theme.json'),
                                ('outdoor', 'outdoor_sitetype.json'),
                                ('outdoor', 'label.json'),
                                ('outdoor', 'source.json'),
                                ('outdoor', 'organism.json'),
                                ('outdoor', 'structure.json'),
                                ('outdoor', 'outdoor_site_ids.json'),
                                ('outdoor', 'outdoor_site.json')]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.outdoor.tests.test_parsers.TestGeotrekSiteParser', verbosity=0)
        self.assertEqual(Site.objects.count(), 6)
        site = Site.objects.get(name_fr="Racine", name_en="Root")
        # TODO : all the ones that are commented do not work
        self.assertEqual(site.published, True)
        self.assertEqual(site.published_fr, True)
        self.assertEqual(site.published_en, True)
        self.assertEqual(site.published_it, False)
        self.assertEqual(site.published_es, False)
        self.assertEqual(str(site.practice), 'Escalade')
        self.assertEqual(str(site.labels.first()), 'Label fr')
        #self.assertEqual(str(site.ratings.all()), 'Très facile')
        #self.assertEqual(str(site.practice.sector), 'Vertical')
        self.assertEqual(str(site.type), 'Ecole')
        self.assertAlmostEqual(site.geom[0][0][0][0], 970023.8976707931, places=5)
        self.assertAlmostEqual(site.geom[0][0][0][1], 6308806.903248067, places=5)
        self.assertAlmostEqual(site.geom[0][0][1][0], 967898.282139539, places=5)
        self.assertAlmostEqual(site.geom[0][0][1][1], 6358768.657410889, places=5)
        self.assertEqual(str(site.labels.first()), "Label fr")
        self.assertEqual(str(site.source.first()), "Source")
        self.assertEqual(str(site.themes.first()), "Test thème fr")
        self.assertEqual(str(site.managers.first()), "Organisme")
        self.assertEqual(str(site.structure), "Test structure")
        self.assertEqual(site.description_teaser, "Test fr")
        self.assertEqual(site.description_teaser_en, "Test en")
        self.assertEqual(site.description, "Test descr fr")
        self.assertEqual(site.description_en, "Test descr en")
        self.assertEqual(site.advice, "Test reco fr")
        self.assertEqual(site.accessibility, "Test access fr")
        self.assertEqual(site.period, "Test périod fr")
        self.assertEqual(site.orientation, ['NE', 'S'])
        self.assertEqual(site.ambiance, "Test ambiance fr")
        self.assertEqual(site.ambiance_en, "Test ambiance en")
        #self.assertEqual(site.parent) # TODO use other to test this
        self.assertEqual(site.wind, ['N', 'E'])
        # self.assertEqual(site.information_desks.count(), 1)
        # self.assertEqual(site.weblink.count(), 1)
        # self.assertEqual(site.excluded_pois.count(), 1)
        self.assertEqual(site.eid, "57a8fb52-213d-4dce-8224-bc997f892aae")
        # self.assertEqual(Attachment.objects.filter(object_id=site.pk).count(), 3)
        # self.assertEqual(Attachment.objects.get(object_id=site.pk, license__isnull=False).license.label, "License")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_create_multiple_page(self, mocked_head, mocked_get):
        class MockResponse:
            mock_json_order = [('trekking', 'trek_difficulty.json'),
                               ('trekking', 'trek_route.json'),
                               ('trekking', 'trek_theme.json'),
                               ('trekking', 'trek_practice.json'),
                               ('trekking', 'trek_accessibility.json'),
                               ('trekking', 'trek_network.json'),
                               ('trekking', 'trek_label.json'),
                               ('trekking', 'sources.json'),
                               ('trekking', 'trek_ids.json'),
                               ('trekking', 'trek.json'),
                               ('trekking', 'trek_children.json'),
                               ('trekking', 'trek_children.json')]
            mock_time = 0
            total_mock_response = 1

            def __init__(self, status_code):
                self.status_code = status_code

            def json(self):
                filename = os.path.join('geotrek', self.mock_json_order[self.mock_time][0], 'tests', 'data',
                                        'geotrek_parser_v2', self.mock_json_order[self.mock_time][1])
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
        self.mock_json_order = [('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids.json'),
                                ('trekking', 'trek.json'),
                                ('trekking', 'trek_children.json')]

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
            mock_json_order = [('trekking', 'trek_difficulty.json'),
                               ('trekking', 'trek_route.json'),
                               ('trekking', 'trek_theme.json'),
                               ('trekking', 'trek_practice.json'),
                               ('trekking', 'trek_accessibility.json'),
                               ('trekking', 'trek_network.json'),
                               ('trekking', 'trek_label.json'),
                               ('trekking', 'sources.json'),
                               ('trekking', 'trek_ids.json'),
                               ('trekking', 'trek.json'),
                               ('trekking', 'trek_children.json')]
            mock_time = 0
            a = 0

            def __init__(self, status_code):
                self.status_code = status_code

            def json(self):
                if len(self.mock_json_order) <= self.mock_time:
                    self.mock_time = 0
                filename = os.path.join('geotrek', self.mock_json_order[self.mock_time][0], 'tests', 'data',
                                        'geotrek_parser_v2', self.mock_json_order[self.mock_time][1])

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
        self.mock_json_order = [('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids.json'),
                                ('trekking', 'trek.json'),
                                ('trekking', 'trek_children.json'),
                                ('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids_2.json'),
                                ('trekking', 'trek_2.json'),
                                ('trekking', 'trek_children.json'),
                                ('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids_2.json'),
                                ('trekking', 'trek_2_after.json'),
                                ('trekking', 'trek_children.json'), ]

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
        self.assertEqual(trek.description_teaser_es, "Chapeau")
        self.assertEqual(trek.description_teaser_en, "Cap")
        self.assertEqual(trek.description_teaser, "Chapeau")
        self.assertEqual(trek.published, True)
        self.assertEqual(trek.published_fr, True)
        self.assertEqual(trek.published_en, False)
        self.assertEqual(trek.published_it, False)
        self.assertEqual(trek.published_es, False)
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrek2TrekParser', verbosity=0)
        trek.refresh_from_db()
        self.assertEqual(Trek.objects.count(), 6)
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

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="en")
    def test_create_multiple_en(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids.json'),
                                ('trekking', 'trek.json'),
                                ('trekking', 'trek_children.json'),
                                ('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids_2.json'),
                                ('trekking', 'trek_2.json'),
                                ('trekking', 'trek_children.json'),
                                ('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids_2.json'),
                                ('trekking', 'trek_2_after.json'),
                                ('trekking', 'trek_children.json')]

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
        self.assertEqual(trek.description_teaser_es, "Cap")
        self.assertEqual(trek.description_teaser_en, "Cap")
        self.assertEqual(trek.description_teaser, "Cap")
        self.assertEqual(trek.published, False)
        self.assertEqual(trek.published_fr, True)
        self.assertEqual(trek.published_en, False)
        self.assertEqual(trek.published_it, False)
        self.assertEqual(trek.published_es, False)
        call_command('import', 'geotrek.trekking.tests.test_parsers.TestGeotrek2TrekParser', verbosity=0)
        trek.refresh_from_db()
        self.assertEqual(Trek.objects.count(), 6)
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

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    def test_children_do_not_exist(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids.json'),
                                ('trekking', 'trek.json'),
                                ('trekking', 'trek_children_do_not_exist.json')]

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
        self.mock_json_order = [('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids.json'),
                                ('trekking', 'trek.json'),
                                ('trekking', 'trek_wrong_children.json'), ]

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
        self.mock_json_order = [('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids.json'),
                                ('trekking', 'trek.json'),
                                ('trekking', 'trek_children.json'),
                                ('trekking', 'trek_difficulty.json'),
                                ('trekking', 'trek_route.json'),
                                ('trekking', 'trek_theme.json'),
                                ('trekking', 'trek_practice.json'),
                                ('trekking', 'trek_accessibility.json'),
                                ('trekking', 'trek_network.json'),
                                ('trekking', 'trek_label.json'),
                                ('trekking', 'sources.json'),
                                ('trekking', 'trek_ids_2.json'),
                                ('trekking', 'trek_2.json'),
                                ('trekking', 'trek_children.json')]

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
