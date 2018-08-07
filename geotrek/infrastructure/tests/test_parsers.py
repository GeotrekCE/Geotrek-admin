import os

from django.core.management import call_command
from django.test import TestCase

from geotrek.infrastructure.factories import SignageFactory, InfrastructureFactory
from geotrek.infrastructure.models import Signage, Infrastructure


class StructureParserTest(TestCase):
    """
    There are 2 structures in the file signage.shp
    """
    def test_load_signage(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        signage = SignageFactory(name="name", implantation_year=2010)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_default='name',
                     condition_default='condition', structure_default='structure',
                     description_default='description', year_default=2010, verbosity=0)
        value = Signage.objects.all()
        self.assertEquals(signage.name, value[1].name)
        self.assertEquals(signage.implantation_year, value[1].implantation_year)
        self.assertEquals(value.count(), 3)

    def test_load_infrastructure(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        building = InfrastructureFactory(name="name", implantation_year=2010)
        call_command('loadinfrastructure', filename, '--infrastructure', type_default='label', name_default='name',
                     condition_default='condition', structure_default='structure',
                     description_default='description', year_default=2010, verbosity=0)
        value = Infrastructure.objects.all()
        self.assertEquals(building.name, value[1].name)
        self.assertEquals(building.implantation_year, value[1].implantation_year)
        self.assertEquals(value.count(), 3)
