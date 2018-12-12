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
