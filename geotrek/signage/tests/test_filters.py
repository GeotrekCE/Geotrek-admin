from django.test import TestCase

from geotrek.common.tests.factories import OrganismFactory

from ..filters import BladeFilterSet, SignageFilterSet
from .factories import BladeFactory, SignageFactory


class SignageFilterTest(TestCase):
    factory = SignageFactory
    filterset = SignageFilterSet

    def test_none_implantation_year_filter(self):
        SignageFactory.create()
        form = self.filterset().form.as_p()
        self.assertNotIn('option value="" selected>None</option', form)

    def test_implantation_year_filter(self):
        i = SignageFactory.create(implantation_year=2015)
        i2 = SignageFactory.create(implantation_year=2016)
        form = self.filterset().form.as_p()
        self.assertIn('<option value="2015">2015</option>', form)
        self.assertIn('<option value="2016">2016</option>', form)
        filter = SignageFilterSet(data={'implantation_year': [2015]})
        self.assertTrue(i in filter.qs)
        self.assertFalse(i2 in filter.qs)

    def test_implantation_year_filter_with_str(self):
        i = SignageFactory.create(implantation_year=2015)
        i2 = SignageFactory.create(implantation_year=2016)
        filter_set = SignageFilterSet(data={'implantation_year': 'toto'})
        filter_form = filter_set.form

        self.assertIn('<option value="2015">2015</option>', filter_form.as_p())
        self.assertIn('<option value="2016">2016</option>', filter_form.as_p())

        self.assertIn(i, filter_set.qs)
        self.assertIn(i2, filter_set.qs)

    def test_provider_filter_without_provider(self):
        filter_set = SignageFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        signage1 = SignageFactory.create(provider='my_provider1')
        signage2 = SignageFactory.create(provider='my_provider2')

        filter_set = SignageFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(signage1, filter_set.qs)
        self.assertIn(signage2, filter_set.qs)


class BladeFilterSetTest(TestCase):
    factory = BladeFactory
    filterset = BladeFilterSet

    @classmethod
    def setUpTestData(cls):
        cls.manager = OrganismFactory()
        cls.manager2 = OrganismFactory()

        cls.signage = SignageFactory(manager=cls.manager, code="COUCOU")
        cls.signage2 = SignageFactory(manager=cls.manager2, code="ADIEU")

        cls.blade = cls.factory(signage=cls.signage)
        cls.blade2 = cls.factory(signage=cls.signage2)

    def test_filter_by_organism(self):
        filter = BladeFilterSet(data={'manager': [self.manager.pk,]})
        self.assertIn(self.blade, filter.qs)
        self.assertNotIn(self.blade2, filter.qs)
