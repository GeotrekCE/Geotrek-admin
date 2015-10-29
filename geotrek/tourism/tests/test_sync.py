# -*- encoding: UTF-8 -*-

import json
import os
from zipfile import ZipFile

from django.conf import settings
from django.core import management
from django.test import TestCase

from geotrek.common.factories import RecordSourceFactory
from geotrek.common.tests import TranslationResetMixin
from geotrek.tourism.factories import (TouristicContentFactory, TouristicEventFactory,
                                       TrekWithTouristicEventFactory, TrekWithTouristicContentFactory)


def factory(factory, source):
    obj = factory()
    obj.source = (source, )
    obj.save()


class SyncTest(TranslationResetMixin, TestCase):
    def test_sync(self):
        source_a = RecordSourceFactory(name='A')
        source_b = RecordSourceFactory(name='B')
        factory(TouristicContentFactory, source_a)
        factory(TouristicContentFactory, source_b)
        factory(TouristicEventFactory, source_a)
        factory(TouristicEventFactory, source_b)
        management.call_command('sync_rando', settings.SYNC_RANDO_ROOT, url='http://localhost:8000', source='A', skip_tiles=True, verbosity='0')

        with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', 'en', 'touristiccontents.geojson'), 'r') as f:
            tcontents = json.load(f)
        self.assertEquals(len(tcontents['features']), 1)

        with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', 'en', 'touristicevents.geojson'), 'r') as f:
            tevents = json.load(f)
        self.assertEquals(len(tevents['features']), 1)

        with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', 'en', 'touristiccontentcategories.json'), 'r') as f:
            tevents = json.load(f)
            self.assertEquals(len(tevents), 2)

    def test_sync_trek_zip_content(self):
        """
        Test including tevents and tcontents in trek zips
        """

        trek1 = TrekWithTouristicEventFactory.create()
        trek2 = TrekWithTouristicContentFactory.create()

        management.call_command('sync_rando',
                                settings.SYNC_RANDO_ROOT,
                                url='http://localhost:8000',
                                skip_tiles=True,
                                with_events=True,
                                content_categories=u"1,2",
                                verbosity='0')

        with ZipFile(os.path.join(settings.SYNC_RANDO_ROOT, 'zip', 'treks', 'fr',
                                  'global.zip'),
                     'r') as zipf:
            self.assertIn(os.path.join('api', 'fr', 'treks',
                                       '{pk}'.format(pk=trek1.pk),
                                       'touristicevents.geojson'),
                          zipf.namelist())
            self.assertIn(os.path.join('api', 'fr', 'treks',
                                       '{pk}'.format(pk=trek2.pk),
                                       'touristiccontents.geojson'),
                          zipf.namelist())
            self.assertIn(os.path.join('api', 'fr',
                                       'touristiccontentcategories.json'),
                          zipf.namelist())
