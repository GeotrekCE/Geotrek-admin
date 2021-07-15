from unittest.mock import patch
from io import StringIO

from geotrek.celery_tasks import debug_task

from django.test.testcases import TestCase


class CeleryTests(TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def test_debug_task(self, mocked_stdout):
        task = debug_task.apply(logfile='test_logfile')
        self.assertEqual(task.status, 'SUCCESS')
        self.assertIn('test_logfile', mocked_stdout.getvalue())
