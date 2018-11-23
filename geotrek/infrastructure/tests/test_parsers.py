import os
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError

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

    def test_no_file_fail(self):
        with self.assertRaisesRegex(CommandError, "File does not exists at: toto.shp"):
            call_command('loadinfrastructure', 'toto.shp')

    def test_load_both_fail(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        with self.assertRaisesRegex(CommandError, "Only one of --signage and --infrastructure required"):
            call_command('loadinfrastructure', filename, '--infrastructure', '--signage')

    def test_missing_defaults(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        output = StringIO()

        call_command('loadinfrastructure', filename, '--signage', stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_default='name',
                     stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_default='name',
                     condition_default='condition', stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_default='name',
                     condition_default='condition', structure_default='structure', stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_default='name',
                     condition_default='condition', structure_default='structure',
                     description_default='description', stdout=output)

        elements_to_check = ['type', 'name', 'condition', 'structure', 'description', 'implantation']
        self.assertEqual(output.getvalue().count("Field 'None' not found in data source."), 6)
        for element in elements_to_check:
            self.assertIn("Set it with --{0}-field, or set a default value with --{0}-default".format(element),
                          output.getvalue())
