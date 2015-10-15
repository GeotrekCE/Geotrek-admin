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
from geotrek.trekking.models import Trek


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

        # test with including tevents and tcontents in trek zips
        source_c = RecordSourceFactory(name='C')
        source_d = RecordSourceFactory(name='D')
        factory(TrekWithTouristicEventFactory, source_c)
        factory(TrekWithTouristicContentFactory, source_d)

        management.call_command('sync_rando',
                                settings.SYNC_RANDO_ROOT,
                                url='http://localhost:8000',
                                source='A',
                                skip_tiles=True,
                                whith_events=True,
                                content_catgories=u"Restaurants,Musée",
                                verbosity='0')

        with ZipFile.open(os.path.join(settings.SYNC_RANDO_ROOT, 'zip', 'treks', 'en',
                                       '{pk}.zip'.format(pk=Trek.objects.existing().filter(published=True)[0])),
                          'r') as zipf:
            raise Exception(u"{}".format(zipf.namelist()))

