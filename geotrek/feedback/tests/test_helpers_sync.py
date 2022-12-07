from io import StringIO
import os
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from geotrek.common.tests.factories import FakeSyncCommand
from geotrek.feedback.tests.factories import ReportCategoryFactory
from geotrek.feedback.helpers_sync import SyncRando


class SyncRandoTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report_category = ReportCategoryFactory.create()

    @patch('sys.stdout', new_callable=StringIO)
    def test_feedback(self, stdout):
        command = FakeSyncCommand()
        synchro = SyncRando(command)
        synchro.sync('en')
        self.assertTrue(os.path.exists(os.path.join(settings.VAR_DIR, command.tmp_root, 'api', 'en', 'feedback',
                                                    'categories.json')))
