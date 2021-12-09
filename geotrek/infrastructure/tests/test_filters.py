from geotrek.infrastructure.filters import InfrastructureFilterSet
from geotrek.infrastructure.tests.factories import InfrastructureUsageDifficultyLevelFactory, InfrastructureFactory, InfrastructureMaintenanceDifficultyLevelFactory
from django.test.testcases import TestCase


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
