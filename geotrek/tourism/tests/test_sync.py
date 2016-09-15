# -*- encoding: UTF-8 -*-

import json
import os
import mock
from zipfile import ZipFile

from django.conf import settings
from django.core import management
from django.test import TestCase
from django.utils import translation

from geotrek.common.factories import RecordSourceFactory, TargetPortalFactory
from geotrek.common.tests import TranslationResetMixin
from geotrek.tourism.factories import (TouristicContentFactory, TouristicEventFactory,
                                       TrekWithTouristicEventFactory, TrekWithTouristicContentFactory)


class SyncTest(TranslationResetMixin, TestCase):
    def setUp(self):
        translation.deactivate()

        self.contents = []
        self.events = []
        self.portals = []

        self.portal_a = TargetPortalFactory()
        self.portal_b = TargetPortalFactory()

        self.source_a = RecordSourceFactory()
        self.source_b = RecordSourceFactory()

        self.content_1 = TouristicContentFactory.create(portals=(self.portal_a, self.portal_b),
                                                        sources=(self.source_a, self.source_b))

        self.content_2 = TouristicContentFactory.create(portals=(self.portal_a,),
                                                        sources=(self.source_a, self.source_b))

        self.event_1 = TouristicEventFactory.create(portals=(self.portal_a, self.portal_b),
                                                    sources=(self.source_b, ))

        self.event_2 = TouristicEventFactory.create(portals=(self.portal_b,),
                                                    sources=(self.source_a, self.source_b))

    def test_sync(self):
        with mock.patch('geotrek.tourism.models.TouristicContent.prepare_map_image'):
            with mock.patch('geotrek.tourism.models.TouristicEvent.prepare_map_image'):
                management.call_command('sync_rando', settings.SYNC_RANDO_ROOT, url='http://localhost:8000',
                                        source=self.source_a.name, skip_tiles=True, skip_pdf=True, verbosity='0')

                with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', 'en', 'touristiccontents.geojson'), 'r') as f:
                    # 2 contents
                    tcontents = json.load(f)
                    self.assertEquals(len(tcontents['features']), 2)

                with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', 'en', 'touristicevents.geojson'), 'r') as f:
                    #  only 1 event
                    tevents = json.load(f)
                    self.assertEquals(len(tevents['features']), 1)

                with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', 'en', 'touristiccategories.json'), 'r') as f:
                    tcategories = json.load(f)
                    self.assertEquals(len(tcategories), 2)

    def test_sync_portal_filtering(self):

        with mock.patch('geotrek.tourism.models.TouristicContent.prepare_map_image'):
            with mock.patch('geotrek.tourism.models.TouristicEvent.prepare_map_image'):
                management.call_command('sync_rando', settings.SYNC_RANDO_ROOT, url='http://localhost:8000',
                                        portal=self.portal_b.name, skip_tiles=True, skip_pdf=True, verbosity='0')

        with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', 'en', 'touristiccontents.geojson'), 'r') as f:
            tcontents = json.load(f)
            # 1 content on portal b
            self.assertEquals(len(tcontents['features']), 1)

        with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', 'en', 'touristicevents.geojson'), 'r') as f:
            tevents = json.load(f)
            # 2 events on portal b
            self.assertEquals(len(tevents['features']), 2)

        with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', 'en', 'touristiccategories.json'), 'r') as f:
            tevents = json.load(f)
            self.assertEquals(len(tevents), 2)

    def test_sync_trek_zip_content(self):
        """
        Test including tevents and tcontents in trek zips
        """

        trek1 = TrekWithTouristicEventFactory.create()
        trek2 = TrekWithTouristicContentFactory.create()

        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando',
                                    settings.SYNC_RANDO_ROOT,
                                    url='http://localhost:8000',
                                    skip_tiles=True,
                                    with_events=True,
                                    skip_profile_png=True,
                                    skip_pdf=True,
                                    skip_dem=True,
                                    content_categories=u"1,2",
                                    verbosity='0')

        for lang in settings.MODELTRANSLATION_LANGUAGES:
            with ZipFile(os.path.join(settings.SYNC_RANDO_ROOT, 'zip', 'treks', lang,
                                      'global.zip'),
                         'r') as zipf:
                file_list = zipf.namelist()

                path_touristevents_geojson = os.path.join('api', lang, 'treks',
                                                          '{pk}'.format(pk=trek1.pk),
                                                          'touristicevents.geojson')
                path_touristcontents_geojson = os.path.join('api', lang, 'treks',
                                                            '{pk}'.format(pk=trek2.pk),
                                                            'touristiccontents.geojson')
                path_touristcategories_json = os.path.join('api', lang,
                                                           'touristiccategories.json')

                self.assertIn(path_touristevents_geojson,
                              file_list,
                              msg=u"Unable to find {file} in {lang}/global.zip".format(file=path_touristevents_geojson,
                                                                                       lang=lang))
                read_content = json.loads(zipf.read(path_touristevents_geojson))
                self.assertIn('features', read_content)

                self.assertIn(path_touristcontents_geojson,
                              file_list,
                              msg=u"Unable to find {file} in {lang}/global.zip".format(file=path_touristcontents_geojson,
                                                                                       lang=lang))
                read_content = json.loads(zipf.read(path_touristcontents_geojson))
                self.assertIn('features', read_content)

                self.assertIn(path_touristcategories_json,
                              file_list,
                              msg=u"Unable to find {file} in {lang}/global.zip".format(file=path_touristcategories_json,
                                                                                       lang=lang))
