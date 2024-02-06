
from unittest import mock, skipIf

from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.common.models import Attachment, FileType
from geotrek.common.tests.mixins import GeotrekParserTestMixin
from geotrek.outdoor.models import Practice, Rating, RatingScale, Sector, Site
from geotrek.outdoor.parsers import GeotrekSiteParser


class TestGeotrekSiteParser(GeotrekSiteParser):
    url = "https://test.fr"
    provider = 'geotrek1'
    field_options = {
        'type': {'create': True, },
        'themes': {'create': True},
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
        self.mock_json_order = [('outdoor', 'theme.json'),
                                ('outdoor', 'outdoor_sitetype.json'),
                                ('outdoor', 'label.json'),
                                ('outdoor', 'source.json'),
                                ('outdoor', 'organism.json'),
                                ('outdoor', 'structure.json'),
                                ('outdoor', 'outdoor_sector.json'),
                                ('outdoor', 'outdoor_practice.json'),
                                ('outdoor', 'outdoor_ratingscale.json'),
                                ('outdoor', 'outdoor_rating.json'),
                                ('outdoor', 'outdoor_site_ids.json'),
                                ('outdoor', 'outdoor_site.json')]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.outdoor.tests.test_parsers.TestGeotrekSiteParser', verbosity=0)
        self.assertEqual(Site.objects.count(), 6)
        self.assertEqual(Sector.objects.count(), 2)
        self.assertEqual(RatingScale.objects.count(), 1)
        self.assertEqual(Rating.objects.count(), 3)
        self.assertEqual(Practice.objects.count(), 1)
        site = Site.objects.get(name_fr="Racine", name_en="Root")
        # TODO : all the ones that are commented do not work
        self.assertEqual(site.published, True)
        self.assertEqual(site.published_fr, True)
        self.assertEqual(site.published_en, True)
        self.assertEqual(site.published_it, False)
        self.assertEqual(site.published_es, False)
        self.assertEqual(str(site.practice.sector), 'Vertical')
        self.assertEqual(str(site.practice), 'Escalade')
        self.assertEqual(str(site.labels.first()), 'Label fr')
        self.assertEqual(site.ratings.count(), 3)
        self.assertEqual(str(site.ratings.first()), 'Cotation : 3+')
        self.assertEqual(site.ratings.first().description, 'Une description')
        self.assertEqual(site.ratings.first().order, 302)
        self.assertEqual(site.ratings.first().color, '#D9D9D8')
        self.assertEqual(str(site.ratings.first().scale), 'Cotation (Escalade)')
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
        self.assertEqual(site.wind, ['N', 'E'])
        self.assertEqual(str(site.structure), 'Test structure')
        # self.assertEqual(site.information_desks.count(), 1)
        # self.assertEqual(site.weblink.count(), 1)
        # self.assertEqual(site.excluded_pois.count(), 1)
        self.assertEqual(site.eid, "57a8fb52-213d-4dce-8224-bc997f892aae")
        self.assertEqual(Attachment.objects.filter(object_id=site.pk).count(), 1)
        attachment = Attachment.objects.filter(object_id=site.pk).first()
        self.assertIsNotNone(attachment.attachment_file.url)
        self.assertEqual(attachment.legend, 'Arrien-en-Bethmale, vue du village')
        child_site = Site.objects.get(name_fr="Noeud 1", name_en="Node")
        self.assertEqual(child_site.parent, site)
