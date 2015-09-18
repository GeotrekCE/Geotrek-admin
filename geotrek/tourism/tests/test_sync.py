import os
import json
from django.test import TestCase
from django.core import management
from django.conf import settings
from geotrek.common.factories import RecordSourceFactory
from geotrek.tourism.factories import TouristicContentFactory, TouristicEventFactory


def factory(factory, source):
    obj = factory()
    obj.source = (source, )
    obj.save()


class SyncTest(TestCase):
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
