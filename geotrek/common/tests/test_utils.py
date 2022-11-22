import os

from django.conf import settings
from django.contrib.gis.geos import Point
from django.test import TestCase, override_settings

from ..parsers import Parser
from ..utils import uniquify, format_coordinates, spatial_reference, simplify_coords
from ..utils.import_celery import create_tmp_destination, subclasses


class UtilsTest(TestCase):
    def test_uniquify(self):
        self.assertEqual([3, 2, 1], uniquify([3, 3, 2, 1, 3, 1, 2]))

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


class SimplifyCoordsTest(TestCase):
    def test_coords_float(self):
        """ Test a float value is rounded at .0000007 """
        arg_value = 0.00000008
        simplified_value = simplify_coords(arg_value)
        self.assertEqual(simplified_value, 0.0000001)

    def test_coords_list_or_tuple_float(self):
        arg_value = (0.00000008, 0.0000001)
        simplified_value = simplify_coords(arg_value)
        for value in simplified_value:
            self.assertEqual(value, 0.0000001)

        simplified_value = simplify_coords(list(arg_value))
        for value in simplified_value:
            self.assertEqual(value, 0.0000001)

    def test_coords_bad_arg(self):
        arg_value = "test"
        with self.assertRaises(Exception):
            simplify_coords(arg_value)
