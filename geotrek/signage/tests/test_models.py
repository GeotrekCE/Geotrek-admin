from django.test import TestCase

from geotrek.signage.tests.factories import BladeFactory, BladeTypeFactory, SealingFactory, SignageFactory
from geotrek.infrastructure.tests.factories import InfrastructureFactory


class SealingModelTest(TestCase):
    def test_sealing_value(self):
        sealing = SealingFactory.create(label='sealing_1', structure=None)
        self.assertEqual(str(sealing), 'sealing_1')


class BladeTypeModelTest(TestCase):
    def test_bladetype_value(self):
        type = BladeTypeFactory.create(label='type_1', structure=None)
        self.assertEqual(str(type), 'type_1')


class BladeModelTest(TestCase):
    def test_set_topology_other_error(self):
        blade = BladeFactory.create()
        infra = InfrastructureFactory.create()
        with self.assertRaisesRegex(ValueError, "Expecting a signage"):
            blade.set_topology(infra)


class SignageModelTest(TestCase):
    def test_order_blades_C(self):
        signage = SignageFactory.create(code="XR2")
        blade_2 = BladeFactory.create(number='A', signage=signage)
        blade = BladeFactory.create(number='*BL', signage=signage)
        self.assertEqual([blade, blade_2], list(signage.order_blades))
