# -*- coding: utf-8 -*-

import os

from django.contrib.gis.geos import Polygon, MultiPolygon
from django.core.management import call_command
from django.test import TestCase

from geotrek.zoning.models import City
from geotrek.zoning.parsers import CityParser


WKT = ('MULTIPOLYGON ((('
       '309716.2814121811534278 6698350.2021761955693364, '
       '330923.9023929062532261 6728938.1170523092150688, '
       '341391.7665949241491035 6698214.2558878632262349, '
       '309716.2814121811534278 6698350.2021761955693364)))')


class CityParserTest(TestCase):
    def test_good_data(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'city.shp')
        call_command('import', 'geotrek.zoning.parsers.CityParser', filename, verbosity=0)
        city = City.objects.get()
        self.assertEqual(city.code, u"99999")
        self.assertEqual(city.name, u"Trifouilli-les-Oies")
        self.assertEqual(city.geom.wkt, WKT)


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
