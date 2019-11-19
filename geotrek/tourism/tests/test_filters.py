from datetime import datetime, timedelta

from django.test import TestCase

from geotrek.tourism.factories import TouristicEventFactory
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
        self.assertEqual(bf.filter(self.qs, datetime.today()).count(), 1)
        self.assertEqual(bf.filter(self.qs, datetime.today() - timedelta(1)).count(), 0)
        # After : date >= date_of_filter
        self.assertEqual(af.filter(self.qs, datetime.today()).count(), 1)
        self.assertEqual(af.filter(self.qs, datetime.today() - timedelta(1)).count(), 1)
