from django.test import TestCase

from geotrek.land.tests.test_filters import LandFiltersTest

from geotrek.trekking.filters import TrekFilterSet, POIFilterSet, ServiceFilterSet
from .factories import TrekFactory, POIFactory, ServiceFactory


class TrekFilterLandTest(LandFiltersTest):
    filterclass = TrekFilterSet

    def test_land_filters_are_well_setup(self):
        filterset = TrekFilterSet()
        self.assertIn('work', filterset.filters)

    def create_pair_of_distinct_path(self):
        useless_path, seek_path = super().create_pair_of_distinct_path()
        self.create_pair_of_distinct_topologies(TrekFactory, useless_path, seek_path)
        return useless_path, seek_path


class TrekFilterTest(TestCase):
    factory = TrekFactory
    filterset = TrekFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = TrekFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        trek1 = TrekFactory.create(provider='my_provider1')
        trek2 = TrekFactory.create(provider='my_provider2')

        filter_set = TrekFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(trek1, filter_set.qs)
        self.assertIn(trek2, filter_set.qs)


class POIFilterTest(TestCase):
    factory = POIFactory
    filterset = POIFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = POIFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        poi1 = POIFactory.create(provider='my_provider1')
        poi2 = POIFactory.create(provider='my_provider2')

        filter_set = POIFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(poi1, filter_set.qs)
        self.assertIn(poi2, filter_set.qs)


class ServiceFilterTest(TestCase):
    factory = ServiceFactory
    filterset = ServiceFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = ServiceFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        service1 = ServiceFactory.create(provider='my_provider1')
        service2 = ServiceFactory.create(provider='my_provider2')

        filter_set = ServiceFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(service1, filter_set.qs)
        self.assertIn(service2, filter_set.qs)
