from io import StringIO
import os
import shutil
from unittest.mock import patch

from django.test import TestCase

from geotrek.common.factories import FakeSyncCommand
from geotrek.feedback.factories import ReportCategoryFactory
from geotrek.feedback.helpers_sync import SyncRando


class SyncRandoTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super(SyncRandoTestCase, cls).setUpClass()
        cls.report_category = ReportCategoryFactory.create()

    @patch('sys.stdout', new_callable=StringIO)
    def test_feedback(self, stdout):
        command = FakeSyncCommand()
        synchro = SyncRando(command)
        synchro.sync('en')
        self.assertTrue(os.path.exists(os.path.join('var', 'tmp_sync_rando', 'api', 'en', 'feedback',
                                                    'categories.json')))

    def tearDown(self):
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
