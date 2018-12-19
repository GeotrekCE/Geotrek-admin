import os
from StringIO import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.core.management.base import CommandError

from geotrek.infrastructure.factories import SignageFactory, InfrastructureFactory
from geotrek.infrastructure.models import Signage, Infrastructure
from geotrek.authent.factories import StructureFactory
from geotrek.authent.models import Structure


class InfrastructureCommandTest(TestCase):
    """
    There are 2 infrastructures in the file signage.shp
    """
    def test_load_signage(self):
        StructureFactory.create(name='structure')
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
        output = StringIO()
        structure = StructureFactory.create(name='structure')
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        building = InfrastructureFactory(name="name", implantation_year=2010)
        call_command('loadinfrastructure', filename, '--infrastructure', type_default='label', name_default='name',
                     condition_default='condition', structure_default='structure',
                     description_default='description', year_default=2010, verbosity=2, stdout=output)
        self.assertIn('Infrastructures will be linked to %s' % structure, output.getvalue())
        self.assertIn('2 objects created.', output.getvalue())
        value = Infrastructure.objects.all()
        self.assertEquals(building.name, value[1].name)
        self.assertEquals(building.implantation_year, value[1].implantation_year)
        self.assertEquals(value.count(), 3)

    def test_load_infrastructure_with_fields(self):
        output = StringIO()
        structure = StructureFactory.create(name='structure')
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        InfrastructureFactory(name="name")
        call_command('loadinfrastructure', filename, '--infrastructure', type_field='label', name_field='name',
                     condition_field='condition', structure_default='structure',
                     description_field='descriptio', year_field='year', verbosity=1, stdout=output)
        self.assertIn('Infrastructures will be linked to %s' % structure, output.getvalue())
        self.assertIn("InfrastructureType 'type (PNX)' created", output.getvalue())
        self.assertIn("Condition Type 'condition (PNX)' created", output.getvalue())
        value = Infrastructure.objects.all()
        names = [val.name for val in value]
        years = [val.implantation_year for val in value]
        self.assertIn('coucou', names)
        self.assertIn(2010, years)
        self.assertIn(2012, years)
        self.assertEquals(value.count(), 3)

    def test_load_infrastructure_without_structure_default_one_structure(self):
        output = StringIO()
        InfrastructureFactory(name="name")
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        call_command('loadinfrastructure', filename, '--infrastructure', type_default='label', name_default='name',
                     verbosity=1, stdout=output)
        structure = Structure.objects.first()
        self.assertIn('Infrastructures will be linked to %s' % structure, output.getvalue())

    def test_no_file_fail(self):
        with self.assertRaises(CommandError) as cm:
            call_command('loadinfrastructure', 'toto.shp')
        self.assertEqual(cm.exception.message, "File does not exists at: toto.shp")

    def test_load_both_fail(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        with self.assertRaises(CommandError) as cm:
            call_command('loadinfrastructure', filename, '--infrastructure', '--signage')
        self.assertEqual(cm.exception.message, "Only one of --signage and --infrastructure required")

    def test_missing_defaults(self):
        StructureFactory.create(name='structure')
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        output = StringIO()

        call_command('loadinfrastructure', filename, '--signage', stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', stdout=output)

        elements_to_check = ['type', 'name']
        self.assertEqual(output.getvalue().count("Field 'None' not found in data source."), 2)
        for element in elements_to_check:
            self.assertIn("Set it with --{0}-field, or set a default value with --{0}-default".format(element),
                          output.getvalue())

    def test_multiple_structure_fail_no_default(self):
        structure1 = StructureFactory.create(name='structure')
        structure2 = StructureFactory.create(name='structure2')
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        output = StringIO()
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_default='name',
                     stdout=output)
        self.assertIn("%s, %s" % (structure1, structure2), output.getvalue())

    def test_no_structure_fail(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        output = StringIO()
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_default='name',
                     stdout=output)
        self.assertIn('There is no structure in your instance', output.getvalue())

    def test_wrong_structure_in_default_fail(self):
        StructureFactory.create(name='structure')
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        output = StringIO()
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_default='name',
                     structure_default='wrong_structure', stdout=output)
        self.assertIn("Infrastructure wrong_structure set in options doesn't exist", output.getvalue())

    def test_wrong_fields_fail(self):
        StructureFactory.create(name='structure')
        filename = os.path.join(os.path.dirname(__file__), 'data', 'signage.shp')
        output = StringIO()
        call_command('loadinfrastructure', filename, '--signage', type_field='wrong_type_field', stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_field='wrong_name_field',
                     stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_field='name',
                     condition_field='wrong_condition_field', stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_field='name',
                     description_field='wrong_description_field', stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_field='name',
                     year_field='wrong_implantation_year_field', stdout=output)
        call_command('loadinfrastructure', filename, '--signage', type_default='label', name_field='name',
                     structure_field='wrong_structure_field', stdout=output)
        elements_to_check = ['wrong_type_field', 'wrong_name_field', 'wrong_condition_field',
                             'wrong_description_field', 'wrong_implantation_year_field', 'wrong_structure_field']
        self.assertEqual(output.getvalue().count("set a default value"), 2)
        self.assertEqual(output.getvalue().count("Change your"), 4)
        self.assertEqual(output.getvalue().count("set a default value"), 2)
        for element in elements_to_check:
            self.assertIn("Field '{}' not found in data source".format(element),
                          output.getvalue())

    def test_line_fail_rolling_back(self):
        StructureFactory.create(name='structure')
        filename = os.path.join(os.path.dirname(__file__), 'data', 'line.geojson')
        output = StringIO()
        with self.assertRaises(IndexError):
            call_command('loadinfrastructure', filename, '--signage', type_default='label', name_default='name',
                         stdout=output)
        self.assertIn('An error occured, rolling back operations.', output.getvalue())
        self.assertEqual(Infrastructure.objects.count(), 0)
