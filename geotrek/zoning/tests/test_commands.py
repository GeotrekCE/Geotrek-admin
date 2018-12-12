import os
from StringIO import StringIO

from django.core.management import call_command
from django.test import TestCase, override_settings
from django.core.management.base import CommandError
from django.contrib.gis.gdal import GDALException
from geotrek.zoning.models import City


class CitiesCommandTest(TestCase):

    def setUp(self):
        self.filename = os.path.join(os.path.dirname(__file__), 'data', 'city.shp')
        self.filename_out_in = os.path.join(os.path.dirname(__file__), 'data', 'polygons_in_out.geojson')
    """
    Get cities
    """
    def test_load_cities_without_spatial_extent(self):
        call_command('loadcities', self.filename, name='NOM', code='Insee', srid=2154, verbosity=0)
        self.assertEquals(City.objects.count(), 0)

    @override_settings(SPATIAL_EXTENT=(0, 6000000.0, 400000.0, 7000000))
    def test_load_cities_within_spatial_extent(self):
        output = StringIO()
        call_command('loadcities', self.filename, name='NOM', code='Insee', srid=2154, verbosity=2, stdout=output)
        value = City.objects.first()
        self.assertEquals('99999', value.code)
        self.assertEquals('Trifouilli-les-Oies', value.name)
        self.assertEquals(City.objects.count(), 1)
        self.assertIn('Created Trifouilli-les-Oies', output.getvalue())
        call_command('loadcities', self.filename, name='NOM', code='Insee', srid=2154, verbosity=2, stdout=output)
        self.assertIn('Updated Trifouilli-les-Oies', output.getvalue())

    def test_load_cities_fail_bad_srid(self):
        with self.assertRaises(CommandError) as e:
            call_command('loadcities', self.filename, name='NOM', code='Insee', verbosity=0)
        self.assertEqual('SRID is not well configurate, change/add option srid', e.exception.message)

    def test_load_cities_without_file(self):
        with self.assertRaises(GDALException) as e:
            call_command('loadcities', 'toto.geojson', name='NOM', code='Insee', srid=2154, verbosity=0)
        self.assertEqual(u'Could not open the datasource at "toto.geojson"', e.exception.message)

    def test_load_cities_with_line(self):
        output = StringIO()
        filename_line = os.path.join(os.path.dirname(__file__), 'data', 'line.geojson')
        call_command('loadcities', filename_line, name='NOM', code='Insee', verbosity=2, stdout=output)
        self.assertIn("coucou's geometry is not a polygon", output.getvalue())

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_cities_with_one_inside_one_outside_within(self):
        call_command('loadcities', self.filename_out_in, name='NOM', code='Insee', verbosity=0)
        self.assertEquals(City.objects.count(), 1)
        value = City.objects.first()
        self.assertEquals('0', value.code)
        self.assertEquals('coucou', value.name)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(10, 11, 11, 12))
    def test_load_cities_not_within(self):
        call_command('loadcities', self.filename_out_in, name='NOM', code='Insee', verbosity=0)
        self.assertEquals(City.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(10, 11, 11, 12))
    def test_load_cities_not_intersect(self):
        call_command('loadcities', self.filename_out_in, '-i', name='NOM', code='Insee', verbosity=0)
        self.assertEquals(City.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_cities_with_one_inside_one_outside_intersect(self):
        output = StringIO()
        call_command('loadcities', self.filename_out_in, '-i', name='NOM', code='Insee', verbosity=2, stdout=output)
        self.assertEquals(City.objects.count(), 2)
        value_1 = City.objects.first()
        self.assertEquals('0', value_1.code)
        self.assertEquals('coucou', value_1.name)
        value_2 = City.objects.last()
        self.assertEquals('1', value_2.code)
        self.assertEquals('lulu', value_2.name)
        output = output.getvalue()
        output_2 = StringIO()
        self.assertIn('Created coucou', output)
        self.assertIn('Created lulu', output)
        call_command('loadcities', self.filename_out_in, '-i', name='NOM', code='Insee', verbosity=2, stdout=output_2)
        output = output_2.getvalue()
        self.assertIn('Updated coucou', output)
        self.assertIn('Updated lulu', output)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_cities_no_match_properties(self):
        output = StringIO()
        call_command('loadcities', self.filename_out_in, name='toto', code='tata', stdout=output)
        self.assertIn('NOM, Insee', output.getvalue())
        call_command('loadcities', self.filename_out_in, '-i', name='toto', code='tata', stdout=output)
        self.assertIn('NOM, Insee', output.getvalue())
