from django.test import TestCase

from geotrek.common.models import Provider
from geotrek.land.tests.test_filters import LandFiltersTest
from geotrek.trekking.filters import POIFilterSet, ServiceFilterSet, TrekFilterSet

from .factories import POIFactory, ServiceFactory, TrekFactory


class TrekFilterLandTest(LandFiltersTest):
    filterclass = TrekFilterSet

    def test_land_filters_are_well_setup(self):
        filterset = TrekFilterSet()
        self.assertIn("work", filterset.filters)

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
        provider1 = Provider.objects.create(name="Provider1")
        provider2 = Provider.objects.create(name="Provider2")
        trek1 = TrekFactory.create(provider=provider1)
        trek2 = TrekFactory.create(provider=provider2)

        filter_set = TrekFilterSet()
        filter_form = filter_set.form

        self.assertIn(
            f'<option value="{provider1.pk}">Provider1</option>', filter_form.as_p()
        )
        self.assertIn(
            f'<option value="{provider2.pk}">Provider2</option>', filter_form.as_p()
        )

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
        provider1 = Provider.objects.create(name="Provider1")
        provider2 = Provider.objects.create(name="Provider2")
        poi1 = POIFactory.create(provider=provider1)
        poi2 = POIFactory.create(provider=provider2)

        filter_set = POIFilterSet()
        filter_form = filter_set.form

        self.assertIn(
            f'<option value="{provider1.pk}">Provider1</option>', filter_form.as_p()
        )
        self.assertIn(
            f'<option value="{provider2.pk}">Provider2</option>', filter_form.as_p()
        )

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
        provider1 = Provider.objects.create(name="Provider1")
        provider2 = Provider.objects.create(name="Provider2")
        service1 = ServiceFactory.create(provider=provider1)
        service2 = ServiceFactory.create(provider=provider2)

        filter_set = ServiceFilterSet()
        filter_form = filter_set.form

        self.assertIn(
            f'<option value="{provider1.pk}">Provider1</option>', filter_form.as_p()
        )
        self.assertIn(
            f'<option value="{provider2.pk}">Provider2</option>', filter_form.as_p()
        )

        self.assertIn(service1, filter_set.qs)
        self.assertIn(service2, filter_set.qs)
