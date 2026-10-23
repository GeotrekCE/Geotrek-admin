import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from geotrek.zoning.utils import weekday_between


class WeekdayBetweenTest(TestCase):
    def test_weekday_between_on_one_year(self):
        start_date = "2026-08-04"
        end_date = "2026-08-07"

        weekdays = weekday_between(start_date, end_date)

        self.assertEqual(sorted(weekdays), [1, 2, 3, 4])

    def test_weekday_between_on_two_years(self):
        start_date = "2026-08-01"
        end_date = "2026-08-05"

        weekdays = weekday_between(start_date, end_date)

        self.assertEqual(sorted(weekdays), [0, 1, 2, 5, 6])

    def test_weekday_between_with_more_than_7_days(self):
        start_date = "2026-08-01"
        end_date = "2026-08-12"

        weekdays = weekday_between(start_date, end_date)

        self.assertEqual(sorted(weekdays), [0, 1, 2, 3, 4, 5, 6])

    default = datetime.datetime(2026, 8, 4).date()

    def test_wrong_date_format(self):
        start_date = "01-05-2027"
        end_date = "01-05-2027"

        with self.assertRaises(ValueError):
            weekday_between(start_date, end_date)

    def test_null_dates(self):
        start_date = None
        end_date = "01-05-2027"

        with self.assertRaises(ValidationError):
            weekday_between(start_date, end_date)
