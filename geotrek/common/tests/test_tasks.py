# -*- encoding: utf-8 -*-
from django.test import TestCase
from geotrek.common.tasks import import_datas
from geotrek.common.models import FileType


class TasksTest(TestCase):
    def setUp(self):
        self.filetype = FileType.objects.create(type="Photographie")

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
