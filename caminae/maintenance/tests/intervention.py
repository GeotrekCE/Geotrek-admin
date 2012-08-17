from django.test import TestCase

from caminae.infrastructure.factories import InfrastructureFactory, SignageFactory
from caminae.maintenance.factories import InterventionFactory


class InterventionTest(TestCase):
    def test_infrastructure(self):
        i = InterventionFactory.create()
        self.assertFalse(i.on_infrastructure)
        infra = InfrastructureFactory.create()
        i.set_infrastructure(infra)
        self.assertTrue(i.on_infrastructure)
        sign = SignageFactory.create()
        i.set_infrastructure(sign)
        self.assertTrue(i.on_infrastructure)
