import datetime

from django.test import TestCase

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import PathManagerFactory
from geotrek.infrastructure.filters import InfrastructureFilterSet
from geotrek.infrastructure.tests.factories import (InfrastructureUsageDifficultyLevelFactory, InfrastructureFactory,
                                                    InfrastructureMaintenanceDifficultyLevelFactory)
from geotrek.maintenance.tests.factories import InterventionFactory


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
        '''Test usage difficulty filter on infrastructure'''
        data = {
            'usage_difficulty': [self.usage_level_1.pk]
        }
        qs = InfrastructureFilterSet(data=data).qs
        self.assertIn(self.infra_u1, qs)
        self.assertIn(self.infra_u1_m2, qs)
        self.assertNotIn(self.infra_u2_m3, qs)
        self.assertNotIn(self.infra_m2, qs)

    def test_filter_maintenance(self):
        '''Test maintenance difficulty filter on infrastructure'''

        data = {
            'maintenance_difficulty': [self.maintenance_level_2.pk],
        }
        qs = InfrastructureFilterSet(data=data).qs
        self.assertNotIn(self.infra_u1, qs)
        self.assertIn(self.infra_u1_m2, qs)
        self.assertNotIn(self.infra_u2_m3, qs)
        self.assertIn(self.infra_m2, qs)

    def test_filter_combo(self):
        '''Test both usage difficulty filter and maintenance difficulty filter on infrastructure as lower bound'''
        data = {
            'usage_difficulty': [self.usage_level_1.pk],
            'maintenance_difficulty': [self.maintenance_level_2.pk],
        }
        qs = InfrastructureFilterSet(data=data).qs
        self.assertNotIn(self.infra_u1, qs)
        self.assertIn(self.infra_u1_m2, qs)
        self.assertNotIn(self.infra_u2_m3, qs)
        self.assertNotIn(self.infra_m2, qs)


class InfraFilterTestMixin:
    factory = None
    filterset = None

    def login(self):
        user = PathManagerFactory(password='booh')
        self.client.force_login(user=user)

    def test_intervention_filter(self):
        self.login()

        model = self.factory._meta.model
        # We will filter by this year
        year = 2014
        good_date_year = datetime.datetime(year=year, month=2, day=2)
        bad_date_year = datetime.datetime(year=year + 2, month=2, day=2)

        # Bad topology/infrastructure: No intervention
        self.factory()

        # Bad signage: intervention with wrong year
        bad_topo = self.factory()
        InterventionFactory(target=bad_topo, begin_date=bad_date_year)

        # Good signage: intervention with the good year
        good_topo = self.factory()
        InterventionFactory(target=good_topo, begin_date=good_date_year)

        data = {
            'intervention_year': year
        }
        response = self.client.get(model.get_datatablelist_url(), data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['data']), 1)

    def test_duplicate_implantation_year_filter(self):
        self.login()

        model = self.factory._meta.model
        # We will check if this
        year = 2014
        year_t = datetime.datetime(year=year, month=2, day=2)

        # Bad signage: intervention with wrong year
        topo_1 = self.factory()
        InterventionFactory(target=topo_1, begin_date=year_t)

        # Good signage: intervention with the good year
        topo_2 = self.factory()
        InterventionFactory(target=topo_2, begin_date=year_t)

        response = self.client.get(model.get_list_url())
        self.assertContains(response, '<option value="2014">2014</option>', count=1)


class InfrastructureFilterTest(InfraFilterTestMixin, AuthentFixturesTest):
    factory = InfrastructureFactory
    filterset = InfrastructureFilterSet

    def test_none_implantation_year_filter(self):
        self.login()
        model = self.factory._meta.model
        InfrastructureFactory.create()
        response = self.client.get(model.get_list_url())
        self.assertFalse('option value="" selected>None</option' in str(response))

    def test_implantation_year_filter(self):
        self.login()
        model = self.factory._meta.model
        i = InfrastructureFactory.create(implantation_year=2015)
        i2 = InfrastructureFactory.create(implantation_year=2016)
        response = self.client.get(model.get_list_url())

        self.assertContains(response, '<option value="2015">2015</option>')
        self.assertContains(response, '<option value="2016">2016</option>')

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
