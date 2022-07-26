from io import StringIO
import os
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from geotrek.infrastructure.tests.factories import InfrastructureFactory
from geotrek.infrastructure.helpers_sync import SyncRando
from geotrek.common.tests.factories import FakeSyncCommand


class SyncRandoTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.signage = InfrastructureFactory.create(published=True)

    @patch('sys.stdout', new_callable=StringIO)
    def test_infrastructure(self, mock_stdout):
        command = FakeSyncCommand()
        synchro = SyncRando(command)
        synchro.sync('en')
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'en', 'infrastructures.geojson')))
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'static', 'infrastructure',
                                                    'picto-infrastructure.png')))
