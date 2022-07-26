import os
from unittest.mock import patch
from io import StringIO

from django.test import TestCase
from django.conf import settings

from geotrek.common.tests.factories import FakeSyncCommand, RecordSourceFactory, TargetPortalFactory, AttachmentFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.tourism.tests.factories import InformationDeskFactory, TouristicContentFactory, TouristicEventFactory

from geotrek.tourism.helpers_sync import SyncRando


@patch('geotrek.tourism.models.TouristicContent.prepare_map_image')
@patch('geotrek.tourism.models.TouristicEvent.prepare_map_image')
class SyncRandoTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.source = RecordSourceFactory()
        cls.portal = TargetPortalFactory()

        cls.information_desks = InformationDeskFactory.create()

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

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync(self, stdout, mock_prepare_event, mock_prepare_content):
        def side_effect_sync_event(lang, event):
            self.assertEqual(event, self.touristic_event)

        def side_effect_sync_content(lang, content):
            self.assertEqual(content, self.touristic_content)

        command = FakeSyncCommand()
        synchro = SyncRando(command)
        with patch('geotrek.tourism.helpers_sync.SyncRando.sync_event', side_effect=side_effect_sync_event):
            with patch('geotrek.tourism.helpers_sync.SyncRando.sync_content', side_effect=side_effect_sync_content):
                synchro.sync('en')
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'static', 'tourism',
                                                    'touristicevent.svg')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'en', 'information_desks.geojson')))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_portal_source(self, stdout, mock_prepare_event, mock_prepare_content):
        def side_effect_sync_event(lang, event):
            self.assertEqual(event, self.touristic_event_p_s)

        def side_effect_sync_content(lang, content):
            self.assertEqual(content, self.touristic_content_p_s)

        self.touristic_content_p_s = TouristicContentFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, sources=(self.source,),
            portals=(self.portal,), published=True)
        self.touristic_event_p_s = TouristicEventFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, sources=(self.source,),
            portals=(self.portal,), published=True)

        command = FakeSyncCommand(portal=self.portal.name, source=[self.source.name])
        synchro = SyncRando(command)
        with patch('geotrek.tourism.helpers_sync.SyncRando.sync_event', side_effect=side_effect_sync_event):
            with patch('geotrek.tourism.helpers_sync.SyncRando.sync_content', side_effect=side_effect_sync_content):
                synchro.sync('en')
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'static', 'tourism',
                                                    'touristicevent.svg')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'en', 'information_desks.geojson')))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_event(self, stdout, mock_prepare_event, mock_prepare_content):
        command = FakeSyncCommand()
        synchro = SyncRando(command)
        synchro.sync_event('fr', self.touristic_event)
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'touristicevents',
                                                    str(self.touristic_event.pk),
                                                    '%s.pdf' % self.touristic_event.slug)))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_content(self, stdout, mock_prepare_event, mock_prepare_content):
        command = FakeSyncCommand()
        synchro = SyncRando(command)
        synchro.sync_content('fr', self.touristic_content)
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'touristiccontents',
                                                    str(self.touristic_content.pk),
                                                    '%s.pdf' % self.touristic_content.slug)))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_event_portal_source(self, stdout, mock_prepare_event, mock_prepare_content):
        command = FakeSyncCommand(portal=self.portal.name, source=[self.source.name])
        synchro = SyncRando(command)
        synchro.sync_event('fr', self.touristic_event)
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'touristicevents',
                                                    str(self.touristic_event.pk),
                                                    '%s.pdf' % self.touristic_event.slug)))

    @patch('sys.stdout', new_callable=StringIO)
    def test_sync_content_portal_source(self, stdout, mock_prepare_event, mock_prepare_content):
        command = FakeSyncCommand(portal=self.portal.name, source=[self.source.name])
        synchro = SyncRando(command)
        synchro.sync_content('fr', self.touristic_content)
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'fr', 'touristiccontents',
                                                    str(self.touristic_content.pk),
                                                    '%s.pdf' % self.touristic_content.slug)))
