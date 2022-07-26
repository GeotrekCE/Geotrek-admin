import os
from unittest.mock import patch

from io import StringIO

from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings

from geotrek.common.tests.factories import FakeSyncCommand, RecordSourceFactory, TargetPortalFactory, AttachmentFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_file
from geotrek.trekking.tests.factories import TrekFactory, TrekWithPublishedPOIsFactory
from geotrek.trekking import models as trek_models
from geotrek.tourism.tests.factories import InformationDeskFactory, TouristicContentFactory, TouristicEventFactory

from geotrek.trekking.helpers_sync import SyncRando


@patch('geotrek.trekking.models.Trek.prepare_map_image')
class SyncRandoTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.trek = TrekWithPublishedPOIsFactory.create(published=True)
        cls.information_desks = InformationDeskFactory.create()
        cls.trek.information_desks.add(cls.information_desks)
        cls.attachment = AttachmentFactory.create(content_object=cls.trek,
                                                  attachment_file=get_dummy_uploaded_image())

        cls.source_a = RecordSourceFactory()
        cls.source_b = RecordSourceFactory()

        cls.portal_a = TargetPortalFactory()
        cls.portal_b = TargetPortalFactory()
        cls.trek_fr = TrekFactory.create(published_fr=True, sources=(cls.source_b,))
        cls.trek_sb = TrekFactory.create(sources=(cls.source_b,),
                                         published=True)

        cls.trek_sb_pa = TrekFactory.create(sources=(cls.source_b,), portals=(cls.portal_a,),
                                            published=True)

        cls.touristic_content = TouristicContentFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        cls.touristic_event = TouristicEventFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        cls.attachment_touristic_content = AttachmentFactory.create(content_object=cls.touristic_content,
                                                                    attachment_file=get_dummy_uploaded_image())
        cls.attachment_touristic_event = AttachmentFactory.create(content_object=cls.touristic_event,
                                                                  attachment_file=get_dummy_uploaded_image())
        AttachmentFactory.create(content_object=cls.touristic_content,
                                 attachment_file=get_dummy_uploaded_image())
        AttachmentFactory.create(content_object=cls.touristic_event,
                                 attachment_file=get_dummy_uploaded_image())
        cls.poi = trek_models.POI.objects.first()
        cls.attachment_poi_image = AttachmentFactory.create(content_object=cls.poi,
                                                            attachment_file=get_dummy_uploaded_image())
        AttachmentFactory.create(content_object=cls.poi,
                                 attachment_file=get_dummy_uploaded_image())
        AttachmentFactory.create(content_object=cls.poi,
                                 attachment_file=get_dummy_uploaded_file())

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_detail_no_portal_no_source(self, stdout, mock_prepare):
        command = FakeSyncCommand()
        synchro = SyncRando(command)
        synchro.sync_detail('fr', self.trek)
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), '%s.pdf' % self.trek.slug)))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), 'pois.geojson')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), 'dem.json')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), 'profile.png')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), 'touristiccontents.geojson')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), 'touristicevents.geojson')))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_detail_no_portal_no_source_skip_everything(self, stdout, mock_prepare):
        command = FakeSyncCommand(skip_dem=True, skip_pdf=True, skip_profile_png=True)
        synchro = SyncRando(command)
        synchro.sync_detail('fr', self.trek)
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), 'pois.geojson')))
        self.assertFalse(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                     str(self.trek.pk), '%s.pdf' % self.trek.slug)))
        self.assertFalse(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                     str(self.trek.pk), 'dem.json')))
        self.assertFalse(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                     str(self.trek.pk), 'profile.png')))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_detail_booklet(self, stdout, mock_prepare):
        command = FakeSyncCommand(skip_dem=True, skip_profile_png=True)
        synchro = SyncRando(command)
        with override_settings(USE_BOOKLET_PDF=False):
            synchro.sync_detail('en', self.trek)
            first_file = os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'en', 'treks', str(self.trek.pk),
                                      '%s.pdf' % self.trek.slug)
            size_first = os.stat(first_file).st_size
        with override_settings(USE_BOOKLET_PDF=True):
            synchro.sync_detail('en', self.trek)
            second_file = os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'en', 'treks', str(self.trek.pk),
                                       '%s.pdf' % self.trek.slug)
            size_second = os.stat(second_file).st_size
        self.assertLess(size_first, size_second)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_detail_portal_source(self, stdout, mock_prepare):
        command = FakeSyncCommand(portal=self.portal_b.name, source=[self.source_b.name])
        synchro = SyncRando(command)
        synchro.sync_detail('fr', self.trek)
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), '%s.pdf' % self.trek.slug)))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), 'pois.geojson')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), 'touristiccontents.geojson')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'treks',
                                                    str(self.trek.pk), 'touristicevents.geojson')))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_language(self, stdout, mock_prepare):
        def side_effect_sync(lang, trek):
            self.assertEqual(trek, self.trek_fr)
        command = FakeSyncCommand()
        synchro = SyncRando(command)
        with patch('geotrek.trekking.helpers_sync.SyncRando.sync_detail', side_effect=side_effect_sync):
            synchro.sync('fr')
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'static', 'trekking', 'trek.svg')))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_language_portal_source(self, stdout, mock_prepare):
        def side_effect_sync(lang, trek):
            self.assertEqual(trek, self.trek_fr)
        command = FakeSyncCommand(portal=self.portal_a.name, source=[self.source_b.name])
        synchro = SyncRando(command)
        with patch('geotrek.trekking.helpers_sync.SyncRando.sync_detail', side_effect=side_effect_sync) as mock_trek:
            synchro.sync('fr')
        self.assertEqual(len(mock_trek.call_args_list), 1)
        mock_trek.assert_called_with('fr', self.trek_fr)
