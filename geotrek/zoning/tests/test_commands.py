import os
from io import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.core.management.base import CommandError
from geotrek.zoning.models import RestrictedArea, RestrictedAreaType


class RestrictedAreasCommandTest(TestCase):

    def setUp(self):
        self.filename_out_in = os.path.join(os.path.dirname(__file__), 'data', 'polygons_in_out.geojson')
        self.filename = os.path.join(os.path.dirname(__file__), 'data', 'city.shp')

    """
    Get Restricted Area
    """
    def test_load_restricted_areas_without_file(self):
        with self.assertRaises(CommandError) as e:
            call_command('loadrestrictedareas')
        self.assertEqual(u'Error: too few arguments', e.exception.message)

    def test_load_cities_without_type(self):
        with self.assertRaises(CommandError) as e:
            call_command('loadrestrictedareas', self.filename_out_in)
        self.assertEqual(u'Error: too few arguments', e.exception.message)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_restrictedareas_with_one_inside_one_outside_within(self):
        output = StringIO()
        call_command('loadrestrictedareas', self.filename_out_in, 'type_area', name='NOM', verbosity=2, stdout=output)
        self.assertEquals(RestrictedArea.objects.count(), 1)
        self.assertEquals(RestrictedAreaType.objects.first().name, 'type_area')
        value = RestrictedArea.objects.first()
        self.assertEquals('coucou', value.name)
        self.assertIn("RestrictedArea Type's type_area created", output.getvalue())
        self.assertIn("Created coucou", output.getvalue())

    @override_settings(SRID=4326, SPATIAL_EXTENT=(10, 11, 11, 12))
    def test_load_restrictedareas_not_within(self):
        call_command('loadrestrictedareas', self.filename_out_in, 'type_area', name='NOM', verbosity=0)
        self.assertEquals(RestrictedArea.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(10, 11, 11, 12))
    def test_load_restrictedareas_not_intersect(self):
        call_command('loadrestrictedareas', self.filename_out_in, 'type_area', '-i', name='NOM', verbosity=0)
        self.assertEquals(RestrictedArea.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_restrictedareas_with_one_inside_one_outside_intersect(self):
        output = StringIO()
        call_command('loadrestrictedareas', self.filename_out_in, 'type_area', '-i', name='NOM', verbosity=2,
                     stdout=output)
        self.assertEquals(RestrictedArea.objects.count(), 2)
        value_1 = RestrictedArea.objects.first()
        self.assertEquals('coucou', value_1.name)
        value_2 = RestrictedArea.objects.last()
        self.assertEquals('lulu', value_2.name)
        output = output.getvalue()
        self.assertIn('Created coucou', output)
        self.assertIn('Created lulu', output)

        output_2 = StringIO()
        call_command('loadrestrictedareas', self.filename_out_in, 'type_area', '-i', name='NOM', verbosity=2,
                     stdout=output_2)
        output = output_2.getvalue()
        self.assertIn('Updated coucou', output)
        self.assertIn('Updated lulu', output)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_cities_no_match_properties(self):
        output = StringIO()
        call_command('loadrestrictedareas', self.filename_out_in, 'type_area', name='toto', stdout=output)
        self.assertIn('NOM, Insee', output.getvalue())
        output_2 = StringIO()
        call_command('loadrestrictedareas', self.filename_out_in, 'type_area', '-i', name='toto', stdout=output_2)
        self.assertIn('NOM, Insee', output.getvalue())

    def test_load_cities_fail_bad_srid(self):
        with self.assertRaises(CommandError) as e:
            call_command('loadrestrictedareas', self.filename, 'type_area', name='NOM', verbosity=0)
        self.assertEqual('SRID is not well configurate, change/add option srid', e.exception.message)
