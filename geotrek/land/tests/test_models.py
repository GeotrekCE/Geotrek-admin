from django.test import TestCase

from geotrek.land.models import LandType, PhysicalType


class TestModelLand(TestCase):
    def test_physicaltype_value_no_structure(self):
        pt = PhysicalType.objects.create(name='PhysicalType_1', structure=None)
        self.assertEqual(str(pt), 'PhysicalType_1')

    def test_physicaltype_value_default_structure(self):
        pt = PhysicalType.objects.create(name='PhysicalType_1')
        self.assertEqual(str(pt), 'PhysicalType_1 (%s)' % pt.structure)

    def test_landtype_value_no_structure(self):
        pt = LandType.objects.create(name='LandType_1', structure=None)
        self.assertEqual(str(pt), 'LandType_1')

    def test_landtype_value_default_structure(self):
        pt = LandType.objects.create(name='LandType_1')
        self.assertEqual(str(pt), 'LandType_1 (%s)' % pt.structure)
