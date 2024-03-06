import errno
import os
import json
from landez.sources import DownloadError
from unittest import mock
import shutil
from io import StringIO
import zipfile

from django.conf import settings
from django.test import TestCase
from django.contrib.gis.geos import LineString
from django.core import management
from django.core.management.base import CommandError
from django.http import HttpResponse, StreamingHttpResponse
from django.test.utils import override_settings

from geotrek.common.tests.factories import FileTypeFactory, RecordSourceFactory, TargetPortalFactory, AttachmentFactory, ThemeFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.core.tests.factories import PathFactory
from geotrek.infrastructure.tests.factories import InfrastructureFactory
from geotrek.sensitivity.tests.factories import SensitiveAreaFactory, SportPracticeFactory
from geotrek.signage.tests.factories import SignageFactory
from geotrek.tourism.tests.factories import InformationDeskFactory, TouristicContentFactory, TouristicEventFactory
from geotrek.trekking.tests.factories import TrekFactory, TrekWithPublishedPOIsFactory
from geotrek.trekking import models as trekking_models


class VarTmpTestCase(TestCase):
    def setUp(self):
        if os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync')):
            shutil.rmtree(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'))

    def tearDown(self):
        if os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync')):
            shutil.rmtree(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'))


class SyncRandoTilesTest(VarTmpTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando')):
            shutil.rmtree(os.path.join(settings.TMP_DIR, 'sync_rando'))

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('landez.TilesManager.tile', return_value=b'I am a png')
    def test_tiles(self, mock_tileslist, mock_tiles):
        output = StringIO()

        p = PathFactory.create(geom=LineString((0, 0), (0, 10)))
        trek_multi = TrekFactory.create(published=True, paths=[(p, 0, 0.1), (p, 0.2, 0.3)])
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000', verbosity=2,
                                languages='en', stdout=output)
        zfile = zipfile.ZipFile(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile_global = zfile.open(finfo)
            if ifile_global.name.startswith('tiles/'):
                self.assertEqual(ifile_global.readline(), b'I am a png')
        zfile_trek = zipfile.ZipFile(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'zip', 'tiles', '{}.zip'.format(trek_multi.pk)))
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
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000', verbosity=2,
                                languages='en', stdout=output)
        zfile = zipfile.ZipFile(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'zip', 'tiles', 'global.zip'))
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
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000', verbosity=2,
                                languages='en', stdout=output)
        zfile = zipfile.ZipFile(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'zip', 'tiles', 'global.zip'))
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
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000', verbosity=2,
                                languages='en', stdout=output)
        zfile = zipfile.ZipFile(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'zip', 'tiles', 'global.zip'))
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
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000', verbosity=2,
                                languages='en', stdout=output)
        zfile = zipfile.ZipFile(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.read(), b'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())
        zfile_trek = zipfile.ZipFile(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'zip', 'tiles', '{pk}.zip'.format(pk=trek.pk)))
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
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                source=self.source.name, portal=self.portal.name, languages='fr',
                                verbosity=2, stdout=output, stderr=StringIO())
        zfile = zipfile.ZipFile(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'zip', 'tiles', 'global.zip'))
        for finfo in zfile.infolist():
            ifile = zfile.open(finfo)
            self.assertEqual(ifile.read(), b'I am a png')
        self.assertIn("zip/tiles/global.zip", output.getvalue())
        zfile_trek = zipfile.ZipFile(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'zip', 'tiles', '{pk}.zip'.format(pk=trek.pk)))
        for finfo in zfile_trek.infolist():
            ifile_trek = zfile_trek.open(finfo)
            self.assertEqual(ifile_trek.read(), b'I am a png')
        self.assertIn("zip/tiles/{pk}.zip".format(pk=trek.pk), output.getvalue())


class SyncRandoFailTest(VarTmpTestCase):
    def test_fail_directory_not_empty(self):
        os.makedirs(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'other'))
        with self.assertRaisesRegex(CommandError, "Destination directory contains extra data"):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2)

    def test_fail_url_ftp(self):
        with self.assertRaisesRegex(CommandError, "url parameter should start with http:// or https://"):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='ftp://localhost:8000',
                                    skip_tiles=True, languages='en', verbosity=2)

    def test_language_not_in_db(self):
        with self.assertRaisesRegex(CommandError,
                                    r"Language cat doesn't exist. Select in these one : \['en', 'es', 'fr', 'it'\]"):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                    skip_tiles=True, languages='cat', verbosity=2)

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    def test_attachments_missing_from_disk(self, mocke):
        mocke.side_effect = Exception()
        trek_1 = TrekWithPublishedPOIsFactory.create(published_fr=True)
        attachment = AttachmentFactory(content_object=trek_1, attachment_file=get_dummy_uploaded_image())
        os.remove(attachment.attachment_file.path)
        with self.assertRaisesRegex(CommandError, 'Some errors raised during synchronization.'):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=StringIO(), stderr=StringIO())
        self.assertFalse(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'mobile', 'nolang', 'media', 'trekking_trek')))

    @mock.patch('os.mkdir')
    def test_fail_sync_permission_denied(self, mkdir):
        mkdir.side_effect = OSError(errno.EACCES, 'Permission Denied')
        with self.assertRaisesRegex(OSError, r'\[Errno 13\] Permission Denied'):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2)

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('geotrek.trekking.views.TrekAPIViewSet.as_view')
    def test_response_500(self, mock_view, mocke_map_image):
        error = StringIO()
        mock_view.return_value.return_value = HttpResponse(status=500)
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaisesRegex(CommandError, 'Some errors raised during synchronization.'):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                    skip_tiles=True, verbosity=2, stdout=StringIO(), stderr=error)
        self.assertIn("failed (HTTP 500)", error.getvalue())

    @mock.patch('geotrek.trekking.views.TrekAPIViewSet.list')
    def test_response_view_exception(self, mocke):
        output = StringIO()
        mocke.side_effect = Exception('This is a test')
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaisesRegex(CommandError, 'Some errors raised during synchronization.'):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                    portal='portal', skip_pdf=True,
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=output)
        self.assertIn("failed (This is a test)", output.getvalue())

    @override_settings(DEBUG=True)
    @mock.patch('geotrek.trekking.views.TrekAPIViewSet.list')
    def test_response_view_exception_with_debug(self, mocke):
        output = StringIO()
        mocke.side_effect = ValueError('This is a test')
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaisesRegex(ValueError, 'This is a test'):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                    portal='portal', skip_pdf=True,
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=output)
        self.assertIn("failed (This is a test)", output.getvalue())

    def test_sync_fail_src_file_not_exist(self):
        output = StringIO()
        theme = ThemeFactory.create()
        theme.pictogram = "other"
        theme.save()
        with self.assertRaisesRegex(CommandError, 'Some errors raised during synchronization.'):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=output, stderr=StringIO())
        self.assertIn("file does not exist", output.getvalue())


class SyncTest(VarTmpTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trek = TrekWithPublishedPOIsFactory.create(published=True)

    def test_sync_multiple_time(self):
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000', skip_tiles=True, languages='en',
                                skip_pdf=True, verbosity=2, stdout=StringIO())
        with open(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)

            # only 2 treks in Portal B + 1 without portal specified
            self.assertEqual(len(treks['features']), 1)

        # portal A and B
        output = StringIO()
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000', skip_tiles=True, languages='en',
                                skip_pdf=True, verbosity=2, stdout=output)
        self.assertIn("unchanged", output.getvalue())

    @override_settings(THUMBNAIL_COPYRIGHT_FORMAT='*' * 300)
    def test_sync_pictures_long_title_legend_author(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, skip_dem=True, skip_profile_png=True,
                                    languages='en', verbosity=2, stdout=StringIO())
            with open(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                self.assertEqual(len(treks['features']),
                                 trekking_models.Trek.objects.filter(published=True).count())

    def test_sync_2028(self):
        old_description = self.trek.description
        self.trek.description = 'toto\u2028tata'
        self.trek.save()

        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, skip_dem=True, skip_profile_png=True,
                                    languages='en', verbosity=2, stdout=StringIO())
            with open(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # \u2028 is translated to \n
                self.assertEqual(treks['features'][0]['properties']['description'], 'toto\ntata')
        self.trek.description = old_description
        self.trek.save()

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @override_settings(ONLY_EXTERNAL_PUBLIC_PDF=True)
    def test_only_external_public_pdf(self, trek):
        output = StringIO()
        trek = TrekFactory.create(published=True, )
        filetype_topoguide = FileTypeFactory.create(type='Topoguide')
        AttachmentFactory.create(content_object=trek, attachment_file=get_dummy_uploaded_image(),
                                 filetype=filetype_topoguide)
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000', verbosity=2,
                                skip_pdf=False, skip_tiles=True, stdout=output)
        self.assertFalse(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'en', 'treks', str(self.trek.pk), '%s.pdf' % self.trek.slug)))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'en', 'treks', str(trek.pk), '%s.pdf' % trek.slug)))

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    def test_sync_pdf_all_languages(self, trek):
        output = StringIO()
        trek = TrekFactory.create(published_it=True, published_en=True, published_fr=True, name_fr='FR', name_en='EN',
                                  name_it="IT")
        trek_2 = TrekFactory.create(published_it=True, published_en=True, published_fr=True, name_fr='FR_2',
                                    name_en='EN_2', name_it="IT_2")
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000', verbosity=2,
                                skip_pdf=False, skip_tiles=True, stdout=output)
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'en', 'treks', str(trek.pk), '%s.pdf' % trek.slug)))
        self.assertFalse(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'it', 'treks', str(trek.pk), '%s.pdf' % trek.slug)))
        self.assertFalse(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'fr', 'treks', str(trek.pk), '%s.pdf' % trek.slug)))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'it', 'treks', str(trek.pk), 'it.pdf')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'fr', 'treks', str(trek.pk), 'fr.pdf')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'it', 'treks', str(trek.pk), 'it.gpx')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'fr', 'treks', str(trek.pk), 'fr.gpx')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'it', 'treks', str(trek.pk), 'it.kml')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'fr', 'treks', str(trek.pk), 'fr.kml')))

        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'it', 'treks', str(trek_2.pk), 'it_2.pdf')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'fr', 'treks', str(trek_2.pk), 'fr_2.pdf')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'it', 'treks', str(trek_2.pk), 'it_2.gpx')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'fr', 'treks', str(trek_2.pk), 'fr_2.gpx')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'it', 'treks', str(trek_2.pk), 'it_2.kml')))
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'fr', 'treks', str(trek_2.pk), 'fr_2.kml')))


class SyncComplexTest(VarTmpTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.information_desks = InformationDeskFactory.create()
        cls.trek = TrekWithPublishedPOIsFactory.create(published=True)
        if settings.TREKKING_TOPOLOGY_ENABLED:
            InfrastructureFactory.create(paths=[(cls.trek.paths.first(), 0, 0)], name="INFRA_1")
            SignageFactory.create(paths=[(cls.trek.paths.first(), 0, 0)], name="SIGNA_1")
        else:
            InfrastructureFactory.create(geom='SRID=2154;POINT(700000 6600000)', name="INFRA_1")
            SignageFactory.create(geom='SRID=2154;POINT(700000 6600000)', name="SIGNA_1")
        area = SensitiveAreaFactory.create(published=True)
        area.species.practices.add(SportPracticeFactory.create(name='Terrestre'))
        area.save()
        cls.touristic_content = TouristicContentFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        cls.touristic_event = TouristicEventFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        cls.attachment_touristic_content = AttachmentFactory.create(content_object=cls.touristic_content,
                                                                    attachment_file=get_dummy_uploaded_image())
        cls.attachment_touristic_event = AttachmentFactory.create(content_object=cls.touristic_event,
                                                                  attachment_file=get_dummy_uploaded_image())
        cls.touristic_content_without_attachment = TouristicContentFactory(
            geom='SRID=%s;POINT(700002 6600002)' % settings.SRID, published=True)
        cls.touristic_event_without_attachment = TouristicEventFactory(
            geom='SRID=%s;POINT(700002 6600002)' % settings.SRID, published=True)

    def get_coordinates(self, geojsonfilename):
        with open(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'en', geojsonfilename), 'r') as f:
            geojsonfile = json.load(f)
            if geojsonfile['features']:
                coordinates = geojsonfile['features'][0]['geometry']['coordinates']
                return coordinates
            return None

    def test_sync_geom_4326(self):
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000',
                                with_signages=True, with_infrastructures=True, with_dives=True,
                                skip_tiles=True, skip_pdf=True, languages='en', verbosity=2,
                                content_categories="1", with_events=True, stdout=StringIO())
        geojson_files = [
            'infrastructures.geojson',
            'touristiccontents.geojson',
            'touristicevents.geojson',
            'sensitiveareas.geojson',
            'signages.geojson',
            'services.geojson',
        ]
        for geojsonfilename in geojson_files:
            with self.subTest(line=geojsonfilename):
                coordinates = self.get_coordinates(geojsonfilename)
                if coordinates:
                    if isinstance(coordinates[0], float):
                        self.assertTrue(coordinates[0] < 90)
                    elif isinstance(coordinates[0][0], float):
                        self.assertTrue(coordinates[0][0] < 90)
                    elif isinstance(coordinates[0][0][0], float):
                        self.assertTrue(coordinates[0][0][0] < 90)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=False, SPLIT_DIVES_CATEGORIES_BY_PRACTICE=False)
    def test_sync_with_multipolygon_sensitive_area(self):
        area = SensitiveAreaFactory.create(geom='MULTIPOLYGON(((0 0, 0 3, 3 3, 3 0, 0 0)))', published=True)
        area.species.practices.add(SportPracticeFactory.create(name='Terrestre'))
        area.save()
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), with_signages=True, with_infrastructures=True,
                                with_dives=True, with_events=True, content_categories="1", url='http://localhost:8000',
                                skip_tiles=True, skip_pdf=True, verbosity=2, languages='en', stdout=StringIO())
        with open(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'en', 'sensitiveareas.geojson'), 'r') as f:
            area = json.load(f)
            # there are 2 areas
            self.assertEqual(len(area['features']), 2)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=False, SPLIT_DIVES_CATEGORIES_BY_PRACTICE=False)
    def test_sync_picture_missing_from_disk(self):
        os.remove(self.information_desks.photo.path)
        output = StringIO()
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), with_signages=True, with_infrastructures=True,
                                with_dives=True, with_events=True, content_categories="1", url='http://localhost:8000',
                                skip_tiles=True, skip_pdf=True, languages='en', verbosity=2, stdout=output)
        self.assertIn('Done', output.getvalue())

    @mock.patch('geotrek.trekking.views.TrekAPIViewSet.list')
    def test_streaminghttpresponse(self, mocke):
        output = StringIO()
        mocke.return_value = StreamingHttpResponse()
        trek = TrekWithPublishedPOIsFactory.create(published_fr=True)
        management.call_command('sync_rando', os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync'), url='http://localhost:8000', skip_pdf=True,
                                skip_tiles=True, languages='fr', verbosity=2, stdout=output)
        self.assertTrue(os.path.exists(os.path.join(settings.TMP_DIR, 'sync_rando', 'tmp_sync', 'api', 'fr', 'treks', str(trek.pk), 'profile.png')))
