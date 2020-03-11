from unittest import mock

from django.contrib.gis.geos import Point
from django.db import connection
from django.test import TestCase, override_settings

from ..utils import sql_extent, uniquify, format_coordinates
from ..utils.postgresql import debug_pg_notices
from ..utils.import_celery import (create_tmp_destination,
                                   subclasses,
                                   )

from geotrek.common.parsers import Parser


class UtilsTest(TestCase):

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
                'ApidaeParser',
                'TourismSystemParser'):
            self.assertTrue(classname not in class_list)

    def test_create_tmp_directory(self):
        self.assertTupleEqual(
            ('/app/src/var/tmp/bombadil', '/app/src/var/tmp/bombadil/bombadil'),
            create_tmp_destination('bombadil')
        )

    @override_settings(DISPLAY_SRID=3857)
    def test_format_coordinates_wgs84(self):
        geom = Point(x=700000, y=6600000, srid=2154)
        self.assertEqual(format_coordinates(geom), '46°30\'00" N / 3°00\'00" E (WGS 84 / Pseudo-Mercator)')

    @override_settings(DISPLAY_SRID=32631)
    def test_format_coordinates_custom_srid(self):
        geom = Point(x=333958, y=5160979, srid=3857)
        self.assertEqual(format_coordinates(geom), 'X : 0500000 / Y : 4649776 (WGS 84 / UTM zone 31N)')
