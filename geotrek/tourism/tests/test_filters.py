# -*- encoding: UTF-8 -*-
from django.test import TestCase

from geotrek.tourism.factories import TouristicEventFactory
from geotrek.tourism.models import TouristicEvent
from geotrek.tourism.filters import CompletedFilter


class FilterList(TestCase):
    def test_touristicevent_filter(self):
        TouristicEventFactory.create()
        qs = TouristicEvent.objects.all()
        cf = CompletedFilter()
        self.assertEqual(cf.filter(qs, False).count(), 1)
        self.assertEqual(cf.filter(qs, True).count(), 0)
