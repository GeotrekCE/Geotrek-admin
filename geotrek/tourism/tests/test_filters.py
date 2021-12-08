from django.test import TestCase

from geotrek.tourism.tests.factories import TouristicEventFactory
from geotrek.tourism.models import TouristicEvent
from geotrek.tourism.filters import CompletedFilter, BeforeFilter, AfterFilter


class FilterList(TestCase):
    def setUp(self):
        # TouristicEvent : end_date = datetime.today()
        TouristicEventFactory.create()
        self.qs = TouristicEvent.objects.all()

    def test_touristicevent_filter_completed(self):
        cf = CompletedFilter()
        bf = BeforeFilter()
        af = AfterFilter()
        # date <= Today (True) : completed
        # date >= Today (False) : not completed
        self.assertEqual(cf.filter(self.qs, False).count(), 1)
        self.assertEqual(cf.filter(self.qs, True).count(), 0)
        # Before : date <= date_of_filter
        self.assertEqual(bf.filter(self.qs, '2000-01-01').count(), 0)
        self.assertEqual(bf.filter(self.qs, '2150-01-01').count(), 1)
        self.assertEqual(bf.filter(self.qs, '2300-01-01').count(), 1)
        # After : date >= date_of_filter
        self.assertEqual(af.filter(self.qs, '2000-01-01').count(), 1)
        self.assertEqual(af.filter(self.qs, '2150-01-01').count(), 1)
        self.assertEqual(af.filter(self.qs, '2300-01-01').count(), 0)
