import os
import json
from landez.sources import DownloadError
import mock
import shutil
from io import BytesIO
import zipfile

from django.test import TestCase
from django.core import management

from geotrek.common.factories import RecordSourceFactory, TargetPortalFactory
from geotrek.trekking.factories import TrekFactory
from geotrek.trekking import models as trek_models


class SyncRandoTilesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncRandoTilesTest, cls).setUpClass()

    @mock.patch('landez.TilesManager.tile', return_value='I am a png')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tiles(self, mock_tileslist, mock_tiles):
        output = BytesIO()
        management.call_command('sync_rando', 'tmp', url='http://localhost:8000', verbosity=2, stdout=output)
        zfile = zipfile.ZipFile(os.path.join('tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.readline(), 'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())

    @mock.patch('landez.TilesManager.tile', return_value='Error')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tile_fail(self, mock_tileslist, mock_tiles):
        mock_tiles.side_effect = DownloadError
        output = BytesIO()
        management.call_command('sync_rando', 'tmp', url='http://localhost:8000', verbosity=2, stdout=output)
        zfile = zipfile.ZipFile(os.path.join('tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.readline(), 'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())


class SyncTest(TestCase):
    def setUp(self):
        self.source_a = RecordSourceFactory()
        self.source_b = RecordSourceFactory()

        self.portal_a = TargetPortalFactory()
        self.portal_b = TargetPortalFactory()

        self.trek_1 = TrekFactory.create(sources=(self.source_a, ),
                                         portals=(self.portal_b,),
                                         published=True)
        self.trek_2 = TrekFactory.create(sources=(self.source_b,),
                                         published=True)
        self.trek_3 = TrekFactory.create(portals=(self.portal_b,
                                                  self.portal_a),
                                         published=True)
        self.trek_4 = TrekFactory.create(portals=(self.portal_a,),
                                         published=True)

    def test_sync(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, verbosity=0)
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # there are 4 treks
                self.assertEquals(len(treks['features']),
                                  trek_models.Trek.objects.filter(published=True).count())

    def test_sync_2028(self):
        self.trek_1.description = u'toto\u2028tata'
        self.trek_1.save()
        self.trek_2.delete()
        self.trek_3.delete()
        self.trek_4.delete()
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, verbosity=0)
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # \u2028 is translated to \n
                self.assertEquals(treks['features'][0]['properties']['description'], u'toto\ntata')

    def test_sync_filtering_sources(self):
        # source A only
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    source=self.source_a.name, skip_tiles=True, skip_pdf=True, verbosity=0)
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # only 1 trek in Source A
                self.assertEquals(len(treks['features']),
                                  trek_models.Trek.objects.filter(published=True,
                                                                  source__name__in=[self.source_a.name, ]).count())

    def test_sync_filtering_portals(self):
        # portal B only
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    portal=self.portal_b.name, skip_tiles=True, skip_pdf=True, verbosity=0)
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)

                # only 2 treks in Portal B + 1 without portal specified
                self.assertEquals(len(treks['features']), 3)

        # portal A and B
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    portal='{},{}'.format(self.portal_a.name, self.portal_b.name),
                                    skip_tiles=True, skip_pdf=True, verbosity=0)
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)

                # 4 treks have portal A or B or no portal
                self.assertEquals(len(treks['features']), 4)

    def tearDown(self):
        shutil.rmtree('tmp')
