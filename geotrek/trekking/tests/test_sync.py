# -*- coding: utf-8 -*-
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

from geotrek.common.factories import FileTypeFactory, RecordSourceFactory, TargetPortalFactory, AttachmentFactory, ThemeFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_file
from geotrek.diving.factories import DiveFactory, PracticeFactory as PracticeDiveFactory
from geotrek.diving.models import Dive
from geotrek.infrastructure.factories import InfrastructureFactory
from geotrek.sensitivity.factories import SensitiveAreaFactory
from geotrek.signage.factories import SignageFactory
from geotrek.trekking.factories import PracticeFactory as PracticeTrekFactory, TrekFactory, TrekWithPublishedPOIsFactory
from geotrek.trekking import models as trek_models
from geotrek.tourism.factories import InformationDeskFactory, TouristicContentFactory, TouristicEventFactory


class SyncRandoTilesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        if os.path.exists(os.path.join('var', 'tmp')):
            shutil.rmtree(os.path.join('var', 'tmp'))
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
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        if os.path.exists(os.path.join('var', 'tmp')):
            shutil.rmtree(os.path.join('var', 'tmp'))
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
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=BytesIO(), stderr=BytesIO())
        self.assertEqual(e.exception.message, 'Some errors raised during synchronization.')
        self.assertFalse(os.path.exists(os.path.join('var', 'tmp', 'mobile', 'nolang', 'media', 'trekking_trek')))

    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('geotrek.trekking.views.TrekViewSet.list')
    def test_response_500(self, mocke_list, mocke_map_image):
        output = BytesIO()
        error = BytesIO()
        mocke_list.return_value = HttpResponse(status=500)
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, verbosity=2, stdout=output, stderr=error)
        self.assertIn("failed (HTTP 500)", error.getvalue())
        self.assertEqual(e.exception.message, 'Some errors raised during synchronization.')

    @override_settings(MEDIA_URL=9)
    def test_bad_settings(self):
        output = BytesIO()
        TrekWithPublishedPOIsFactory.create(published_fr=True)
        with self.assertRaises(AttributeError) as e:
            management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=output, stderr=BytesIO())
            self.assertIn("Exception raised in callable attribute", output.getvalue())
        self.assertEqual(e.exception.message, "'int' object has no attribute 'strip'")

    def test_sync_fail_src_file_not_exist(self):
        output = BytesIO()
        theme = ThemeFactory.create()
        theme.pictogram = "other"
        theme.save()
        with self.assertRaises(CommandError) as e:
            management.call_command('sync_rando', 'tmp', url='http://localhost:8000',
                                    skip_tiles=True, languages='fr', verbosity=2, stdout=output, stderr=BytesIO())
        self.assertEqual(e.exception.message, 'Some errors raised during synchronization.')
        self.assertIn("file does not exist", output.getvalue())

    @classmethod
    def tearDownClass(cls):
        super(SyncRandoFailTest, cls).tearDownClass()
        shutil.rmtree(os.path.join('var', 'tmp'))


class SyncSetup(TestCase):
    @classmethod
    def setUpClass(cls):
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        if os.path.exists(os.path.join('var', 'tmp')):
            shutil.rmtree(os.path.join('var', 'tmp'))
        super(SyncSetup, cls).setUpClass()

    def setUp(self):
        self.source_a = RecordSourceFactory()
        self.source_b = RecordSourceFactory()

        self.portal_a = TargetPortalFactory()
        self.portal_b = TargetPortalFactory()
        information_desks = InformationDeskFactory.create()

        self.practice_trek = PracticeTrekFactory.create(order=0)

        self.trek_1 = TrekWithPublishedPOIsFactory.create(practice=self.practice_trek, sources=(self.source_a, ),
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
        self.trek_4 = TrekFactory.create(practice=self.practice_trek, portals=(self.portal_a,),
                                         published=True)
        self.practice_dive = PracticeDiveFactory.create(order=0)

        self.dive_1 = DiveFactory.create(practice=self.practice_dive, sources=(self.source_a,),
                                         portals=(self.portal_b,),
                                         published=True)
        self.attachment_dive = AttachmentFactory.create(content_object=self.dive_1,
                                                        attachment_file=get_dummy_uploaded_image())
        self.dive_2 = DiveFactory.create(sources=(self.source_b,),
                                         published=True)
        self.dive_3 = DiveFactory.create(portals=(self.portal_b,
                                                  self.portal_a),
                                         published=True)
        self.dive_4 = DiveFactory.create(practice=self.practice_dive, portals=(self.portal_a,),
                                         published=True)
        self.poi_1 = trek_models.POI.objects.first()
        self.attachment_poi_image_1 = AttachmentFactory.create(content_object=self.poi_1,
                                                               attachment_file=get_dummy_uploaded_image())
        self.attachment_poi_image_2 = AttachmentFactory.create(content_object=self.poi_1,
                                                               attachment_file=get_dummy_uploaded_image())
        self.attachment_poi_file = AttachmentFactory.create(content_object=self.poi_1,
                                                            attachment_file=get_dummy_uploaded_file())
        if settings.TREKKING_TOPOLOGY_ENABLED:
            infrastructure = InfrastructureFactory.create(no_path=True, name="INFRA_1")
            infrastructure.add_path(self.trek_1.paths.first(), start=0, end=0)
            signage = SignageFactory.create(no_path=True, name="SIGNA_1")
            signage.add_path(self.trek_1.paths.first(), start=0, end=0)
        else:
            InfrastructureFactory.create(geom='SRID=2154;POINT(700000 6600000)', name="INFRA_1")
            SignageFactory.create(geom='SRID=2154;POINT(700000 6600000)', name="SIGNA_1")
        SensitiveAreaFactory.create(published=True)
        self.touristic_content = TouristicContentFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        self.touristic_event = TouristicEventFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        self.attachment_touristic_content = AttachmentFactory.create(content_object=self.touristic_content,
                                                                     attachment_file=get_dummy_uploaded_image())
        self.attachment_touristic_event = AttachmentFactory.create(content_object=self.touristic_event,
                                                                   attachment_file=get_dummy_uploaded_image())

    def tearDown(self):
        shutil.rmtree(os.path.join('tmp'))


class SyncTest(SyncSetup):
    @override_settings(THUMBNAIL_COPYRIGHT_FORMAT=u'*' * 300)
    def test_sync_pictures_long_title_legend_author(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True,
                                    with_infrastructures=True, with_dives=True,
                                    with_events=True, content_categories="1", url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # there are 4 treks
                self.assertEquals(len(treks['features']),
                                  trek_models.Trek.objects.filter(published=True).count())

    @override_settings(THUMBNAIL_COPYRIGHT_FORMAT=u'{author} éà@za,£')
    def test_sync_pictures_with_accents(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True,
                                    with_infrastructures=True, with_dives=True,
                                    with_events=True, content_categories="1", url='http://localhost:8000',
                                    skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
            with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
                treks = json.load(f)
                # there are 4 treks
                self.assertEquals(len(treks['features']),
                                  trek_models.Trek.objects.filter(published=True).count())

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=False, SPLIT_DIVES_CATEGORIES_BY_PRACTICE=False)
    def test_sync_without_pdf(self):
        management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True, with_infrastructures=True,
                                with_dives=True, with_events=True, content_categories="1", url='http://localhost:8000',
                                skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)
            # there are 4 treks
            self.assertEquals(len(treks['features']),
                              trek_models.Trek.objects.filter(published=True).count())
            self.assertEquals(treks['features'][0]['properties']['category']['id'],
                              treks['features'][3]['properties']['category']['id'],
                              'T')
            self.assertEquals(treks['features'][0]['properties']['name'], self.trek_1.name)
            self.assertEquals(treks['features'][3]['properties']['name'], self.trek_4.name)

        with open(os.path.join('var', 'tmp', 'api', 'en', 'dives.geojson'), 'r') as f:
            dives = json.load(f)
            # there are 4 dives
            self.assertEquals(len(dives['features']),
                              Dive.objects.filter(published=True).count())
            self.assertEquals(dives['features'][0]['properties']['category']['id'],
                              dives['features'][3]['properties']['category']['id'],
                              'D')
            self.assertEquals(dives['features'][0]['properties']['name'], self.dive_1.name)
            self.assertEquals(dives['features'][3]['properties']['name'], self.dive_4.name)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=True, SPLIT_DIVES_CATEGORIES_BY_PRACTICE=True)
    def test_sync_without_pdf_split_by_practice(self):
        management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True, with_infrastructures=True,
                                with_dives=True, with_events=True, content_categories="1", url='http://localhost:8000',
                                skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)
            # there are 4 treks
            self.assertEquals(len(treks['features']),
                              trek_models.Trek.objects.filter(published=True).count())
            self.assertEquals(treks['features'][0]['properties']['category']['id'],
                              treks['features'][3]['properties']['category']['id'],
                              'T%s' % self.practice_trek.pk)
            self.assertEquals(treks['features'][0]['properties']['name'], self.trek_1.name)
            self.assertEquals(treks['features'][3]['properties']['name'], self.trek_4.name)

        with open(os.path.join('var', 'tmp', 'api', 'en', 'dives.geojson'), 'r') as f:
            dives = json.load(f)
            # there are 4 dives
            self.assertEquals(len(dives['features']),
                              Dive.objects.filter(published=True).count())
            self.assertEquals(dives['features'][0]['properties']['category']['id'],
                              dives['features'][3]['properties']['category']['id'],
                              'D%s' % self.practice_dive.pk)
            self.assertEquals(dives['features'][0]['properties']['name'], self.dive_1.name)
            self.assertEquals(dives['features'][3]['properties']['name'], self.dive_4.name)

    def test_sync_https(self):
        with mock.patch('geotrek.trekking.models.Trek.prepare_map_image'):
            management.call_command('sync_rando', os.path.join('var', 'tmp'), with_signages=True, with_infrastructures=True, with_dives=True,
                                    with_events=True, content_categories="1", url='https://localhost:8000',
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
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', skip_pdf=True,
                                skip_tiles=True, verbosity=2, stdout=output)
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp', 'api', 'fr', 'treks', str(trek.pk), 'profile.png')))

    def test_sync_filtering_sources(self):
        # source A only
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                source=self.source_a.name, skip_tiles=True, skip_pdf=True, verbosity=2,
                                stdout=BytesIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)
            # only 1 trek in Source A
            self.assertEquals(len(treks['features']),
                              trek_models.Trek.objects.filter(published=True,
                                                              source__name__in=[self.source_a.name, ]).count())

    def test_sync_filtering_sources_diving(self):
        # source A only
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', with_dives=True,
                                source=self.source_a.name, skip_tiles=True, skip_pdf=True, verbosity=2,
                                stdout=BytesIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'dives.geojson'), 'r') as f:
            dives = json.load(f)
            # only 1 trek in Source A
            self.assertEquals(len(dives['features']),
                              trek_models.Trek.objects.filter(published=True,
                                                              source__name__in=[self.source_a.name, ]).count())

    def test_sync_filtering_portals(self):
        # portal B only
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                portal=self.portal_b.name, skip_tiles=True, skip_pdf=True, verbosity=2,
                                stdout=BytesIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)

            # only 2 treks in Portal B + 1 without portal specified
            self.assertEquals(len(treks['features']), 3)

        # portal A and B
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                portal='{},{}'.format(self.portal_a.name, self.portal_b.name),
                                skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'treks.geojson'), 'r') as f:
            treks = json.load(f)

            # 4 treks have portal A or B or no portal
            self.assertEquals(len(treks['features']), 4)

    def test_sync_filtering_portals_diving(self):
        # portal B only
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000', with_dives=True,
                                portal=self.portal_b.name, skip_tiles=True, skip_pdf=True, verbosity=2,
                                stdout=BytesIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'dives.geojson'), 'r') as f:
            dives = json.load(f)

            # only 2 dives in Portal B + 1 without portal specified
            self.assertEquals(len(dives['features']), 3)

        # portal A and B
        management.call_command('sync_rando', os.path.join('var', 'tmp'), url='http://localhost:8000',
                                portal='{},{}'.format(self.portal_a.name, self.portal_b.name), with_dives=True,
                                skip_tiles=True, skip_pdf=True, verbosity=2, stdout=BytesIO())
        with open(os.path.join('var', 'tmp', 'api', 'en', 'dives.geojson'), 'r') as f:
            dives = json.load(f)
            # 4 dives have portal A or B or no portal
            self.assertEquals(len(dives['features']), 4)


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
        output = BytesIO()
        management.call_command('sync_rando', 'tmp', url='http://localhost:8000', verbosity=2,
                                skip_pdf=False, skip_tiles=True, stdout=output)
        self.assertFalse(os.path.exists(os.path.join('tmp', 'api', 'en', 'dives', str(self.dive_1.pk), '%s.pdf' % self.dive_1.slug)))
        self.assertFalse(os.path.exists(os.path.join('tmp', 'api', 'en', 'dives', str(self.dive_2.pk), '%s.pdf' % self.dive_2.slug)))
        self.assertFalse(os.path.exists(os.path.join('tmp', 'api', 'en', 'dives', str(self.dive_3.pk), '%s.pdf' % self.dive_3.slug)))
        self.assertFalse(os.path.exists(os.path.join('tmp', 'api', 'en', 'dives', str(self.dive_4.pk), '%s.pdf' % self.dive_4.slug)))
        self.assertFalse(os.path.exists(os.path.join('tmp', 'api', 'en', 'treks', str(self.trek_1.pk), '%s.pdf' % self.trek_1.slug)))
        self.assertFalse(os.path.exists(os.path.join('tmp', 'api', 'en', 'treks', str(self.trek_2.pk), '%s.pdf' % self.trek_2.slug)))
        self.assertFalse(os.path.exists(os.path.join('tmp', 'api', 'en', 'treks', str(self.trek_3.pk), '%s.pdf' % self.trek_3.slug)))
        self.assertFalse(os.path.exists(os.path.join('tmp', 'api', 'en', 'treks', str(self.trek_4.pk), '%s.pdf' % self.trek_4.slug)))
        self.assertTrue(os.path.exists(os.path.join('tmp', 'api', 'en', 'treks', str(self.trek_5.pk), '%s.pdf' % self.trek_5.slug)))

    def test_sync_pdfs(self, event, content, dive, trek):
        output = BytesIO()
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

    def test_sync_pdfs_portals_sources(self, event, content, dive, trek):
        output = BytesIO()
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

    def tearDown(self):
        shutil.rmtree(os.path.join('var', 'tmp'))
