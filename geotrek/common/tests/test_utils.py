import os
from shutil import copy as copyfile
from unittest import mock
from unittest.mock import MagicMock

import requests
from django.conf import settings
from django.contrib.gis.geos import GeometryCollection, GEOSGeometry, MultiPoint, Point
from django.test import SimpleTestCase, TestCase
from django.test.utils import override_settings
from mapbox_baselayer.models import BaseLayerTile, MapBaseLayer
from pmtiles.tile import TileType
from requests import HTTPError

from ..parsers import Parser
from ..utils import format_coordinates, simplify_coords, spatial_reference, uniquify
from ..utils.file_infos import get_encoding_file
from ..utils.generate_pmtiles import (
    PATH,
    RETRY_COUNT,
    TMP_PATH,
    generate_pmtiles,
    get_baselayer,
    get_json,
    get_or_retry,
    get_tile_type,
    get_tile_url,
    get_zooms,
)
from ..utils.import_celery import create_tmp_destination, subclasses
from ..utils.parsers import (
    GeomValueError,
    add_http_prefix,
    force_geom_to_2d,
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


class ForceGeomTo2dTests(TestCase):
    def test_error_when_geom_is_none(self):
        with self.assertRaisesMessage(ValueError, "Input geometry cannot be None"):
            force_geom_to_2d(None)

    def test_succeed_when_geom_is_empty(self):
        empty_geom = GEOSGeometry("POINT EMPTY")
        result = force_geom_to_2d(empty_geom)
        self.assertTrue(result.empty)
        self.assertEqual(result.geom_type, "Point")
        self.assertFalse(result.hasz)

    def test_succeed_when_geom_is_empty_geometry_collection(self):
        empty_collection = GeometryCollection()
        result = force_geom_to_2d(empty_collection)
        self.assertTrue(result.empty)
        self.assertEqual(result.geom_type, "GeometryCollection")
        self.assertFalse(result.hasz)

    def test_succeed_when_geom2d_to_geom2d(self):
        geom = Point(3.0, 4.0)
        original_wkt = geom.wkt
        result = force_geom_to_2d(geom)
        self.assertEqual(result.geom_type, "Point")
        self.assertFalse(result.hasz)
        self.assertEqual(result.coords, (3.0, 4.0))
        self.assertTrue(result.valid)
        self.assertEqual(geom.wkt, original_wkt)

    def test_succeed_when_geom3d_to_geom2d(self):
        geom = Point(3.0, 4.0, 5.0)
        original_wkt = geom.wkt
        result = force_geom_to_2d(geom)
        self.assertEqual(result.geom_type, "Point")
        self.assertFalse(result.hasz)
        self.assertEqual(result.coords, (3.0, 4.0))
        self.assertTrue(result.valid)
        self.assertEqual(geom.wkt, original_wkt)

    def test_succeed_when_mixed_geom2d_geom3d_to_geom2d(self):
        geom = MultiPoint(Point(1.0, 2.0), Point(1.0, 2.0, 3.0))
        original_wkt = geom.wkt
        result = force_geom_to_2d(geom)
        self.assertEqual(result.geom_type, "MultiPoint")
        self.assertEqual(len(result), 2)
        for point in result:
            self.assertFalse(point.hasz)
        self.assertTrue(result.valid)
        self.assertEqual(geom.wkt, original_wkt)


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


class TestGeneratePmtiles(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.raster_base_layer = MapBaseLayer.objects.create(
            name="Raster layer",
            base_layer_type="raster",
            sprite="http://mystyle",
            glyphs="http://mystyle",
            min_zoom=1,
            max_zoom=9,
        )
        cls.tile = BaseLayerTile.objects.create(
            base_layer=cls.raster_base_layer, url="http://tiles/{x}/{y}/{z}"
        )
        cls.mapbox_base_layer = MapBaseLayer.objects.create(
            name="Mapbox layer",
            order=0,
            base_layer_type="mapbox",
            map_box_url="mapbox://mystyle",
        )

        cls.json_style = {
            "sources": {"source 1": {"tiles": ["http://tiles/{x}/{y}/{z}"]}},
            "layers": [],
        }

    def _make_raise_for_status(self, succeed):
        def raise_for_status():
            if not succeed:
                url = "http://url.com"
                msg = "Error"
                raise requests.exceptions.HTTPError(url, 500, msg, None, None)

        return raise_for_status

    def test_get_baselayer(self):
        # get existent baselayer
        baselayer = get_baselayer(self.raster_base_layer.pk)
        self.assertEqual(baselayer, self.raster_base_layer)

        # get non existent baselayer
        with self.assertRaisesRegex(
            MapBaseLayer.DoesNotExist, "MapBaseLayer 9999 does not exist"
        ):
            get_baselayer(9999)

    def test_get_zooms(self):
        # zooms in bounderies
        zooms = get_zooms(1, 6, self.raster_base_layer)
        self.assertEqual(zooms, [1, 2, 3, 4, 5, 6])

        # min zoom out of bounderies
        with self.assertLogs(
            "geotrek.common.utils.generate_pmtiles", level="WARNING"
        ) as log:
            zooms = get_zooms(0, 6, self.raster_base_layer)
            self.assertEqual(zooms, [1, 2, 3, 4, 5, 6])
            self.assertTrue("Baselayer min zoom has been selected: 1" in log.output[0])

        # max zoom out of bounderies
        with self.assertLogs(
            "geotrek.common.utils.generate_pmtiles", level="WARNING"
        ) as log:
            zooms = get_zooms(4, 10, self.raster_base_layer)
            self.assertEqual(zooms, [4, 5, 6, 7, 8, 9])
            self.assertTrue("Baselayer max zoom has been selected: 9" in log.output[0])

        # min zoom = None
        with self.assertLogs(
            "geotrek.common.utils.generate_pmtiles", level="WARNING"
        ) as log:
            zooms = get_zooms(None, 6, self.raster_base_layer)
            self.assertEqual(zooms, [1, 2, 3, 4, 5, 6])
            self.assertTrue("Baselayer min zoom has been selected: 1" in log.output[0])

        # max zoom = None
        with self.assertLogs(
            "geotrek.common.utils.generate_pmtiles", level="WARNING"
        ) as log:
            zooms = get_zooms(4, None, self.raster_base_layer)
            self.assertEqual(zooms, [4, 5, 6, 7, 8, 9])
            self.assertTrue("Baselayer max zoom has been selected: 9" in log.output[0])

        # get non existent baselayer
        with self.assertRaisesRegex(
            MapBaseLayer.DoesNotExist, "MapBaseLayer 9999 does not exist"
        ):
            get_baselayer(9999)

    @mock.patch("geotrek.common.utils.generate_pmtiles.requests.get")
    def test_get_json(self, mocked):
        raster_json = get_json(self.raster_base_layer)
        self.assertEqual(raster_json, self.raster_base_layer.tilejson)

        mocked.return_value.status_code = 200
        mocked.return_value.json.return_value = self.json_style

        vector_json = get_json(self.mapbox_base_layer)
        self.assertEqual(vector_json, self.json_style)

    def test_get_tile_url(self):
        data = {
            "sources": {
                "source 1": {
                    "tiles": [
                        "http://tiles1_1/{x}/{y}/{z}",
                        "http://tiles1_2/{x}/{y}/{z}",
                    ]
                },
                "source 2": {
                    "tiles": [
                        "http://tiles2_1/{x}/{y}/{z}",
                        "http://tiles2_2/{x}/{y}/{z}",
                    ]
                },
            }
        }
        tile_url = get_tile_url(data)
        self.assertEqual(tile_url, "http://tiles1_1/{x}/{y}/{z}")

    @mock.patch("geotrek.common.utils.generate_pmtiles.requests.get")
    def test_get_or_retry_good_request(self, mocked):
        mocked.return_value.raise_for_status.side_effect = self._make_raise_for_status(
            succeed=True
        )
        mocked.return_value.content = b""

        response = get_or_retry("http://url.com")
        self.assertEqual(response.content, b"")

    @mock.patch("geotrek.common.utils.generate_pmtiles.requests.get")
    def test_get_or_retry_wrong_request(self, mocked):
        mocked.return_value.raise_for_status.side_effect = self._make_raise_for_status(
            succeed=False
        )
        mocked.return_value.content = b""

        with self.assertRaises(HTTPError):
            get_or_retry("http://url.com")

        self.assertEqual(mocked.call_count, RETRY_COUNT)

    def test_get_tile_type(self):
        self.assertEqual(get_tile_type(self.raster_base_layer), TileType.PNG)
        self.assertEqual(get_tile_type(self.mapbox_base_layer), TileType.MVT)

    @mock.patch("geotrek.common.utils.generate_pmtiles.requests.get")
    def _run_generate_pmtiles_test(self, base_layer, succeed, mocked):
        slug = base_layer.slug

        self.assertFalse(os.path.exists(f"{TMP_PATH}{slug}.pmtiles"))
        self.assertFalse(os.path.exists(f"{PATH}{slug}.pmtiles"))
        self.assertFalse(os.path.exists(f"{PATH}{slug}.json"))

        side_effect = self._make_raise_for_status(succeed)

        style_response = MagicMock()
        style_response.raise_for_status.side_effect = side_effect
        style_response.json.return_value = self.json_style

        tile_response = MagicMock()
        tile_response.raise_for_status.side_effect = side_effect
        tile_response.content = b"fake-tile-data"

        mocked.side_effect = lambda url, *args, **kwargs: (
            style_response if url == base_layer.real_url else tile_response
        )

        # keep small zoom interval to generate files quickly
        generate_pmtiles(base_layer.pk, 1, 3)

    def _check_files(self, base_layer, succeed):
        slug = base_layer.slug

        self.assertEqual(os.path.exists(f"{TMP_PATH}{slug}.pmtiles"), not succeed)
        self.assertEqual(os.path.exists(f"{PATH}{slug}.pmtiles"), succeed)
        self.assertEqual(os.path.exists(f"{PATH}{slug}.json"), succeed)

        path = PATH if succeed else TMP_PATH
        os.remove(f"{path}{slug}.pmtiles")
        if succeed:
            os.remove(f"{PATH}{slug}.json")

    def test_generate_raster_pmtiles(self):
        self._run_generate_pmtiles_test(self.raster_base_layer, True)
        self._check_files(self.raster_base_layer, True)

    def test_generate_mapbox_pmtiles(self):
        self._run_generate_pmtiles_test(self.mapbox_base_layer, True)
        self._check_files(self.mapbox_base_layer, True)

    def test_generate_incorrect_raster_pmtiles(self):
        with self.assertRaises(HTTPError):
            self._run_generate_pmtiles_test(self.raster_base_layer, False)
        self._check_files(self.raster_base_layer, False)
