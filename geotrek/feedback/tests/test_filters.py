from django.test import TestCase
from django.views.generic.dates import timezone_today
from freezegun.api import freeze_time

from geotrek.feedback.filters import ReportFilterSet
from geotrek.feedback.tests.factories import ReportFactory


class ReportFilterTest(TestCase):
    @classmethod
    @freeze_time("2020-01-01")
    def setUpTestData(cls):
        cls.report1 = ReportFactory()

    def setUp(self):
        self.report2 = ReportFactory()

    def test_empty_filters(self):
        filter_set = ReportFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(2, filter_set.qs.count())

        self.assertIn(self.report1, filter_set.qs)
        self.assertIn(self.report2, filter_set.qs)

    def test_year_insert_filter(self):
        current_year = timezone_today().year
        filter_set = ReportFilterSet(data={"year_insert": [2020]})
        filter_form = filter_set.form

        self.assertIn('<option value="2020">2020</option>', filter_form.as_p())
        self.assertIn(
            f'<option value="{current_year}">{current_year}</option>',
            filter_form.as_p(),
        )

        self.assertTrue(filter_form.is_valid())
        self.assertIn(self.report1, filter_set.qs)
        self.assertNotIn(self.report2, filter_set.qs)

    def test_year_update_filter(self):
        current_year = timezone_today().year
        filter_set = ReportFilterSet(data={"year_update": [current_year]})
        filter_form = filter_set.form

        self.assertIn('<option value="2020">2020</option>', filter_form.as_p())
        self.assertIn(
            f'<option value="{current_year}">{current_year}</option>',
            filter_form.as_p(),
        )

        self.assertTrue(filter_form.is_valid())
        self.assertNotIn(self.report1, filter_set.qs)
        self.assertIn(self.report2, filter_set.qs)
