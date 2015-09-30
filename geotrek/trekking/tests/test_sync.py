import os
import json
from django.test import TestCase
from django.core import management
from django.conf import settings
from geotrek.common.factories import RecordSourceFactory
from geotrek.trekking.factories import TrekFactory


def factory(factory, source):
    obj = factory()
    obj.source = (source, )
    obj.save()


class SyncTest(TestCase):
    def test_sync(self):
        source_a = RecordSourceFactory(name='A')
        source_b = RecordSourceFactory(name='B')
        factory(TrekFactory, source_a)
        factory(TrekFactory, source_b)
        management.call_command('sync_rando', settings.SYNC_RANDO_ROOT, url='http://localhost:8000', source='A', skip_tiles=True, verbosity='0')
        with open(os.path.join(settings.SYNC_RANDO_ROOT, 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)
        self.assertEquals(len(treks['features']), 1)
