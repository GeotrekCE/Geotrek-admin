import errno
import os
import json
from landez.sources import DownloadError
from unittest import mock
import shutil
from io import StringIO
import zipfile

from django.test import TestCase
from django.conf import settings
from django.contrib.gis.geos import LineString
from django.core import management
from django.core.management.base import CommandError
from django.http import HttpResponse, StreamingHttpResponse
from django.test.utils import override_settings

from geotrek.common.factories import FileTypeFactory, RecordSourceFactory, TargetPortalFactory, AttachmentFactory, ThemeFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_file
from geotrek.core.factories import PathFactory
from geotrek.diving.factories import DiveFactory, PracticeFactory as PracticeDiveFactory
from geotrek.diving.models import Dive
from geotrek.infrastructure.factories import InfrastructureFactory
from geotrek.sensitivity.factories import SensitiveAreaFactory, SportPracticeFactory
from geotrek.signage.factories import SignageFactory
from geotrek.trekking.factories import POIFactory, PracticeFactory as PracticeTrekFactory, TrekFactory, TrekWithPublishedPOIsFactory
from geotrek.trekking import models as trek_models
from geotrek.tourism.factories import InformationDeskFactory, TouristicContentFactory, TouristicEventFactory


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


class SyncSetup(VarTmpTestCase):
    def setUp(self):
        super().setUp()
        self.source_a = RecordSourceFactory()
        self.source_b = RecordSourceFactory()

        self.portal_a = TargetPortalFactory()
        self.portal_b = TargetPortalFactory()
        self.information_desks = InformationDeskFactory.create()
        information_desk_without_photo = InformationDeskFactory.create(photo=None)
        self.practice_trek = PracticeTrekFactory.create(order=1)
        self.practice_trek_first = PracticeTrekFactory.create(order=0)
        self.trek_1 = TrekWithPublishedPOIsFactory.create(practice=self.practice_trek, sources=(self.source_a, ),
                                                          portals=(self.portal_b,),
                                                          published=True)
        self.trek_1.information_desks.add(self.information_desks)
        self.trek_1.information_desks.add(information_desk_without_photo)
        self.attachment_1 = AttachmentFactory.create(content_object=self.trek_1,
                                                     attachment_file=get_dummy_uploaded_image())
        self.trek_2 = TrekFactory.create(sources=(self.source_b,),
                                         published=True)
        self.trek_3 = TrekFactory.create(portals=(self.portal_b,
                                                  self.portal_a),
                                         published=True)
        self.trek_4 = TrekFactory.create(practice=self.practice_trek, portals=(self.portal_a,),
                                         published=True)
        self.trek_5 = TrekFactory.create(practice=self.practice_trek_first, portals=(self.portal_a,),
                                         published=True, name="other")

        self.practice_dive = PracticeDiveFactory.create(order=0)

        self.dive_1 = DiveFactory.create(practice=self.practice_dive, sources=(self.source_a,),
                                         portals=(self.portal_b,),
                                         published=True, geom='SRID=2154;POINT(700001 6600001)')
        self.attachment_dive = AttachmentFactory.create(content_object=self.dive_1,
                                                        attachment_file=get_dummy_uploaded_image())
        self.dive_2 = DiveFactory.create(sources=(self.source_b,),
                                         published=True, geom='SRID=2154;LINESTRING (700000 6600000, 700100 6600100)')
        self.dive_3 = DiveFactory.create(portals=(self.portal_b,
                                                  self.portal_a),
                                         published=True, geom='POLYGON((700000 6600000, 700000 6600100, '
                                                              '700100 6600100, 700100 6600000, 700000 6600000))')
        self.dive_4 = DiveFactory.create(practice=self.practice_dive, portals=(self.portal_a,),
                                         published=True)
        self.poi_1 = trek_models.POI.objects.first()
        self.poi_dive = POIFactory.create(name="dive_poi", published=True)
        self.attachment_poi_image_1 = AttachmentFactory.create(content_object=self.poi_1,
                                                               attachment_file=get_dummy_uploaded_image())
        AttachmentFactory.create(content_object=self.poi_dive,
                                 attachment_file=get_dummy_uploaded_image())
        self.attachment_poi_image_2 = AttachmentFactory.create(content_object=self.poi_1,
                                                               attachment_file=get_dummy_uploaded_image())
        AttachmentFactory.create(content_object=self.poi_dive,
                                 attachment_file=get_dummy_uploaded_file())
        self.attachment_poi_file = AttachmentFactory.create(content_object=self.poi_1,
                                                            attachment_file=get_dummy_uploaded_file())
        if settings.TREKKING_TOPOLOGY_ENABLED:
            InfrastructureFactory.create(paths=[(self.trek_1.paths.first(), 0, 0)], name="INFRA_1")
            SignageFactory.create(paths=[(self.trek_1.paths.first(), 0, 0)], name="SIGNA_1")
        else:
            InfrastructureFactory.create(geom='SRID=2154;POINT(700000 6600000)', name="INFRA_1")
            SignageFactory.create(geom='SRID=2154;POINT(700000 6600000)', name="SIGNA_1")
        area = SensitiveAreaFactory.create(published=True)
        area.species.practices.add(SportPracticeFactory.create(name='Terrestre'))
        area.save()
        self.touristic_content = TouristicContentFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        self.touristic_event = TouristicEventFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        self.attachment_touristic_content = AttachmentFactory.create(content_object=self.touristic_content,
                                                                     attachment_file=get_dummy_uploaded_image())
        self.attachment_touristic_event = AttachmentFactory.create(content_object=self.touristic_event,
                                                                   attachment_file=get_dummy_uploaded_image())
        self.touristic_content_without_attachment = TouristicContentFactory(
            geom='SRID=%s;POINT(700002 6600002)' % settings.SRID, published=True, portals=(self.portal_b,),
            sources=(self.source_a,))
        self.touristic_event_without_attachment = TouristicEventFactory(
            geom='SRID=%s;POINT(700002 6600002)' % settings.SRID, published=True, portals=(self.portal_a,),
            sources=(self.source_b,))


class SyncTest(SyncSetup):
    @override_settings(THUMBNAIL_COPYRIGHT_FORMAT='*' * 300)
    def test_sync_pictures_long_title_legend_author(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True,
                                    with_infrastructures=True, with_dives=True,
                                    with_events=True, content_categories="1", url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, languages='en', verbosity=2, stdout=StringIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # there are 4 treks
                self.assertEqual(len(treks['features']),
                                 trek_models.Trek.objects.filter(published=True).count())

    @override_settings(THUMBNAIL_COPYRIGHT_FORMAT='{author} éà@za,£')
    def test_sync_pictures_with_accents(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True,
                                    with_infrastructures=True, with_dives=True,
                                    with_events=True, content_categories="1", url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, languages='en', verbosity=2, stdout=StringIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # there are 4 treks
                self.assertEqual(len(treks['features']),
                                 trek_models.Trek.objects.filter(published=True).count())

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=False, SPLIT_DIVES_CATEGORIES_BY_PRACTICE=False)
    def test_sync_without_pdf(self):
        management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True, with_infrastructures=True,
                                with_dives=True, with_events=True, content_categories="1", url='http://localhost:8000',
                                skip_tiles=True, skip_pdf=True, languages='en', verbosity=2, stdout=StringIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)
            # there are 4 treks
            self.assertEqual(len(treks['features']),
                             trek_models.Trek.objects.filter(published=True).count())
            self.assertEqual(treks['features'][0]['properties']['category']['id'],
                             treks['features'][3]['properties']['category']['id'],
                             'T')
            self.assertEqual(treks['features'][0]['properties']['name'], self.trek_2.name)
            self.assertEqual(treks['features'][3]['properties']['name'], self.trek_4.name)

        with open(os.path.join('var', 'tmp', 'api', 'en', 'dives.geojson'), 'r') as f:
            dives = json.load(f)
            # there are 4 dives
            self.assertEqual(len(dives['features']),
                             Dive.objects.filter(published=True).count())
            self.assertEqual(dives['features'][0]['properties']['category']['id'],
                             dives['features'][3]['properties']['category']['id'],
                             'D')
            self.assertEqual(dives['features'][0]['properties']['name'], self.dive_1.name)
            self.assertEqual(dives['features'][3]['properties']['name'], self.dive_4.name)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=True, SPLIT_DIVES_CATEGORIES_BY_PRACTICE=True)
    def test_sync_without_pdf_split_by_practice(self):
        management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True, with_infrastructures=True,
                                with_dives=True, with_events=True, content_categories="1", url='http://localhost:8000',
                                skip_tiles=True, skip_pdf=True, languages='en', verbosity=2, stdout=StringIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)
            # there are 4 treks
            self.assertEqual(len(treks['features']),
                             trek_models.Trek.objects.filter(published=True).count())
            self.assertEqual(treks['features'][2]['properties']['category']['id'],
                             treks['features'][3]['properties']['category']['id'],
                             'T%s' % self.practice_trek.pk)
            self.assertEqual(treks['features'][2]['properties']['name'], self.trek_1.name)
            self.assertEqual(treks['features'][3]['properties']['name'], self.trek_4.name)

        with open(os.path.join('var', 'tmp', 'api', 'en', 'dives.geojson'), 'r') as f:
            dives = json.load(f)
            # there are 4 dives
            self.assertEqual(len(dives['features']),
                             Dive.objects.filter(published=True).count())
            self.assertEqual(dives['features'][0]['properties']['category']['id'],
                             dives['features'][3]['properties']['category']['id'],
                             'D%s' % self.practice_dive.pk)
            self.assertEqual(dives['features'][0]['properties']['name'], self.dive_1.name)
            self.assertEqual(dives['features'][3]['properties']['name'], self.dive_4.name)

    def test_sync_https(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True, with_infrastructures=True, with_dives=True,
                                    with_events=True, content_categories="1", url='https://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, languages='en', verbosity=2, stdout=StringIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # there are 4 treks
                self.assertEqual(len(treks['features']),
                                 trek_models.Trek.objects.filter(published=True).count())

    def test_sync_2028(self):
        self.trek_1.description = 'toto\u2028tata'
        self.trek_1.save()
        self.trek_2.delete()
        self.trek_3.delete()
        self.trek_4.delete()
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, languages='en', verbosity=2, stdout=StringIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # \u2028 is translated to \n
                self.assertEqual(treks['features'][0]['properties']['description'], 'toto\ntata')

    @mock.patch('geotrek.trekking.views.TrekViewSet.list')
    def test_streaminghttpresponse(self, mocke):
        output = StringIO()
        mocke.return_value = StreamingHttpResponse()
        trek = TrekWithPublishedPOIsFactory.create(published_fr=True)
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', skip_pdf=True,
                                skip_tiles=True, languages='fr', verbosity=2, stdout=output)
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'fr', 'treks', str(trek.pk), 'profile.png')))

    def test_sync_filtering_sources(self):
        # source A only
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                source=self.source_a.name, skip_tiles=True, skip_pdf=True, languages='en', verbosity=2,
                                content_categories="1", with_events=True, stdout=StringIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)
            # only 1 trek in Source A
            self.assertEqual(len(treks['features']),
                             trek_models.Trek.objects.filter(published=True,
                                                             source__name__in=[self.source_a.name, ]).count())

    def test_sync_filtering_sources_diving(self):
        # source A only
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', with_dives=True,
                                source=self.source_a.name, skip_tiles=True, skip_pdf=True, languages='en', verbosity=2,
                                content_categories="1", with_events=True, stdout=StringIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'dives.geojson'), 'r') as f:
            dives = json.load(f)
            # only 1 dive in Source A
            self.assertEqual(len(dives['features']),
                             trek_models.Trek.objects.filter(published=True,
                                                             source__name__in=[self.source_a.name, ]).count())

    def test_sync_filtering_portals(self):
        # portal B only
        management.call_command('sync_rando', 'var/tmp', url='http://localhost:8000',
                                portal=self.portal_b.name, skip_tiles=True, languages='en', skip_pdf=True, verbosity=2,
                                content_categories="1", with_events=True, stdout=StringIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)

            # only 2 treks in Portal B + 1 without portal specified
            self.assertEqual(len(treks['features']), 3)

    def test_sync_practice_orders(self):
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                skip_tiles=True, skip_pdf=True, languages='en', verbosity=2, stdout=StringIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)
            self.assertEqual(len(treks['features']), 5)
            trek_name = [trek.get('properties').get('name') for trek in treks['features']]

            # trek_5 => Practice (order 0); trek_1, trek_4 =>  Practice (order 1);
            # trek_2, trek_3 => usage 4 (no order, alphabetical)
            # It's desc for rando.
            self.assertEqual([self.trek_2.name, self.trek_3.name, self.trek_1.name, self.trek_4.name, self.trek_5.name],
                             trek_name)

    def test_sync_filtering_portals_diving(self):
        # portal B only
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', with_dives=True,
                                portal=self.portal_b.name, skip_tiles=True, skip_pdf=True, languages='en', verbosity=2,
                                stdout=StringIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'dives.geojson'), 'r') as f:
            dives = json.load(f)

            # only 2 dives in Portal B + 1 without portal specified
            self.assertEqual(len(dives['features']), 3)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=False, SPLIT_DIVES_CATEGORIES_BY_PRACTICE=False)
    def test_sync_with_multipolygon_sensitive_area(self):
        area = SensitiveAreaFactory.create(geom='MULTIPOLYGON(((0 0, 0 3, 3 3, 3 0, 0 0)))', published=True)
        area.species.practices.add(SportPracticeFactory.create(name='Terrestre'))
        area.save()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True, with_infrastructures=True,
                                with_dives=True, with_events=True, content_categories="1", url='http://localhost:8000',
                                skip_tiles=True, skip_pdf=True, verbosity=2, languages='en', stdout=StringIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'sensitiveareas.geojson'), 'r') as f:
            area = json.load(f)
            # there are 2 areas
            self.assertEqual(len(area['features']), 2)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=False, SPLIT_DIVES_CATEGORIES_BY_PRACTICE=False)
    def test_sync_picture_missing_from_disk(self):
        os.remove(self.information_desks.photo.path)
        output = StringIO()
        management.call_command('sync_rando', 'var/tmp', with_signages=True, with_infrastructures=True,
                                with_dives=True, with_events=True, content_categories="1", url='http://localhost:8000',
                                skip_tiles=True, skip_pdf=True, languages='en', verbosity=2, stdout=output)
        self.assertIn('Done', output.getvalue())


class SyncTestGeom(SyncSetup):
    def get_coordinates(self, geojsonfilename):
        with open(os.path.join('var', 'tmp', 'api', 'en', geojsonfilename), 'r') as f:
            geojsonfile = json.load(f)
            if geojsonfile['features']:
                coordinates = geojsonfile['features'][0]['geometry']['coordinates']
                return coordinates
            return None

    def test_sync_geom_4326(self):
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
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


@mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
@mock.patch('geotrek.diving.models.Dive.prepare_map_image')
@mock.patch('geotrek.tourism.models.TouristicContent.prepare_map_image')
@mock.patch('geotrek.tourism.models.TouristicEvent.prepare_map_image')
class SyncTestPdf(SyncSetup):
    def setUp(self):
        super(SyncTestPdf, self).setUp()
        self.trek_5 = TrekFactory.create(practice=self.practice_trek, portals=(self.portal_a,),
                                         published=True)
        filetype_topoguide = FileTypeFactory.create(type='Topoguide')
        AttachmentFactory.create(content_object=self.trek_5, attachment_file=get_dummy_uploaded_image(),
                                 filetype=filetype_topoguide)

    @override_settings(ONLY_EXTERNAL_PUBLIC_PDF=True)
    def test_only_external_public_pdf(self, event, content, dive, trek):
        output = StringIO()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                skip_pdf=False, skip_tiles=True, stdout=output)
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_1.pk), '%s.pdf' % self.dive_1.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_2.pk), '%s.pdf' % self.dive_2.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_3.pk), '%s.pdf' % self.dive_3.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_4.pk), '%s.pdf' % self.dive_4.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_1.pk), '%s.pdf' % self.trek_1.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_2.pk), '%s.pdf' % self.trek_2.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_3.pk), '%s.pdf' % self.trek_3.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_4.pk), '%s.pdf' % self.trek_4.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_5.pk), '%s.pdf' % self.trek_5.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristiccontents',
                                                     str(self.touristic_content.pk), '%s.pdf' % self.touristic_content.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristiccontents',
                                                     str(self.touristic_content_without_attachment.pk),
                                                     '%s.pdf' % self.touristic_content_without_attachment.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristicevents',
                                                     str(self.touristic_event.pk),
                                                     '%s.pdf' % self.touristic_event.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristicevents',
                                                     str(self.touristic_event_without_attachment.pk),
                                                     '%s.pdf' % self.touristic_event_without_attachment.slug)))

    def test_sync_pdfs(self, event, content, dive, trek):
        output = StringIO()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                with_dives=True, skip_tiles=True, stdout=output)
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_1.pk), '%s.pdf' % self.dive_1.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_2.pk), '%s.pdf' % self.dive_2.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_3.pk), '%s.pdf' % self.dive_3.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_4.pk), '%s.pdf' % self.dive_4.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_1.pk), '%s.pdf' % self.trek_1.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_2.pk), '%s.pdf' % self.trek_2.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_3.pk), '%s.pdf' % self.trek_3.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_4.pk), '%s.pdf' % self.trek_4.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_5.pk), '%s.pdf' % self.trek_5.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristiccontents',
                                                    str(self.touristic_content.pk), '%s.pdf' % self.touristic_content.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristiccontents',
                                                    str(self.touristic_content_without_attachment.pk),
                                                    '%s.pdf' % self.touristic_content_without_attachment.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristicevents',
                                                    str(self.touristic_event.pk), '%s.pdf' % self.touristic_event.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristicevents',
                                                    str(self.touristic_event_without_attachment.pk),
                                                    '%s.pdf' % self.touristic_event_without_attachment.slug)))

    def test_sync_pdfs_portals_sources(self, event, content, dive, trek):
        output = StringIO()
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                with_dives=True, skip_tiles=True, portal=self.portal_b.name, source=self.source_a.name,
                                stdout=output)
        # It has to be portal b or 'No portal' and source a : only dive_1 and trek_1 has both of these statements
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_1.pk), '%s.pdf' % self.dive_1.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_2.pk), '%s.pdf' % self.dive_2.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_3.pk), '%s.pdf' % self.dive_3.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'dives', str(self.dive_4.pk), '%s.pdf' % self.dive_4.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_1.pk), '%s.pdf' % self.trek_1.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_2.pk), '%s.pdf' % self.trek_2.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_3.pk), '%s.pdf' % self.trek_3.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_4.pk), '%s.pdf' % self.trek_4.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_5.pk), '%s.pdf' % self.trek_5.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristiccontents',
                                                     str(self.touristic_content.pk), '%s.pdf' % self.touristic_content.slug)))
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristiccontents',
                                                    str(self.touristic_content_without_attachment.pk),
                                                    '%s.pdf' % self.touristic_content_without_attachment.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristicevents',
                                                     str(self.touristic_event.pk), '%s.pdf' % self.touristic_event.slug)))
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'api', 'en', 'touristicevents',
                                                     str(self.touristic_event_without_attachment.pk),
                                                     '%s.pdf' % self.touristic_event_without_attachment.slug)))


@mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
@mock.patch('geotrek.diving.models.Dive.prepare_map_image')
@mock.patch('geotrek.tourism.models.TouristicContent.prepare_map_image')
@mock.patch('geotrek.tourism.models.TouristicEvent.prepare_map_image')
class SyncPdfBookletTest(VarTmpTestCase):
    def setUp(self):
        super().setUp()
        self.trek_1 = TrekFactory.create(published=True)

    def test_sync_pdfs_booklet(self, event, content, dive, trek):
        output = StringIO()
        with override_settings(USE_BOOKLET_PDF=False):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                    with_dives=True, skip_tiles=True, stdout=output)
            first_file = os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_1.pk), '%s.pdf' % self.trek_1.slug)
            size_first = os.stat(first_file).st_size
        with override_settings(USE_BOOKLET_PDF=True):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', verbosity=2,
                                    with_dives=True, skip_tiles=True, stdout=output)
            second_file = os.path.join('var', 'tmp', 'api', 'en', 'treks', str(self.trek_1.pk), '%s.pdf' % self.trek_1.slug)
            size_second = os.stat(second_file).st_size
        self.assertLess(size_first, size_second)
