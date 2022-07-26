from io import StringIO
import os
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from geotrek.common.tests.factories import FakeSyncCommand, RecordSourceFactory, TargetPortalFactory
from geotrek.flatpages.tests.factories import FlatPageFactory
from geotrek.flatpages.helpers_sync import SyncRando


class SyncRandoTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.flatpage = FlatPageFactory.create(published=True, title="test-0")
        cls.source = RecordSourceFactory()

        cls.portal = TargetPortalFactory()
        cls.flatpage_s_p = FlatPageFactory.create(published=True, title="test", portals=(cls.portal,),
                                                  sources=(cls.source,))
        cls.flatpage_s_p.save()

    @patch('sys.stdout', new_callable=StringIO)
    def test_flatpages(self, mock_stdout):
        command = FakeSyncCommand()
        synchro = SyncRando(command)
        synchro.sync('en')
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'en', 'flatpages.geojson')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'meta', 'en', 'informations',
                                                    'test-0', 'index.html')))

    @patch('sys.stdout', new_callable=StringIO)
    def test_flatpages_sources_portal_filter(self, mock_stdout):
        command = FakeSyncCommand(portal=self.portal.name, source=[self.source.name])
        synchro = SyncRando(command)
        synchro.sync('en')
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'en', 'flatpages.geojson')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'meta', 'en', 'informations',
                                                    'test', 'index.html')))
