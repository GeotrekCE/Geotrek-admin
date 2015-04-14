# -*- coding: utf-8 -*-

import os

from django.core.management import call_command
from django.test import TestCase

from geotrek.zoning.models import City


WKT = ('MULTIPOLYGON ((('
       '309716.2814123088610359 6698350.2021781457588077, '
       '330923.9023930223193020 6728938.1170541746541858, '
       '341391.7665950411465019 6698214.2558898078277707, '
       '309716.2814123088610359 6698350.2021781457588077)))')


class CityParserTest(TestCase):
    def test_good_data(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'city.shp')
        call_command('import', 'geotrek.zoning.parsers.CityParser', filename, verbosity=0)
        city = City.objects.get()
        self.assertEqual(city.code, u"99999")
        self.assertEqual(city.name, u"Trifouilli-les-Oies")
        self.assertEqual(city.geom.wkt, WKT)
