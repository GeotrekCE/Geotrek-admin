# -*- encoding: utf-8 -*-

import mock

from django.db import connection
from django.test import TestCase

from ..utils import almostequal, sql_extent, uniquify
from ..utils.postgresql import debug_pg_notices
from ..utils.import_celery import (create_tmp_destination,
                                   subclasses,
                                   )

from geotrek.common.parsers import Parser


class UtilsTest(TestCase):

    def test_almostequal(self):
        self.assertTrue(almostequal(0.001, 0.002))
        self.assertFalse(almostequal(0.001, 0.002, precision=3))
        self.assertFalse(almostequal(1, 2, precision=0))
        self.assertFalse(almostequal(-1, 1))
        self.assertFalse(almostequal(1, -1))

    def test_sqlextent(self):
        ext = sql_extent(
            "SELECT ST_Extent('LINESTRING(0 0, 10 10)'::geometry)")
        self.assertEqual((0.0, 0.0, 10.0, 10.0), ext)

    def test_uniquify(self):
        self.assertEqual([3, 2, 1], uniquify([3, 3, 2, 1, 3, 1, 2]))

    def test_postgresql_notices(self):
        def raisenotice():
            cursor = connection.cursor()
            cursor.execute("""
                CREATE OR REPLACE FUNCTION geotrek.raisenotice() RETURNS boolean AS $$
                BEGIN
                RAISE NOTICE 'hello'; RETURN FALSE;
                END; $$ LANGUAGE plpgsql;
                SELECT raisenotice();""")
        raisenotice = debug_pg_notices(raisenotice)
        with mock.patch('geotrek.common.utils.postgresql.logger') as fake_log:
            raisenotice()
            fake_log.debug.assert_called_with('hello')

    def test_subclasses(self):
        class_list = subclasses(Parser)
        for classname in (
                'TrekParser',
                'TourInSoftParser',
                'CityParser',
                'ExcelParser',
                'OpenSystemParser',
                'ShapeParser',
                'SitraParser',
                'TourismSystemParser'):
            self.assert_(classname not in class_list)

    def test_create_tmp_directory(self):
        self.assertTupleEqual(
            ('/tmp/geotrek/bombadil', '/tmp/geotrek/bombadil/bombadil'),
            create_tmp_destination('bombadil')
        )
