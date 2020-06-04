import errno
import os
import json
from landez.sources import DownloadError
from unittest import mock
import shutil
from io import StringIO
import zipfile

from django.test import TestCase
from django.contrib.gis.geos import LineString
from django.core import management
from django.core.management.base import CommandError
from django.http import HttpResponse
from django.test.utils import override_settings

from geotrek.common.factories import FileTypeFactory, RecordSourceFactory, TargetPortalFactory, AttachmentFactory, ThemeFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.core.factories import PathFactory
from geotrek.trekking.factories import TrekFactory, TrekWithPublishedPOIsFactory
from geotrek.trekking import models as trekking_models


class VarTmpTestCase(TestCase):
    def setUp(self):
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        if os.path.exists(os.path.join('var', 'tmp')):
            shutil.rmtree(os.path.join('var', 'tmp'))

    def tearDown(self):
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        if os.path.exists(os.path.join('var', 'tmp')):
            shutil.rmtree(os.path.join('var', 'tmp'))


class SyncRandoTilesTest(VarTmpTestCase):
    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('landez.TilesManager.tile', return_value=b'I am a png')
    def test_tiles(self, mock_tileslist, mock_tiles):
        output = StringIO()

        p = PathFactory.create(geom=LineString((0, 0), (0, 10)))
        trek_multi = TrekFactory.create(published=True, paths=[(p, 0, 0.1), (p, 0.2, 0.3)])
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                languages='en', stdout=output)
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile_global = zfile.open(finfo)
            if ifile_global.name.startswith('tiles/'):
                self.assertEqual(ifile_global.readline(), b'I am a png')
        zfile_trek = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', '{}.zip'.format(trek_multi.pk)))
        for finfo in zfile_trek.infolist():
            ifile_trek = zfile_trek.open(finfo)
            if ifile_trek.name.startswith('tiles/'):
                self.assertEqual(ifile_trek.readline(), b'I am a png')
        self.assertIn("tiles/global.zip", output.getvalue())
        self.assertIn("tiles/{pk}.zip".format(pk=trek_multi.pk), output.getvalue())

    @mock.patch('landez.TilesManager.tile', return_value='Error')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tile_fail(self, mock_tileslist, mock_tiles):
        mock_tiles.side_effect = DownloadError
        output = StringIO()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                languages='en', stdout=output)
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.read(), b'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())

    @override_settings(MOBILE_TILES_URL=['http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                                         'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'])
    @mock.patch('landez.TilesManager.tile', return_value='Error')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_multiple_tiles(self, mock_tileslist, mock_tiles):
        mock_tiles.side_effect = DownloadError
        output = StringIO()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                languages='en', stdout=output)
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.read(), b'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())

    @override_settings(MOBILE_TILES_URL='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
    @mock.patch('landez.TilesManager.tile', return_value='Error')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tiles_url_str(self, mock_tileslist, mock_tiles):
        mock_tiles.side_effect = DownloadError
        output = StringIO()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                languages='en', stdout=output)
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.read(), b'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('landez.TilesManager.tile', return_value=b'I am a png')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tiles_with_treks(self, mock_tileslist, mock_tiles, mock_prepare):
        output = StringIO()
        trek = TrekFactory.create(published=True)
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                languages='en', stdout=output)
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.read(), b'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())
        zfile_trek = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', '{pk}.zip'.format(pk=trek.pk)))
        for finfo in zfile_trek.infolist():
            ifile_trek = zfile_trek.open(finfo)
            self.assertEqual(ifile_trek.read(), b'I am a png')
        self.assertIn("zip/tiles/{pk}.zip".format(pk=trek.pk), output.getvalue())

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('landez.TilesManager.tile', return_value=b'I am a png')
    @mock.patch('landez.TilesManager.tileslist', return_value=[(9, 258, 199)])
    def test_tiles_with_treks_source_portal(self, mock_tileslist, mock_tiles, mock_prepare):
        output = StringIO()
        self.source = RecordSourceFactory()
        self.portal = TargetPortalFactory()
        trek = TrekFactory.create(published=True, sources=(self.source,), portals=(self.portal,))
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                source=self.source.name, portal=self.portal.name, languages='fr',
                                verbosity=2, stdout=output, stderr=StringIO())
        zfile = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.read(), b'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())
        zfile_trek = zipfile.ZipFile(os.path.join('var', 'tmp', 'zip', 'tiles', '{pk}.zip'.format(pk=trek.pk)))
        for finfo in zfile_trek.infolist():
            ifile_trek = zfile_trek.open(finfo)
            self.assertEqual(ifile_trek.read(), b'I am a png')
        self.assertIn("zip/tiles/{pk}.zip".format(pk=trek.pk), output.getvalue())


class SyncRandoFailTest(VarTmpTestCase):
    def test_fail_directory_not_empty(self):
        os.makedirs(os.path.join('var', 'tmp', 'other'))
        with self.assertRaisesRegex(CommandError, "Destination directory contains extra data"):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2)

    def test_fail_url_ftp(self):
        with self.assertRaisesRegex(CommandError, "url parameter should start with http:// or https://"):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='ftp://localhost:8000',
                                    skip_tiles=True, languages='en', verbosity=2)

    def test_language_not_in_db(self):
        with self.assertRaisesRegex(CommandError,
                                    r"Language cat doesn't exist. Select in these one : \('en', 'es', 'fr', 'it'\)"):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, languages='cat', verbosity=2)

    def test_attachments_missing_from_disk(self):
        trek_1 = TrekWithPublishedPOIsFactory.create(published_fr=True)
        attachment = AttachmentFactory(content_object=trek_1, attachment_file=get_dummy_uploaded_image())
        os.remove(attachment.attachment_file.path)
        with self.assertRaisesRegex(CommandError, 'Some errors raised during synchronization.'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=StringIO(), stderr=StringIO())
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'mobile', 'nolang', 'media', 'trekking_trek')))

    def test_fail_sync_already_running(self):
        os.makedirs(os.path.join('var', 'tmp_sync_rando'))
        msg = "The var/tmp_sync_rando/ directory already exists. " \
              "Please check no other sync_rando command is already running. " \
              "If not, please delete this directory."
        with self.assertRaisesRegex(CommandError, msg):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2)

    @mock.patch('os.mkdir')
    def test_fail_sync_tmp_sync_rando_permission_denied(self, mkdir):
        mkdir.side_effect = OSError(errno.EACCES, 'Permission Denied')
        with self.assertRaisesRegex(OSError, r'\[Errno 13\] Permission Denied'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2)

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('geotrek.trekking.views.TrekViewSet.as_view')
    def test_response_500(self, mock_view, mocke_map_image):
        error = StringIO()
        mock_view.return_value.return_value = HttpResponse(status=500)
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaisesRegex(CommandError, 'Some errors raised during synchronization.'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2, stdout=StringIO(), stderr=error)
        self.assertIn("failed (HTTP 500)", error.getvalue())

    @mock.patch('geotrek.trekking.views.TrekViewSet.list')
    def test_response_view_exception(self, mocke):
        output = StringIO()
        mocke.side_effect = Exception('This is a test')
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaisesRegex(CommandError, 'Some errors raised during synchronization.'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    portal='portal', skip_pdf=True,
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=output)
        self.assertIn("failed (This is a test)", output.getvalue())

    @override_settings(DEBUG=True)
    @mock.patch('geotrek.trekking.views.TrekViewSet.list')
    def test_response_view_exception_with_debug(self, mocke):
        output = StringIO()
        mocke.side_effect = ValueError('This is a test')
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaisesRegex(ValueError, 'This is a test'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    portal='portal', skip_pdf=True,
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=output)
        self.assertIn("failed (This is a test)", output.getvalue())

    @override_settings(MEDIA_URL=9)
    def test_bad_settings(self):
        output = StringIO()
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaisesRegex(AttributeError, "'int' object has no attribute 'strip'"):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=output)
        self.assertIn("failed (Cannot mix str and non-str arguments)", output.getvalue())

    def test_sync_fail_src_file_not_exist(self):
        output = StringIO()
        theme = ThemeFactory.create()
        theme.pictogram = "other"
        theme.save()
        with self.assertRaisesRegex(CommandError, 'Some errors raised during synchronization.'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=output, stderr=StringIO())
        self.assertIn("file does not exist", output.getvalue())


class SyncTest(VarTmpTestCase):
    def setUp(self):
        super().setUp()
        self.trek = TrekWithPublishedPOIsFactory.create(published=True)

    def test_sync_multiple_time(self):
        management.call_command('sync_rando', 'var/tmp', url='http://localhost:8000', skip_tiles=True, languages='en',
                                skip_pdf=True, verbosity=2, stdout=StringIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)

            # only 2 treks in Portal B + 1 without portal specified
            self.assertEqual(len(treks['features']), 1)

        # portal A and B
        output = StringIO()
        management.call_command('sync_rando', 'var/tmp', url='http://localhost:8000', skip_tiles=True, languages='en',
                                skip_pdf=True, verbosity=2, stdout=output)
        self.assertIn("unchanged", output.getvalue())

    @override_settings(THUMBNAIL_COPYRIGHT_FORMAT='*' * 300)
    def test_sync_pictures_long_title_legend_author(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, skip_dem=True, skip_profile_png=True,
                                    languages='en', verbosity=2, stdout=StringIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                self.assertEqual(len(treks['features']),
                                 trekking_models.Trek.objects.filter(published=True).count())

    def test_sync_2028(self):
        self.trek.description = 'toto\u2028tata'
        self.trek.save()

        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, skip_dem=True, skip_profile_png=True,
                                    languages='en', verbosity=2, stdout=StringIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # \u2028 is translated to \n
                self.assertEqual(treks['features'][0]['properties']['description'], 'toto\ntata')

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @override_settings(ONLY_EXTERNAL_PUBLIC_PDF=True)
    def test_only_external_public_pdf(self, trek):
        output = StringIO()
        trek = TrekFactory.create(published=True, )
        filetype_topoguide = FileTypeFactory.create(type='Topoguide')
        AttachmentFactory.create(content_object=trek, attachment_file=get_dummy_uploaded_image(),
                                 filetype=filetype_topoguide)
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                skip_pdf=False, skip_tiles=True, stdout=output)
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek.pk), '%s.pdf' % self.trek.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(trek.pk), '%s.pdf' % trek.slug)))
