from django.test import TestCase

from geotrek.tourism.tests.factories import TouristicContentFactory, TouristicEventFactory
from geotrek.tourism.models import TouristicEvent
from geotrek.tourism.filters import CompletedFilter, TouristicEventFilterSet, TouristicContentFilterSet


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


class TouristicContentFilterTest(TestCase):
    factory = TouristicContentFactory
    filterset = TouristicContentFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = TouristicContentFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        touristic_content1 = TouristicContentFactory.create(provider='my_provider1')
        touristic_content2 = TouristicContentFactory.create(provider='my_provider2')

        filter_set = TouristicContentFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(touristic_content1, filter_set.qs)
        self.assertIn(touristic_content2, filter_set.qs)


class TouristicEventFilterTest(TestCase):
    factory = TouristicEventFactory
    filterset = TouristicEventFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = TouristicEventFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        touristic_event1 = TouristicEventFactory.create(provider='my_provider1')
        touristic_event2 = TouristicEventFactory.create(provider='my_provider2')

        filter_set = TouristicEventFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(touristic_event1, filter_set.qs)
        self.assertIn(touristic_event2, filter_set.qs)
