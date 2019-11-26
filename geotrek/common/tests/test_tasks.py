from django.test import TestCase
from geotrek.common.tasks import import_datas, import_datas_from_web
from geotrek.common.models import Organism
from geotrek.common.parsers import ExcelParser, GlobalImportError


class OrganismParser(ExcelParser):
    model = Organism
    fields = {'organism': 'nOm'}


class TasksTest(TestCase):
    def test_import_datas_message_exception(self):
        self.assertRaisesMessage(
            ImportError,
            "Failed to import parser class 'haricot' from module 'toto'",
            import_datas,
            filename='bombadil',
            name='haricot',
            module='toto'
        )

    def test_import_datas_from_web_message_exception(self):
        self.assertRaisesMessage(
            ImportError,
            "Failed to import parser class 'haricot' from module 'toto'",
            import_datas_from_web,
            filename='bombadil',
            name='haricot',
            module='toto'
        )

    def test_import_datas_from_web_other_exception(self):
        self.assertRaisesMessage(
            GlobalImportError,
            'Filename is required',
            import_datas_from_web,
            name='OrganismParser',
            module='geotrek.common.tests.test_tasks'
        )

    def test_import_datas_other_exception(self):
        self.assertRaisesMessage(
            GlobalImportError,
            'File does not exists at: bombadil',
            import_datas,
            filename='bombadil',
            name='OrganismParser',
            module='geotrek.common.tests.test_tasks'
        )
