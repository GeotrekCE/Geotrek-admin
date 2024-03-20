from django.test import TestCase

from geotrek.infrastructure.filters import InfrastructureFilterSet

from .factories import (
    InfrastructureFactory,
    InfrastructureMaintenanceDifficultyLevelFactory,
    InfrastructureUsageDifficultyLevelFactory,
)


class DifficultyLeversFilterTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.usage_level_1 = InfrastructureUsageDifficultyLevelFactory()
        cls.usage_level_2 = InfrastructureUsageDifficultyLevelFactory()
        cls.maintenance_level_1 = InfrastructureMaintenanceDifficultyLevelFactory()
        cls.maintenance_level_2 = InfrastructureMaintenanceDifficultyLevelFactory()
        cls.maintenance_level_3 = InfrastructureMaintenanceDifficultyLevelFactory()
        cls.infra_u1 = InfrastructureFactory(usage_difficulty=cls.usage_level_1)
        cls.infra_u1_m2 = InfrastructureFactory(usage_difficulty=cls.usage_level_1, maintenance_difficulty=cls.maintenance_level_2)
        cls.infra_u2_m3 = InfrastructureFactory(usage_difficulty=cls.usage_level_2, maintenance_difficulty=cls.maintenance_level_3)
        cls.infra_m2 = InfrastructureFactory(maintenance_difficulty=cls.maintenance_level_2)

    def test_filter_usages(self):
        """ Test usage difficulty filter on infrastructure """
        data = {
            'usage_difficulty': [self.usage_level_1.pk]
        }
        qs = InfrastructureFilterSet(data=data).qs
        self.assertIn(self.infra_u1, qs)
        self.assertIn(self.infra_u1_m2, qs)
        self.assertNotIn(self.infra_u2_m3, qs)
        self.assertNotIn(self.infra_m2, qs)

    def test_filter_maintenance(self):
        """Test maintenance difficulty filter on infrastructure"""

        data = {
            'maintenance_difficulty': [self.maintenance_level_2.pk],
        }
        qs = InfrastructureFilterSet(data=data).qs
        self.assertNotIn(self.infra_u1, qs)
        self.assertIn(self.infra_u1_m2, qs)
        self.assertNotIn(self.infra_u2_m3, qs)
        self.assertIn(self.infra_m2, qs)

    def test_filter_combo(self):
        """Test both usage difficulty filter and maintenance difficulty filter on infrastructure as lower bound"""
        data = {
            'usage_difficulty': [self.usage_level_1.pk],
            'maintenance_difficulty': [self.maintenance_level_2.pk],
        }
        qs = InfrastructureFilterSet(data=data).qs
        self.assertNotIn(self.infra_u1, qs)
        self.assertIn(self.infra_u1_m2, qs)
        self.assertNotIn(self.infra_u2_m3, qs)
        self.assertNotIn(self.infra_m2, qs)


class InfrastructureFilterTest(TestCase):
    factory = InfrastructureFactory
    filterset = InfrastructureFilterSet

    def test_none_implantation_year_filter(self):
        self.factory.create()
        form = self.filterset().form
        self.assertNotIn('option value="" selected>None</option', form.as_p())

    def test_implantation_year_filter(self):
        i = InfrastructureFactory.create(implantation_year=2015)
        i2 = InfrastructureFactory.create(implantation_year=2016)
        form = self.filterset().form

        self.assertIn('<option value="2015">2015</option>', form.as_p())
        self.assertIn('<option value="2016">2016</option>', form.as_p())

        filter = InfrastructureFilterSet(data={'implantation_year': [2015]})
        self.assertTrue(i in filter.qs)
        self.assertFalse(i2 in filter.qs)

    def test_implantation_year_filter_with_str(self):
        i = InfrastructureFactory.create(implantation_year=2015)
        i2 = InfrastructureFactory.create(implantation_year=2016)
        filter_set = InfrastructureFilterSet(data={'implantation_year': 'toto'})
        filter_form = filter_set.form.as_p()
        self.assertIn('<option value="2015">2015</option>', filter_form)
        self.assertIn('<option value="2016">2016</option>', filter_form)

        self.assertIn(i, filter_set.qs)
        self.assertIn(i2, filter_set.qs)

    def test_provider_filter_without_provider(self):
        filter_set = InfrastructureFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        infrastructure1 = InfrastructureFactory.create(provider='my_provider1')
        infrastructure2 = InfrastructureFactory.create(provider='my_provider2')

        filter_set = InfrastructureFilterSet()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(infrastructure1, filter_set.qs)
        self.assertIn(infrastructure2, filter_set.qs)
