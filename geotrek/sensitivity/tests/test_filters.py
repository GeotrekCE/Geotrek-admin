from django.test import TestCase

from geotrek.common.models import Provider
from geotrek.sensitivity.filters import SensitiveAreaFilterSet

from .factories import SensitiveAreaFactory


class SensitiveAreaFilterTest(TestCase):
    factory = SensitiveAreaFactory
    filterset = SensitiveAreaFilterSet

    def test_provider_filter_without_provider(self):
        filter_set = SensitiveAreaFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        provider1 = Provider.objects.create(name="Provider1")
        provider2 = Provider.objects.create(name="Provider2")
        sensitive_area1 = SensitiveAreaFactory.create(provider=provider1)
        sensitive_area2 = SensitiveAreaFactory.create(provider=provider2)

        filter_set = SensitiveAreaFilterSet()
        filter_form = filter_set.form

        self.assertIn(
            f'<option value="{provider1.pk}">Provider1</option>', filter_form.as_p()
        )
        self.assertIn(
            f'<option value="{provider2.pk}">Provider2</option>', filter_form.as_p()
        )

        self.assertIn(sensitive_area1, filter_set.qs)
        self.assertIn(sensitive_area2, filter_set.qs)
