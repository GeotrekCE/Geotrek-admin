from django.test import TestCase

from geotrek.authent.models import Structure
from geotrek.land.models import LandType, PhysicalType, CirculationType, AuthorizationType
from geotrek.land.tests.factories import CirculationEdgeFactory


class TestModelLand(TestCase):
    def test_physicaltype_value_no_structure(self):
        pt = PhysicalType.objects.create(name='PhysicalType_1')
        self.assertEqual(str(pt), 'PhysicalType_1')

    def test_physicaltype_value_default_structure(self):
        structure = Structure.objects.create(name="Structure_1")
        pt = PhysicalType.objects.create(name='PhysicalType_1', structure=structure)
        self.assertEqual(str(pt), 'PhysicalType_1 (Structure_1)')

    def test_landtype_value_no_structure(self):
        pt = LandType.objects.create(name='LandType_1')
        self.assertEqual(str(pt), 'LandType_1')

    def test_landtype_value_default_structure(self):
        structure = Structure.objects.create(name="Structure_1")
        pt = LandType.objects.create(name='LandType_1', structure=structure)
        self.assertEqual(str(pt), 'LandType_1 (Structure_1)')

    def test_circulationtype_value_no_structure(self):
        pt = CirculationType.objects.create(name='CirculationType_1')
        self.assertEqual(str(pt), 'CirculationType_1')

    def test_circulationtype_value_default_structure(self):
        structure = Structure.objects.create(name="Structure_1")
        pt = CirculationType.objects.create(name='CirculationType_1', structure=structure)
        self.assertEqual(str(pt), 'CirculationType_1 (Structure_1)')

    def test_authorizationtype_value_no_structure(self):
        pt = AuthorizationType.objects.create(name='AuthorizationType_1')
        self.assertEqual(str(pt), 'AuthorizationType_1')

    def test_authorizationtype_value_default_structure(self):
        structure = Structure.objects.create(name="Structure_1")
        pt = AuthorizationType.objects.create(name='AuthorizationType_1', structure=structure)
        self.assertEqual(str(pt), 'AuthorizationType_1 (Structure_1)')

    def test_circulationedge_display(self):
        circulation_edge = CirculationEdgeFactory()
        self.assertEqual(circulation_edge.name_display, f'<a data-pk="{circulation_edge.pk}" href="/circulationedge/{circulation_edge.pk}/" >{circulation_edge.circulation_type}</a>')
