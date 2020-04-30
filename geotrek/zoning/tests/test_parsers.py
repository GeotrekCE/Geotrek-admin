import os

from django.contrib.gis.geos import Polygon, MultiPolygon, WKTWriter
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from geotrek.zoning.models import City
from geotrek.zoning.parsers import CityParser


WKT = (
    b'MULTIPOLYGON ((('
    b'309716.2814122 6698350.2021762, '
    b'330923.9023929 6728938.1170523, '
    b'341391.7665949 6698214.2558879, '
    b'309716.2814122 6698350.2021762'
    b')))'
)


class CityParserTest(TestCase):
    def test_good_data(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'city.shp')
        call_command('import', 'geotrek.zoning.parsers.CityParser', filename, verbosity=0)
        city = City.objects.get()
        self.assertEqual(city.code, "99999")
        self.assertEqual(city.name, "Trifouilli-les-Oies")
        self.assertEqual(WKTWriter(precision=7).write(city.geom), WKT)

    def test_wrong_geom(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'line.geojson')
        with self.assertRaisesRegex(CommandError, r"Invalid geometry type for field 'GEOM'. "
                                                   r"Should be \(Multi\)Polygon, not LineString"):
            call_command('import', 'geotrek.zoning.parsers.CityParser', filename, verbosity=2)
        self.assertEqual(City.objects.count(), 0)


class FilterGeomTest(TestCase):
    def setUp(self):
        self.parser = CityParser()

    def test_empty_geom(self):
        self.assertEqual(self.parser.filter_geom('geom', None), None)
        self.assertFalse(self.parser.warnings)

    def test_invalid_geom(self):
        geom = MultiPolygon(Polygon(((0, 0), (0, 1), (1, 0), (1, 1), (0, 0))))
        self.assertEqual(self.parser.filter_geom('geom', geom), None)
        self.assertTrue(self.parser.warnings)

    def test_polygon(self):
        geom = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        self.assertEqual(self.parser.filter_geom('geom', geom), MultiPolygon(geom))
        self.assertFalse(self.parser.warnings)

    def test_multipolygon(self):
        geom = MultiPolygon(Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))))
        self.assertEqual(self.parser.filter_geom('geom', geom), geom)
        self.assertFalse(self.parser.warnings)
