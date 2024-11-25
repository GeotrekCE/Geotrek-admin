from django.test import TestCase

from geotrek.maintenance.tests.factories import InfrastructureInterventionFactory

from ..filters import InfrastructureFilterSet
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
        self.factory()
        form = self.filterset().form
        self.assertNotIn('option value="" selected>None</option', form.as_p())

    def test_implantation_year_filter(self):
        i = self.factory(implantation_year=2015)
        i2 = self.factory(implantation_year=2016)
        form = self.filterset().form

        self.assertIn('<option value="2015">2015</option>', form.as_p())
        self.assertIn('<option value="2016">2016</option>', form.as_p())

        filterset = self.filterset(data={'implantation_year': [2015]})
        self.assertTrue(i in filterset.qs)
        self.assertFalse(i2 in filterset.qs)

    def test_implantation_year_filter_with_str(self):
        i = self.factory(implantation_year=2015)
        i2 = self.factory(implantation_year=2016)
        filter_set = self.filterset(data={'implantation_year': 'toto'})
        filter_form = filter_set.form.as_p()
        self.assertIn('<option value="2015">2015</option>', filter_form)
        self.assertIn('<option value="2016">2016</option>', filter_form)

        self.assertIn(i, filter_set.qs)
        self.assertIn(i2, filter_set.qs)

    def test_form_should_have_signage_intervention_year_choices(self):
        InfrastructureInterventionFactory(begin_date='2015-01-01')
        InfrastructureInterventionFactory(begin_date='2020-01-01')
        filter_set = self.filterset()
        choice_values = [choice[0] for choice in filter_set.form.fields['intervention_year'].choices]
        self.assertIn(2015, choice_values)
        self.assertIn(2020, choice_values)
        self.assertNotIn(2022, choice_values)

    def test_filter_by_intervention_year(self):
        filtered_infra_intervention = InfrastructureInterventionFactory(begin_date='2015-01-01')
        non_filtered_infra_intervention = InfrastructureInterventionFactory(begin_date='2020-01-01')
        filter_set = self.filterset(data={'intervention_year': [2015]})
        qs = filter_set.qs

        self.assertEqual(1, len(qs))
        self.assertIn(filtered_infra_intervention.target, qs)
        self.assertNotIn(non_filtered_infra_intervention.target, qs)

    def test_provider_filter_without_provider(self):
        filter_set = self.filterset(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(0, filter_set.qs.count())

    def test_provider_filter_with_providers(self):
        infrastructure1 = self.factory(provider='my_provider1')
        infrastructure2 = self.factory(provider='my_provider2')

        filter_set = self.filterset()
        filter_form = filter_set.form

        self.assertIn('<option value="my_provider1">my_provider1</option>', filter_form.as_p())
        self.assertIn('<option value="my_provider2">my_provider2</option>', filter_form.as_p())

        self.assertIn(infrastructure1, filter_set.qs)
        self.assertIn(infrastructure2, filter_set.qs)
