import os
from unittest import mock

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import connection
from django.test import TestCase, override_settings

from geotrek.common.parsers import Parser
from ..utils import sql_extent, uniquify, format_coordinates, spatial_reference
from ..utils.import_celery import create_tmp_destination, subclasses
from ..utils.postgresql import debug_pg_notices


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
                CREATE OR REPLACE FUNCTION raisenotice() RETURNS boolean AS $$
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
            (os.path.join(settings.TMP_DIR, 'bombadil'),
             os.path.join(settings.TMP_DIR, 'bombadil', 'bombadil')),
            create_tmp_destination('bombadil')
        )

    @override_settings(DISPLAY_SRID=3857)
    def test_format_coordinates_wgs84(self):
        geom = Point(x=700000, y=6600000, srid=2154)
        self.assertEqual(format_coordinates(geom), '46°30\'00" N / 3°00\'00" E')

    @override_settings(DISPLAY_SRID=32631)
    def test_format_coordinates_custom_srid(self):
        geom = Point(x=333958, y=5160979, srid=3857)
        self.assertEqual(format_coordinates(geom), 'X : 0500000 / Y : 4649776')

    @override_settings(DISPLAY_SRID=4326)
    @override_settings(DISPLAY_COORDS_AS_DECIMALS=True)
    def test_format_coordinates_as_decimals(self):
        geom = Point(x=6.266479251980001, y=44.079241580599906, srid=4326)
        self.assertEqual(format_coordinates(geom), '44.079242°N, 6.266479°E')

    @override_settings(DISPLAY_SRID=4326)
    @override_settings(DISPLAY_COORDS_AS_DECIMALS=True)
    def test_format_coordinates_as_decimals_negative(self):
        geom = Point(x=-6.266479251980001, y=-44.079241580599906, srid=4326)
        self.assertEqual(format_coordinates(geom), '44.079242°S, 6.266479°W')

    @override_settings(DISPLAY_SRID=4326)
    @override_settings(DISPLAY_COORDS_AS_DECIMALS=True)
    def test_format_coordinates_as_decimals_from_lambert(self):
        geom = Point(x=961553.0322000659, y=6336548.320195582, srid=2154)
        self.assertEqual(format_coordinates(geom), '44.079242°N, 6.266479°E')

    @override_settings(DISPLAY_SRID=3857)
    def test_spatial_reference(self):
        self.assertEqual(spatial_reference(), 'WGS 84 / Pseudo-Mercator')

    @override_settings(DISPLAY_SRID=32631)
    def test_spatial_reference_wgs84(self):
        self.assertEqual(spatial_reference(), 'WGS 84 / UTM zone 31N')
