import os
import json
from landez.sources import DownloadError
import mock
import shutil
from io import BytesIO
import zipfile

from django.test import TestCase
from django.conf import settings
from django.core import management
from django.core.management.base import CommandError
from django.http import HttpResponse, StreamingHttpResponse
from django.test.utils import override_settings

from geotrek.common.factories import RecordSourceFactory, TargetPortalFactory, AttachmentFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_file
from geotrek.infrastructure.factories import InfrastructureFactory
from geotrek.sensitivity.factories import SensitiveAreaFactory
from geotrek.signage.factories import SignageFactory
from geotrek.trekking.factories import TrekFactory, TrekWithPublishedPOIsFactory
from geotrek.trekking import models as trek_models
from geotrek.tourism.factories import InformationDeskFactory, TouristicContentFactory, TouristicEventFactory


class SyncRandoTilesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncRandoTilesTest, cls).setUpClass()

    @mock.patch('landez.TilesManager.tile', return_value='I am a png')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tiles(self, mock_tileslist, mock_tiles):
        output = BytesIO()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                stdout=output)
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.readline(), 'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())

    @mock.patch('landez.TilesManager.tile', return_value='Error')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tile_fail(self, mock_tileslist, mock_tiles):
        mock_tiles.side_effect = DownloadError
        output = BytesIO()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                stdout=output)
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.readline(), 'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())

    @override_settings(MOBILE_TILES_URL=['http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                                         'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'])
    @mock.patch('landez.TilesManager.tile', return_value='Error')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_multiple_tiles(self, mock_tileslist, mock_tiles):
        mock_tiles.side_effect = DownloadError
        output = BytesIO()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                stdout=output)
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.readline(), 'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())

    @override_settings(MOBILE_TILES_URL='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
    @mock.patch('landez.TilesManager.tile', return_value='Error')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tiles_url_str(self, mock_tileslist, mock_tiles):
        mock_tiles.side_effect = DownloadError
        output = BytesIO()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                stdout=output)
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.readline(), 'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('landez.TilesManager.tile', return_value='I am a png')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tiles_with_treks(self, mock_tileslist, mock_tiles, mock_prepare):
        output = BytesIO()
        trek = TrekFactory.create(published=True)
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                stdout=output)
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.readline(), 'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())
        zfile_trek = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', '{pk}.zip'.format(pk=trek.pk)))
        for finfo in zfile_trek.infolist():
            ifile_trek = zfile_trek.open(finfo)
            self.assertEqual(ifile_trek.readline(), 'I am a png')
        self.assertIn("zip/tiles/{pk}.zip".format(pk=trek.pk), output.getvalue())

    def tearDown(self):
        shutil.rmtree(os.path.join('var', 'tmp'))


class SyncRandoFailTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncRandoFailTest, cls).setUpClass()

    def test_fail_directory_not_empty(self):
        os.makedirs(os.path.join('var', 'tmp', 'other'))
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2)
        self.assertEqual(e.exception.message, "Destination directory contains extra data")
        shutil.rmtree(os.path.join('var', 'tmp', 'other'))

    def test_fail_url_ftp(self):
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='ftp://localhost:8000',
                                    skip_tiles=True, verbosity=2)
        self.assertIn("url parameter should start with http:// or https://", e.exception.message)

    def test_language_not_in_db(self):
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, languages='cat', verbosity=2)
        self.assertEqual(e.exception.message,
                         "Language cat doesn't exist. Select in these one : ('en', 'es', 'fr', 'it')")

    def test_attachments_missing_from_disk(self):
        trek_1 = TrekWithPublishedPOIsFactory.create(published_fr=True)
        attachment = AttachmentFactory(content_object=trek_1, attachment_file=get_dummy_uploaded_image())
        os.remove(attachment.attachment_file.path)
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=BytesIO())
        self.assertEqual(e.exception.message, 'Some errors raised during synchronization.')
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'mobile', 'nolang', 'media', 'trekking_trek')))

    @mock.patch('geotrek.trekking.views.TrekViewSet.list')
    def test_response_500(self, mocke):
        output = BytesIO()
        mocke.return_value = HttpResponse(status=500)
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2, stdout=output)
        self.assertEqual(e.exception.message, 'Some errors raised during synchronization.')
        self.assertIn("failed (HTTP 500)", output.getvalue())

    @override_settings(MEDIA_URL=9)
    def test_bad_settings(self):
        output = BytesIO()
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaises(AttributeError) as e:
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=output)
        self.assertEqual(e.exception.message, "'int' object has no attribute 'strip'")
        self.assertIn("Exception raised in callable attribute", output.getvalue())

    @classmethod
    def tearDownClass(cls):
        super(SyncRandoFailTest, cls).tearDownClass()
        shutil.rmtree(os.path.join('var', 'tmp'))


class SyncTest(TestCase):
    def setUp(self):
        self.source_a = RecordSourceFactory()
        self.source_b = RecordSourceFactory()

        self.portal_a = TargetPortalFactory()
        self.portal_b = TargetPortalFactory()
        information_desks = InformationDeskFactory.create()
        self.trek_1 = TrekWithPublishedPOIsFactory.create(sources=(self.source_a, ),
                                                          portals=(self.portal_b,),
                                                          published=True)
        self.trek_1.information_desks.add(information_desks)
        self.attachment_1 = AttachmentFactory.create(content_object=self.trek_1,
                                                     attachment_file=get_dummy_uploaded_image())
        self.trek_2 = TrekFactory.create(sources=(self.source_b,),
                                         published=True)
        self.trek_3 = TrekFactory.create(portals=(self.portal_b,
                                                  self.portal_a),
                                         published=True)
        self.trek_4 = TrekFactory.create(portals=(self.portal_a,),
                                         published=True)

        self.poi_1 = trek_models.POI.objects.first()
        self.attachment_poi_image_1 = AttachmentFactory.create(content_object=self.poi_1,
                                                               attachment_file=get_dummy_uploaded_image())
        self.attachment_poi_image_2 = AttachmentFactory.create(content_object=self.poi_1,
                                                               attachment_file=get_dummy_uploaded_image())
        self.attachment_poi_file = AttachmentFactory.create(content_object=self.poi_1,
                                                            attachment_file=get_dummy_uploaded_file())

        infrastructure = InfrastructureFactory.create(no_path=True, name="INFRA_1")
        infrastructure.add_path(self.trek_1.paths.first(), start=0, end=0)
        signage = SignageFactory.create(no_path=True, name="SIGNA_1")
        signage.add_path(self.trek_1.paths.first(), start=0, end=0)
        SensitiveAreaFactory.create(published=True)
        self.touristic_content = TouristicContentFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        self.touristic_event = TouristicEventFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        self.attachment_touristic_content = AttachmentFactory.create(content_object=self.touristic_content,
                                                                     attachment_file=get_dummy_uploaded_image())
        self.attachment_touristic_event = AttachmentFactory.create(content_object=self.touristic_event,
                                                                   attachment_file=get_dummy_uploaded_image())

    def test_sync(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True, with_infrastructures=True,
                                    with_events=True, content_categories="1", url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
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
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # \u2028 is translated to \n
                self.assertEquals(treks['features'][0]['properties']['description'], u'toto\ntata')

    @mock.patch('geotrek.trekking.views.TrekViewSet.list')
    def test_streaminghttpresponse(self, mocke):
        output = BytesIO()
        mocke.return_value = StreamingHttpResponse()
        trek = TrekWithPublishedPOIsFactory.create(published_fr=True)
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_pdf=True, skip_tiles=True, verbosity=2, stdout=output)
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'fr', 'treks', str(trek.pk), 'profile.png')))

    def test_sync_filtering_sources(self):
        # source A only
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    source=self.source_a.name, skip_tiles=True, skip_pdf=True, verbosity=2,
                                    stdout=BytesIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # only 1 trek in Source A
                self.assertEquals(len(treks['features']),
                                  trek_models.Trek.objects.filter(published=True,
                                                                  source__name__in=[self.source_a.name, ]).count())

    def test_sync_filtering_portals(self):
        # portal B only
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    portal=self.portal_b.name, skip_tiles=True, skip_pdf=True, verbosity=2,
                                    stdout=BytesIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)

                # only 2 treks in Portal B + 1 without portal specified
                self.assertEquals(len(treks['features']), 3)

        # portal A and B
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    portal='{},{}'.format(self.portal_a.name, self.portal_b.name),
                                    skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)

                # 4 treks have portal A or B or no portal
                self.assertEquals(len(treks['features']), 4)

    def tearDown(self):
        shutil.rmtree(os.path.join('var', 'tmp'))
