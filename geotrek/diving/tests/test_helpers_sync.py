import os
from unittest.mock import patch
from io import StringIO

from django.test import TestCase
from django.conf import settings

from geotrek.common.tests.factories import FakeSyncCommand, RecordSourceFactory, TargetPortalFactory, AttachmentFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_file
from geotrek.diving.tests.factories import DiveFactory, PracticeFactory
from geotrek.trekking.tests.factories import POIFactory
from geotrek.tourism.tests.factories import TouristicContentFactory, TouristicEventFactory

from geotrek.diving.helpers_sync import SyncRando


@patch('geotrek.diving.models.Dive.prepare_map_image')
class SyncRandoTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.practice_dive = PracticeFactory.create(order=0)
        cls.dive = DiveFactory.create(practice=cls.practice_dive, published=True,
                                      geom='SRID=2154;POINT(700001 6600001)')
        cls.attachment_dive = AttachmentFactory.create(content_object=cls.dive,
                                                       attachment_file=get_dummy_uploaded_image())
        cls.poi_dive = POIFactory.create(name="dive_poi", published=True)
        AttachmentFactory.create(content_object=cls.poi_dive,
                                 attachment_file=get_dummy_uploaded_image())
        AttachmentFactory.create(content_object=cls.poi_dive,
                                 attachment_file=get_dummy_uploaded_image())
        AttachmentFactory.create(content_object=cls.poi_dive,
                                 attachment_file=get_dummy_uploaded_file())
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
        cls.source_a = RecordSourceFactory()
        cls.source_b = RecordSourceFactory()

        cls.portal_a = TargetPortalFactory()
        cls.portal_b = TargetPortalFactory()
        cls.dive_portal_source = DiveFactory.create(practice=cls.practice_dive, published=True,
                                                    geom='SRID=2154;POINT(700002 6600002)',
                                                    portals=(cls.portal_a,), sources=(cls.source_a,))
        cls.dive_other_portal_source = DiveFactory.create(practice=cls.practice_dive, published=True,
                                                          geom='SRID=2154;POINT(700002 6600002)',
                                                          portals=(cls.portal_b,), sources=(cls.source_b,))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_detail_no_portal_no_source(self, stdout, mock_prepare):
        command = FakeSyncCommand()
        synchro = SyncRando(command)
        synchro.sync_detail('fr', self.dive)
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'dives',
                                                    str(self.dive.pk), '%s.pdf' % self.dive.slug)))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_detail_portal_source(self, stdout, mock_prepare):
        command = FakeSyncCommand(portal=self.portal_b.name, source=[self.source_b.name])
        synchro = SyncRando(command)
        synchro.sync_detail('fr', self.dive)
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'dives',
                                                    str(self.dive.pk), '%s.pdf' % self.dive.slug)))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'dives',
                                                    str(self.dive.pk), 'pois.geojson')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'dives',
                                                    str(self.dive.pk), 'touristiccontents.geojson')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'dives',
                                                    str(self.dive.pk), 'touristicevents.geojson')))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_language(self, stdout, mock_prepare):
        def side_effect_sync(lang, trek):
            pass
        command = FakeSyncCommand()
        synchro = SyncRando(command)
        with patch('geotrek.diving.helpers_sync.SyncRando.sync_detail', side_effect=side_effect_sync) as mock_dive:
            synchro.sync('en')
        self.assertEqual(len(mock_dive.call_args_list), 3)
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'en', 'dives.geojson')))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_language_portal_source(self, stdout, mock_prepare):
        def side_effect_sync(lang, dive):
            self.assertEqual(dive, self.dive_portal_source)
        command = FakeSyncCommand(portal=self.portal_a.name, source=[self.source_a.name])
        synchro = SyncRando(command)
        with patch('geotrek.diving.helpers_sync.SyncRando.sync_detail', side_effect=side_effect_sync) as mock_dive:
            synchro.sync('en')
        self.assertEqual(len(mock_dive.call_args_list), 1)
        mock_dive.assert_called_with('en', self.dive_portal_source)
