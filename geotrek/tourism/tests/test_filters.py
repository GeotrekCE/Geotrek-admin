from django.test import TestCase

from geotrek.tourism.tests.factories import TouristicEventFactory
from geotrek.tourism.models import TouristicEvent
from geotrek.tourism.filters import CompletedFilter, TouristicEventFilterSet


class TouristicEventFilterSetTestCase(TestCase):
    filter_class = TouristicEventFilterSet

    @classmethod
    def setUpTestData(cls):
        # TouristicEvent : end_date = datetime.today()
        TouristicEventFactory.create()
        cls.qs = TouristicEvent.objects.all()

    def test_touristicevent_filter_completed(self):
        cf = CompletedFilter()
        # date <= Today (True) : completed
        # date >= Today (False) : not completed
        self.assertEqual(cf.filter(self.qs, False).count(), 1)
        self.assertEqual(cf.filter(self.qs, True).count(), 0)

    def test_before_filter(self):
        filter = self.filter_class(data={'before': '2000-01-01'})
        # Before : date <= date_of_filter
        self.assertEqual(filter.qs.count(), 0)
        filter = self.filter_class(data={'before': '2150-01-01'})
        self.assertEqual(filter.qs.count(), 1)
        filter = self.filter_class(data={'before': '2300-01-01'})
        self.assertEqual(filter.qs.count(), 1)

    def test_after_filter(self):
        filter = self.filter_class(data={'after': '2000-01-01'})
        self.assertEqual(filter.qs.count(), 1)
        filter = self.filter_class(data={'after': '2150-01-01'})
        self.assertEqual(filter.qs.count(), 1)
        filter = self.filter_class(data={'after': '2300-01-01'})
        self.assertEqual(filter.qs.count(), 0)
