import json
import os
from io import StringIO
from unittest.mock import patch

from django.test import TestCase

from geotrek.common.models import FileType, Organism
from geotrek.common.parsers import ExcelParser, GlobalImportError
from geotrek.common.tasks import import_datas, import_datas_from_web
from geotrek.tourism.models import TouristicEvent


class OrganismParser(ExcelParser):
    model = Organism
    fields = {"organism": "nOm"}


class TasksTest(TestCase):
    def test_import_datas_message_exception(self):
        self.assertRaisesMessage(
            ImportError,
            "No module named 'toto'",
            import_datas,
            filename="bombadil",
            name="haricot",
            module="toto",
        )

    def test_import_datas_from_web_message_exception(self):
        self.assertRaisesMessage(
            ImportError,
            "No module named 'toto'",
            import_datas_from_web,
            filename="bombadil",
            name="haricot",
            module="toto",
        )

    def test_import_datas_from_web_other_exception(self):
        self.assertRaisesMessage(
            GlobalImportError,
            "Filename or url is required",
            import_datas_from_web,
            name="OrganismParser",
            module="geotrek.common.tests.test_tasks",
        )

    def test_import_datas_other_exception(self):
        self.assertRaisesMessage(
            GlobalImportError,
            "File does not exists at: bombadil",
            import_datas,
            filename="bombadil",
            name="OrganismParser",
            module="geotrek.common.tests.test_tasks",
        )

    @patch("sys.stdout", new_callable=StringIO)
    def test_import_data_task(self, mock):
        filename = os.path.join(os.path.dirname(__file__), "data", "organism.xls")
        task = import_datas.s(
            filename=filename,
            name="OrganismParser",
            module="geotrek.common.tests.test_tasks",
        ).apply()
        log = mock.getvalue()
        self.assertEqual(Organism.objects.count(), 1)
        organism = Organism.objects.get()
        self.assertEqual(organism.organism, "2.0")
        self.assertEqual("100%", log)
        self.assertEqual(task.status, "SUCCESS")

    @patch("requests.get")
    @patch("sys.stdout", new_callable=StringIO)
    def test_import_data_from_web_task(self, mock, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "apidaeEvent.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json
        mocked.return_value.content = b"Fake image"
        FileType.objects.create(type="Photographie")

        task = import_datas_from_web.s(
            url="http://url_test.com",
            name="TouristicEventApidaeParser",
            module="geotrek.tourism.parsers",
        ).apply()
        self.assertEqual(TouristicEvent.objects.count(), 1)
        event = TouristicEvent.objects.get()
        self.assertEqual(event.eid, "323154")
        self.assertEqual(task.status, "SUCCESS")
