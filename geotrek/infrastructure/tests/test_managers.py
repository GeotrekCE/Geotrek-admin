from django.test import TestCase

from geotrek.infrastructure.models import InfrastructureCondition
from geotrek.infrastructure.tests.factories import InfrastructureConditionFactory


class InfrastructureConditionTest(TestCase):
    def test_manager(self):
        it1 = InfrastructureConditionFactory.create()
        it2 = InfrastructureConditionFactory.create()
        it3 = InfrastructureConditionFactory.create()

        self.assertCountEqual(InfrastructureCondition.objects.all(), [it1, it2, it3])
