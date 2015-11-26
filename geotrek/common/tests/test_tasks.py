# -*- encoding: utf-8 -*-

import os
from django.test import TestCase
from geotrek.common.tasks import import_datas
from geotrek.common.models import FileType


class TasksTest(TestCase):
    def setUp(self):
        self.filetype = FileType.objects.create(type=u"Photographie")

    def test_import_exceptions(self):
        self.assertRaises(
            ImportError, import_datas, filename='bombadil', class_name='haricot', module_name='toto')

    def test_import_message_exception(self):
        self.assertRaisesMessage(
            ImportError,
            "Failed to import parser class 'haricot' from module 'toto'",
            import_datas,
            filename='bombadil',
            class_name='haricot',
            module_name='toto'
        )

    def test_import_return(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'organism.xls')
        task = import_datas.delay('AttachmentParser', filename, 'geotrek.common.tests.test_parsers')

        self.assertEqual(task.status, 'SUCCESS')
        self.assertEqual(task.result['parser'], 'AttachmentParser')
        self.assertEqual(task.result['filename'], 'organism.xls')
        self.assertEqual(task.result['current'], 100)
        self.assertEqual(task.result['total'], 100)
        self.assertEqual(task.result['name'], 'geotrek.common.import-file')
