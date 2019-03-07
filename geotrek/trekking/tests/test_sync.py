import os
import json
from landez.sources import DownloadError
import mock
import shutil
from io import BytesIO
import zipfile

from django.test import TestCase
from django.core import management
from django.core.management.base import CommandError

from geotrek.common.factories import RecordSourceFactory, TargetPortalFactory, AttachmentFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.trekking.factories import TrekFactory, TrekWithPublishedPOIsFactory
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


class SyncRandoFailTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncRandoFailTest, cls).setUpClass()

    def test_fail_directory_not_empty(self):
        os.makedirs(os.path.join('tmp', 'other'))
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2)
        self.assertEqual(e.exception.message, "Destination directory contains extra data")
        shutil.rmtree(os.path.join('tmp', 'other'))

    def test_fail_url_ftp(self):
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', 'tmp', url='ftp://localhost:8000',
                                    skip_tiles=True, verbosity=2)
        self.assertEqual(e.exception.message, "url parameter should start with http:// or https://")

    def test_language_not_in_db(self):
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    skip_tiles=True, languages='cat', verbosity=2)
        self.assertEqual(e.exception.message,
                         "Language cat doesn't exist. Select in these one : ('en', 'es', 'fr', 'it')")

    def test_attachments_missing_from_disk(self):
        trek_1 = TrekWithPublishedPOIsFactory.create(published_fr=True)
        attachment = AttachmentFactory(content_object=trek_1, attachment_file=get_dummy_uploaded_image())
        os.remove(attachment.attachment_file.path)
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=BytesIO())
        self.assertEqual(e.exception.message, 'Some errors raised during synchronization.')
        self.assertFalse(os.path.exists(os.path.join('tmp', 'mobile', 'nolang', 'media', 'trekking_trek')))

    @classmethod
    def tearDownClass(cls):
        super(SyncRandoFailTest, cls).tearDownClass()
        shutil.rmtree('tmp')


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
                                    skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
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
                                    skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # \u2028 is translated to \n
                self.assertEquals(treks['features'][0]['properties']['description'], u'toto\ntata')

    def test_sync_filtering_sources(self):
        # source A only
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    source=self.source_a.name, skip_tiles=True, skip_pdf=True, verbosity=2,
                                    stdout=BytesIO())
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
                                    portal=self.portal_b.name, skip_tiles=True, skip_pdf=True, verbosity=2,
                                    sdtout=BytesIO())
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)

                # only 2 treks in Portal B + 1 without portal specified
                self.assertEquals(len(treks['features']), 3)

        # portal A and B
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    portal='{},{}'.format(self.portal_a.name, self.portal_b.name),
                                    skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
            with open(os.path.join('tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)

                # 4 treks have portal A or B or no portal
                self.assertEquals(len(treks['features']), 4)

    def tearDown(self):
        shutil.rmtree('tmp')
