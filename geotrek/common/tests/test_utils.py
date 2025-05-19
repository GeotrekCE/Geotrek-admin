import os
from shutil import copy as copyfile

from django.conf import settings
from django.contrib.gis.geos import Point
from django.test import SimpleTestCase, TestCase
from django.test.utils import override_settings

from ..parsers import Parser
from ..utils import format_coordinates, simplify_coords, spatial_reference, uniquify
from ..utils.file_infos import get_encoding_file
from ..utils.import_celery import create_tmp_destination, subclasses
from ..utils.parsers import (
    GeomValueError,
    add_http_prefix,
    get_geom_from_gpx,
    get_geom_from_kml,
    maybe_fix_encoding_to_utf8,
)


class UtilsTest(TestCase):
    def test_uniquify(self):
        self.assertEqual([3, 2, 1], uniquify([3, 3, 2, 1, 3, 1, 2]))

    def test_subclasses(self):
        class_list = subclasses(Parser)
        for classname in (
            "TrekParser",
            "TourInSoftParser",
            "CityParser",
            "ExcelParser",
            "OpenSystemParser",
            "ShapeParser",
            "ApidaeParser",
            "TourismSystemParser",
        ):
            self.assertTrue(classname not in class_list)

    def test_create_tmp_directory(self):
        self.assertTupleEqual(
            (
                os.path.join(settings.TMP_DIR, "bombadil"),
                os.path.join(settings.TMP_DIR, "bombadil", "bombadil"),
            ),
            create_tmp_destination("bombadil"),
        )

    @override_settings(DISPLAY_SRID=3857)
    def test_format_coordinates_wgs84(self):
        geom = Point(x=700000, y=6600000, srid=2154)
        self.assertEqual(format_coordinates(geom), "46°30'00\" N / 3°00'00\" E")

    @override_settings(DISPLAY_SRID=32631)
    def test_format_coordinates_custom_srid(self):
        geom = Point(x=333958, y=5160979, srid=3857)
        self.assertEqual(format_coordinates(geom), "X : 0500000 / Y : 4649776")

    @override_settings(DISPLAY_SRID=4326)
    @override_settings(DISPLAY_COORDS_AS_DECIMALS=True)
    def test_format_coordinates_as_decimals(self):
        geom = Point(x=6.266479251980001, y=44.079241580599906, srid=4326)
        self.assertEqual(format_coordinates(geom), "44.079242°N, 6.266479°E")

    @override_settings(DISPLAY_SRID=4326)
    @override_settings(DISPLAY_COORDS_AS_DECIMALS=True)
    def test_format_coordinates_as_decimals_negative(self):
        geom = Point(x=-6.266479251980001, y=-44.079241580599906, srid=4326)
        self.assertEqual(format_coordinates(geom), "44.079242°S, 6.266479°W")

    @override_settings(DISPLAY_SRID=4326)
    @override_settings(DISPLAY_COORDS_AS_DECIMALS=True)
    def test_format_coordinates_as_decimals_from_lambert(self):
        geom = Point(x=961553.0322000659, y=6336548.320195582, srid=2154)
        self.assertEqual(format_coordinates(geom), "44.079242°N, 6.266479°E")

    @override_settings(DISPLAY_SRID=3857)
    def test_spatial_reference(self):
        self.assertEqual(spatial_reference(), "WGS 84 / Pseudo-Mercator")

    @override_settings(DISPLAY_SRID=32631)
    def test_spatial_reference_wgs84(self):
        self.assertEqual(spatial_reference(), "WGS 84 / UTM zone 31N")


class SimplifyCoordsTest(TestCase):
    def test_coords_float(self):
        """Test a float value is rounded at .0000007"""
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


class UtilsParsersTest(SimpleTestCase):
    def test_add_http_prefix_without_prefix(self):
        self.assertEqual("http://test.com", add_http_prefix("test.com"))

    def test_add_http_prefix_with_prefix(self):
        self.assertEqual("http://test.com", add_http_prefix("http://test.com"))


class GpxToGeomTests(SimpleTestCase):
    @staticmethod
    def _get_gpx_from(filename):
        with open(filename) as f:
            gpx = f.read()
        return bytes(gpx, "utf-8")

    def test_gpx_with_waypoint_can_be_converted(self):
        gpx = self._get_gpx_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/apidae_test_trek.gpx"
        )

        geom = get_geom_from_gpx(gpx)

        self.assertEqual(geom.srid, 2154)
        self.assertEqual(geom.geom_type, "LineString")
        self.assertEqual(len(geom.coords), 13)
        first_point = geom.coords[0]
        self.assertAlmostEqual(first_point[0], 977776.9, delta=0.1)
        self.assertAlmostEqual(first_point[1], 6547354.8, delta=0.1)

    def test_gpx_with_route_points_can_be_converted(self):
        gpx = self._get_gpx_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace_with_route_points.gpx"
        )

        geom = get_geom_from_gpx(gpx)

        self.assertEqual(geom.srid, 2154)
        self.assertEqual(geom.geom_type, "LineString")
        self.assertEqual(len(geom.coords), 13)
        first_point = geom.coords[0]
        self.assertAlmostEqual(first_point[0], 977776.9, delta=0.1)
        self.assertAlmostEqual(first_point[1], 6547354.8, delta=0.1)

    def test_it_raises_an_error_on_not_continuous_segments(self):
        gpx = self._get_gpx_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace_with_not_continuous_segments.gpx"
        )

        with self.assertRaises(GeomValueError):
            get_geom_from_gpx(gpx)

    def test_it_handles_segment_with_single_point(self):
        gpx = self._get_gpx_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace_with_single_point_segment.gpx"
        )
        geom = get_geom_from_gpx(gpx)

        self.assertEqual(geom.srid, 2154)
        self.assertEqual(geom.geom_type, "LineString")
        self.assertEqual(len(geom.coords), 13)

    def test_it_raises_an_error_when_no_linestring(self):
        gpx = self._get_gpx_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace_with_no_feature.gpx"
        )

        with self.assertRaises(GeomValueError):
            get_geom_from_gpx(gpx)

    def test_it_handles_multiple_continuous_features(self):
        gpx = self._get_gpx_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace_with_multiple_continuous_features.gpx"
        )
        geom = get_geom_from_gpx(gpx)

        self.assertEqual(geom.srid, 2154)
        self.assertEqual(geom.geom_type, "LineString")
        self.assertEqual(len(geom.coords), 12)
        first_point = geom.coords[0]
        self.assertAlmostEqual(first_point[0], 977776.9, delta=0.1)
        self.assertAlmostEqual(first_point[1], 6547354.8, delta=0.1)

    def test_it_handles_multiple_continuous_features_with_one_empty(self):
        gpx = self._get_gpx_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace_with_multiple_continuous_features_and_one_empty.gpx"
        )
        geom = get_geom_from_gpx(gpx)

        self.assertEqual(geom.srid, 2154)
        self.assertEqual(geom.geom_type, "LineString")
        self.assertEqual(len(geom.coords), 12)
        first_point = geom.coords[0]
        self.assertAlmostEqual(first_point[0], 977776.9, delta=0.1)
        self.assertAlmostEqual(first_point[1], 6547354.8, delta=0.1)

    def test_it_raises_error_on_multiple_not_continuous_features(self):
        gpx = self._get_gpx_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace_with_multiple_not_continuous_features.gpx"
        )
        with self.assertRaises(GeomValueError):
            get_geom_from_gpx(gpx)

    def test_it_raises_error_on_invalid_multilinestring_merge(self):
        gpx = self._get_gpx_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace_with_only_two_duplicate_track_points.gpx"
        )
        with self.assertRaises(GeomValueError):
            get_geom_from_gpx(gpx)


class KmlToGeomTests(SimpleTestCase):
    @staticmethod
    def _get_kml_from(filename):
        with open(filename) as f:
            kml = f.read()
        return bytes(kml, "utf-8")

    def test_kml_can_be_converted(self):
        kml = self._get_kml_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace.kml"
        )

        geom = get_geom_from_kml(kml)

        self.assertEqual(geom.srid, 2154)
        self.assertEqual(geom.geom_type, "LineString")
        self.assertEqual(len(geom.coords), 61)
        first_point = geom.coords[0]
        self.assertAlmostEqual(first_point[0], 973160.8, delta=0.1)
        self.assertAlmostEqual(first_point[1], 6529320.1, delta=0.1)

    def test_it_raises_exception_when_no_linear_data(self):
        kml = self._get_kml_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace_with_no_line.kml"
        )

        with self.assertRaises(GeomValueError):
            get_geom_from_kml(kml)

    def test_it_raises_exception_on_invalid_multilinestring_merge(self):
        kml = self._get_kml_from(
            "geotrek/trekking/tests/data/apidae_trek_parser/trace_with_only_two_duplicate_coordinates.kml"
        )

        with self.assertRaises(GeomValueError):
            get_geom_from_kml(kml)


class TestConvertEncodingFiles(TestCase):
    data_dir = "geotrek/trekking/tests/data"

    def setUp(self):
        if not os.path.exists(settings.TMP_DIR):
            os.mkdir(settings.TMP_DIR)

    def test_fix_encoding_to_utf8(self):
        file_name = f"{settings.TMP_DIR}/file_bad_encoding_tmp.kml"
        copyfile(f"{self.data_dir}/file_bad_encoding.kml", file_name)

        encoding = get_encoding_file(file_name)
        self.assertNotEqual(encoding, "utf-8")

        new_file_name = maybe_fix_encoding_to_utf8(file_name)

        encoding = get_encoding_file(new_file_name)
        self.assertEqual(encoding, "utf-8")

    def test_not_fix_encoding_to_utf8(self):
        file_name = f"{settings.TMP_DIR}/file_good_encoding_tmp.kml"
        copyfile(f"{self.data_dir}/file_good_encoding.kml", file_name)

        encoding = get_encoding_file(file_name)
        self.assertEqual(encoding, "utf-8")

        new_file_name = maybe_fix_encoding_to_utf8(file_name)

        encoding = get_encoding_file(new_file_name)
        self.assertEqual(encoding, "utf-8")
