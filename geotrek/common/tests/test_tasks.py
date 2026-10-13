import datetime
import json
import os
from io import StringIO
from unittest.mock import patch

from dateutil.relativedelta import relativedelta
from django.test import TestCase, override_settings

from geotrek.common.models import FileType, Organism
from geotrek.common.parsers import ExcelParser, GlobalImportError
from geotrek.common.tasks import (
    get_parser_class,
    import_datas,
    import_datas_from_web,
    update_annual_vigilance_areas,
)
from geotrek.tourism.models import TouristicEvent
from geotrek.zoning.models import VigilancePeriod
from geotrek.zoning.tests.factories import VigilanceAreaFactory


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

    def test_get_parser_class_from_var_dir(self):
        with override_settings(VAR_DIR=os.path.join(os.path.dirname(__file__), "data")):
            parser_cls = get_parser_class("parsers", "CustomParser")
            self.assertEqual(parser_cls.__name__, "CustomParser")

    def test_update_years(self):
        today = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        start_date = today - datetime.timedelta(days=30)
        vigilance_area = VigilanceAreaFactory.create()

        def create_period(end_date, annual):
            return VigilancePeriod.objects.create(
                vigilance_area=vigilance_area,
                start_date=start_date,
                end_date=end_date,
                annual=annual,
            )

        finished_annual = create_period(today - one_day, annual=True)
        ongoing_annual = create_period(today + one_day, annual=True)
        finished_not_annual = create_period(today - one_day, annual=False)

        task = update_annual_vigilance_areas.apply()

        self.assertEqual(task.status, "SUCCESS")

        def assert_dates(period, expected_start, expected_end):
            period.refresh_from_db()
            self.assertEqual(period.start_date, expected_start)
            self.assertEqual(period.end_date, expected_end)

        assert_dates(
            finished_annual,
            start_date + relativedelta(years=1),
            today - one_day + relativedelta(years=1),
        )
        assert_dates(ongoing_annual, start_date, today + one_day)
        assert_dates(finished_not_annual, start_date, today - one_day)
