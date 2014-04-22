import os

import mock

from django.db import connection
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured

from mapentity.tests import MapEntityTest
from mapentity.factories import UserFactory

from geotrek.settings import EnvIniReader
from .utils import almostequal, sampling, sql_extent, uniquify
from .utils.postgresql import debug_pg_notices
from . import check_srid_has_meter_unit


class CommonTest(MapEntityTest):
    fixtures = ['minimal.json', 'basic.json']


class StartupCheckTest(TestCase):
    def test_error_is_raised_if_srid_is_not_meters(self):
        delattr(check_srid_has_meter_unit, '_checked')
        with self.settings(SRID=4326):
            self.assertRaises(ImproperlyConfigured, check_srid_has_meter_unit, None)


class ViewsTest(TestCase):

    def setUp(self):
        self.user = UserFactory.create(username='homer', password='dooh')
        success = self.client.login(username=self.user.username, password='dooh')
        self.assertTrue(success)

    def test_settings_json(self):
        url = reverse('common:settings_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_check_extents(self):
        url = reverse('common:check_extents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class UtilsTest(TestCase):
    def test_almostequal(self):
        self.assertTrue(almostequal(0.001, 0.002))
        self.assertFalse(almostequal(0.001, 0.002, precision=3))
        self.assertFalse(almostequal(1, 2, precision=0))
        self.assertFalse(almostequal(-1, 1))
        self.assertFalse(almostequal(1, -1))

    def test_sampling(self):
        self.assertEqual([0, 2, 4, 6, 8], sampling(range(10), 5))
        self.assertEqual([0, 3, 6, 9], sampling(range(10), 3))
        self.assertEqual(['a', 'd', 'g', 'j'], sampling('abcdefghijkl', 4))

    def test_sqlextent(self):
        ext = sql_extent("SELECT ST_Extent('LINESTRING(0 0, 10 10)'::geometry)")
        self.assertEqual((0.0, 0.0, 10.0, 10.0), ext)

    def test_uniquify(self):
        self.assertEqual([3, 2, 1], uniquify([3, 3, 2, 1, 3, 1, 2]))

    def test_postgresql_notices(self):
        def raisenotice():
            cursor = connection.cursor()
            cursor.execute("""
                CREATE OR REPLACE FUNCTION raisenotice() RETURNS boolean AS $$
                BEGIN
                RAISE NOTICE 'hello'; RETURN FALSE;
                END; $$ LANGUAGE plpgsql;
                SELECT raisenotice();""")
        raisenotice = debug_pg_notices(raisenotice)
        with mock.patch('geotrek.common.utils.postgresql.logger') as fake_log:
            raisenotice()
            fake_log.debug.assert_called_with('hello')


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
