from django.test import TestCase

from geotrek.signage.factories import SealingFactory, BladeTypeFactory, BladeFactory
from geotrek.infrastructure.factories import InfrastructureFactory


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
        with self.assertRaisesRegexp(ValueError, "Expecting a signage"):
            blade.set_topology(infra)
