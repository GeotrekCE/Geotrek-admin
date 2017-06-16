# -*- encoding: utf-8 -*-

import os
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from geotrek.common.utils.signals import check_srid_has_meter_unit
from geotrek.settings import EnvIniReader


class StartupCheckTest(TestCase):
    def test_error_is_raised_if_srid_is_not_meters(self):
        delattr(check_srid_has_meter_unit, '_checked')
        with self.settings(SRID=4326):
            self.assertRaises(ImproperlyConfigured, check_srid_has_meter_unit, None)


class EnvIniTests(TestCase):
    ini_file = os.path.join('conf.ini')

    def setUp(self):
        with open(self.ini_file, 'w') as f:
            f.write("""[settings]\nkey = value\nkeyint = 3\nlist = a, b,c\nfloats = 0.4 ,1.3""")
        self.envini = EnvIniReader(self.ini_file)
        os.environ['KEYINT'] = '4'

    def test_existing_key(self):
        self.assertEqual(self.envini.get('key'), 'value')
        self.assertEqual(self.envini.get('keyint'), '4')
        self.assertEqual(self.envini.get('keyint', env=False), '3')

    def test_missing_key(self):
        self.assertEqual(self.envini.get('unknown', 'void'), 'void')
        self.assertEqual(self.envini.get('unknown', None), None)
        self.assertRaises(ImproperlyConfigured, self.envini.get, 'unknown')

    def test_helpers(self):
        self.assertEqual(self.envini.getint('keyint'), 4)
        self.assertEqual(self.envini.getstrings('list'), ['a', 'b', 'c'])
        self.assertEqual(self.envini.getfloats('floats'), [0.4, 1.3])

    def tearDown(self):
        os.remove(self.ini_file)
