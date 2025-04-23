import os
import json

from django.contrib.gis.geos import MultiPolygon, Polygon, WKTWriter
from django.core.management import CommandError, call_command
from django.test import TestCase

from geotrek.zoning.models import City, District
from geotrek.zoning.parsers import CityParser, OpenStreetMapDistrictParser

from unittest import mock

WKT = (
    b"MULTIPOLYGON (((309716.2814 6698350.2022, 330923.9024 6728938.1171, "
    b"341391.7666 6698214.2559, 309716.2814 6698350.2022)))"
)


class CityParserTest(TestCase):
    def test_good_data(self):
        filename = os.path.join(os.path.dirname(__file__), "data", "city.shp")
        call_command(
            "import", "geotrek.zoning.parsers.CityParser", filename, verbosity=0
        )
        city = City.objects.get()
        self.assertEqual(city.code, "99999")
        self.assertEqual(city.name, "Trifouilli-les-Oies")
        self.assertEqual(WKTWriter(precision=4).write(city.geom), WKT)

    def test_wrong_geom(self):
        filename = os.path.join(os.path.dirname(__file__), "data", "line.geojson")
        with self.assertRaisesRegex(
            CommandError,
            r"Invalid geometry type for field 'GEOM'. "
            r"Should be \(Multi\)Polygon, not LineString",
        ):
            call_command(
                "import", "geotrek.zoning.parsers.CityParser", filename, verbosity=2
            )
        self.assertEqual(City.objects.count(), 0)


class FilterGeomTest(TestCase):
    def setUp(self):
        self.parser = CityParser()

    def test_empty_geom(self):
        self.assertEqual(self.parser.filter_geom("geom", None), None)
        self.assertFalse(self.parser.warnings)

    def test_invalid_geom(self):
        geom = MultiPolygon(Polygon(((0, 0), (0, 1), (1, 0), (1, 1), (0, 0))))
        self.assertEqual(self.parser.filter_geom("geom", geom), None)
        self.assertTrue(self.parser.warnings)

    def test_polygon(self):
        geom = Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0)))
        self.assertEqual(self.parser.filter_geom("geom", geom), MultiPolygon(geom))
        self.assertFalse(self.parser.warnings)

    def test_multipolygon(self):
        geom = MultiPolygon(Polygon(((0, 0), (0, 1), (1, 1), (1, 0), (0, 0))))
        self.assertEqual(self.parser.filter_geom("geom", geom), geom)
        self.assertFalse(self.parser.warnings)


class TestDistrictOpenStreetMapParser(OpenStreetMapDistrictParser):
    provider = "OpenStreetMap"
    tags = [
        [{"boundary": "administrative"}, {"admin_level": "6"}]
    ]


class OpenStreetMapDistrictParser(TestCase):

    @mock.patch("geotrek.common.parsers.requests.get")
    def import_district(self, nominatim_file, mocked):
        def mocked_json_overpass():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "district_OSM.json"
            )
            with open(filename) as f:
                return json.load(f)

        def mocked_json_nominatim():
            filename = os.path.join(
                os.path.dirname(__file__), "data", nominatim_file
            )
            with open(filename) as f:
                return json.load(f)

        response1 = mock.Mock()
        response1.json = mocked_json_overpass
        response1.status_code = 200

        response2 = mock.Mock()
        response2.json = mocked_json_nominatim
        response2.status_code = 200

        mocked.side_effect = [response1, response2]

        call_command(
            "import",
            "geotrek.zoning.tests.test_parsers.TestDistrictOpenStreetMapParser",
        )

        self.district = District.objects.order_by("pk").all()

    def test_query_OSM(self):
        query = TestDistrictOpenStreetMapParser().build_query()

        self.assertIn("(relation['boundary'='administrative']['admin_level'='6'];);out tags;", query)

    def test_multipolygon_OSM(self):
        nominatim_file = os.path.join(os.path.dirname(__file__), "data", "district_multipolygon.json")
        self.import_district(nominatim_file)

        self.assertEqual(len(self.district), 1)
        self.assertEqual(type(self.district[0].geom), MultiPolygon)
        self.assertEqual(len(self.district[0].geom), 2)

        # test the first point of each polygon
        self.assertAlmostEqual(self.district[0].geom.coords[0][0][0][0], 869953.4333298746)
        self.assertAlmostEqual(self.district[0].geom.coords[0][0][0][1], 6365109.915336954)

        self.assertAlmostEqual(self.district[0].geom.coords[1][0][0][0], 872596.9093673624)
        self.assertAlmostEqual(self.district[0].geom.coords[1][0][0][1], 6367024.025305742)

    def test_polygon_OSM(self):
        nominatim_file = os.path.join(os.path.dirname(__file__), "data", "district_polygon.json")
        self.import_district(nominatim_file)

        self.assertEqual(len(self.district), 1)
        self.assertEqual(type(self.district[0].geom), MultiPolygon)
        self.assertEqual(len(self.district[0].geom), 1)

        # test the first point of each polygon
        self.assertAlmostEqual(self.district[0].geom.coords[0][0][0][0], 872596.9093673624)
        self.assertAlmostEqual(self.district[0].geom.coords[0][0][0][1], 6367024.025305742)

    def test_name_OSM(self):
        nominatim_file = os.path.join(os.path.dirname(__file__), "data", "district_polygon.json")
        self.import_district(nominatim_file)

        self.assertEqual(self.district[0].name, "Venterol")
