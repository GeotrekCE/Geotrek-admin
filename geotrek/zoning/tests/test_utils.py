import datetime

from django.test import TestCase

from geotrek.zoning.utils import weekday_between


class WeekdayBetweenTest(TestCase):
    def test_weekday_between_on_one_year(self):
        start_date = datetime.date(year=2026, month=8, day=4)
        end_date = datetime.date(year=2026, month=8, day=7)

        weekdays = weekday_between(start_date, end_date)

        self.assertEqual(weekdays, [1, 2, 3, 4])

    def test_weekday_between_on_two_years(self):
        start_date = datetime.date(year=2026, month=8, day=1)
        end_date = datetime.date(year=2026, month=8, day=5)

        weekdays = weekday_between(start_date, end_date)

        self.assertEqual(weekdays, [5, 6, 0, 1, 2])

    def test_weekday_between_with_more_than_twelve_months(self):
        start_date = datetime.date(year=2026, month=8, day=1)
        end_date = datetime.date(year=2026, month=8, day=12)

        weekdays = weekday_between(start_date, end_date)

        self.assertEqual(weekdays, [0, 1, 2, 3, 4, 5, 6])
