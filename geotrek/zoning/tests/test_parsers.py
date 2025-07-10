import json
import os
from io import StringIO
from unittest import mock

from django.contrib.gis.geos import MultiPolygon, Polygon, WKTWriter
from django.core.management import CommandError, call_command
from django.test import TestCase

from geotrek.zoning.models import City, District, RestrictedArea, RestrictedAreaType
from geotrek.zoning.parsers import (
    CityParser,
    OpenStreetMapCityParser,
    OpenStreetMapDistrictParser,
    OpenStreetMapRestrictedAreaParser,
)

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
    tags = [[{"boundary": "administrative"}, {"admin_level": "6"}]]


class OpenStreetMapDistrictParserTests(TestCase):
    @mock.patch("geotrek.common.parsers.requests.get")
    def import_district(self, nominatim_file, mocked):
        def mocked_json_overpass():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "district_OSM.json"
            )
            with open(filename) as f:
                return json.load(f)

        def mocked_json_nominatim():
            filename = os.path.join(os.path.dirname(__file__), "data", nominatim_file)
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

        self.districts = District.objects.order_by("pk").all()

    def test_query_OSM(self):
        query = TestDistrictOpenStreetMapParser().build_query()

        self.assertIn(
            "(relation['boundary'='administrative']['admin_level'='6'];);out tags;",
            query,
        )

    def test_multipolygon_OSM(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_multipolygon.json"
        )
        self.import_district(nominatim_file)

        self.assertEqual(len(self.districts), 1)
        self.assertEqual(type(self.districts[0].geom), MultiPolygon)
        self.assertEqual(len(self.districts[0].geom), 2)

        # test the first point of each polygon
        self.assertAlmostEqual(
            self.districts[0].geom.coords[0][0][0][0], 869953.433, places=2
        )
        self.assertAlmostEqual(
            self.districts[0].geom.coords[0][0][0][1], 6365109.915, places=2
        )

        self.assertAlmostEqual(
            self.districts[0].geom.coords[1][0][0][0], 872596.909, places=2
        )
        self.assertAlmostEqual(
            self.districts[0].geom.coords[1][0][0][1], 6367024.025, places=2
        )

    def test_polygon_OSM(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_polygon.json"
        )
        self.import_district(nominatim_file)

        self.assertEqual(len(self.districts), 1)
        self.assertEqual(type(self.districts[0].geom), MultiPolygon)
        self.assertEqual(len(self.districts[0].geom), 1)

        # test the first point of each polygon
        self.assertAlmostEqual(
            self.districts[0].geom.coords[0][0][0][0], 872596.909, places=2
        )
        self.assertAlmostEqual(
            self.districts[0].geom.coords[0][0][0][1], 6367024.025, places=2
        )

    def test_name_OSM(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_polygon.json"
        )
        self.import_district(nominatim_file)

        self.assertEqual(self.districts[0].name, "Venterol")


class TestRestrictedAreaOpenStreetMapParser(OpenStreetMapRestrictedAreaParser):
    provider = "OpenStreetMap"
    tags = [{"protected_area": "2"}]
    area_type = "Inconnu"


class OpenStreetMapRestrictedAreaParserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.area_type = RestrictedAreaType.objects.create(name="Inconnu")

    @mock.patch("geotrek.common.parsers.requests.get")
    def import_restrictedarea(self, nominatim_file, status_code, mocked):
        def mocked_json_overpass():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "restrictedarea_OSM.json"
            )
            with open(filename) as f:
                return json.load(f)

        def mocked_json_nominatim():
            filename = os.path.join(os.path.dirname(__file__), "data", nominatim_file)
            with open(filename) as f:
                return json.load(f)

        response1 = mock.Mock()
        response1.json = mocked_json_overpass
        response1.status_code = 200

        response2 = mock.Mock()
        response2.json = mocked_json_nominatim
        response2.status_code = status_code

        mocked.side_effect = [response1, response2]

        output = StringIO()
        call_command(
            "import",
            "geotrek.zoning.tests.test_parsers.TestRestrictedAreaOpenStreetMapParser",
            verbosity=2,
            stdout=output,
        )

        self.output = output.getvalue()
        self.restricted_areas = RestrictedArea.objects.order_by("pk").all()

    def test_multipolygon_OSM(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_multipolygon.json"
        )
        self.import_restrictedarea(nominatim_file, 200)

        self.assertEqual(self.restricted_areas.count(), 1)
        self.assertEqual(type(self.restricted_areas[0].geom), MultiPolygon)
        self.assertEqual(len(self.restricted_areas[0].geom), 2)

        # test the first point of each polygon
        self.assertAlmostEqual(
            self.restricted_areas[0].geom.coords[0][0][0][0], 869953.433, places=2
        )
        self.assertAlmostEqual(
            self.restricted_areas[0].geom.coords[0][0][0][1], 6365109.915, places=2
        )

        self.assertAlmostEqual(
            self.restricted_areas[0].geom.coords[1][0][0][0], 872596.909, places=2
        )
        self.assertAlmostEqual(
            self.restricted_areas[0].geom.coords[1][0][0][1], 6367024.025, places=2
        )

    def test_polygon_OSM(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_polygon.json"
        )
        self.import_restrictedarea(nominatim_file, 200)

        self.assertEqual(self.restricted_areas.count(), 1)
        self.assertEqual(type(self.restricted_areas[0].geom), MultiPolygon)
        self.assertEqual(len(self.restricted_areas[0].geom), 1)

        # test the first point of each polygon
        self.assertAlmostEqual(
            self.restricted_areas[0].geom.coords[0][0][0][0], 872596.909, places=2
        )
        self.assertAlmostEqual(
            self.restricted_areas[0].geom.coords[0][0][0][1], 6367024.025, places=2
        )

    def test_geom_does_not_exist(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_polygon.json"
        )
        self.import_restrictedarea(nominatim_file, 404)

        self.assertEqual(self.restricted_areas.count(), 0)

        self.assertIn(
            "Failed to fetch https://nominatim.openstreetmap.org/lookup after 1 attempt(s).",
            self.output,
        )

    def test_name_OSM(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_polygon.json"
        )
        self.import_restrictedarea(nominatim_file, 200)

        self.assertEqual(
            self.restricted_areas[0].name,
            "Parc Naturel Régional des Pyrénées Ariégeoises",
        )


class TestCityOpenStreetMapParser(OpenStreetMapCityParser):
    provider = "OpenStreetMap"
    tags = [[{"boundary": "administrative"}, {"admin_level": "8"}]]
    code_tag = "ref:INSEE"


class OpenStreetMapCityParserTests(TestCase):
    @mock.patch("geotrek.common.parsers.requests.get")
    def import_cities(self, nominatim_file, status_code, mocked):
        def mocked_json_overpass():
            filename = os.path.join(os.path.dirname(__file__), "data", "city_OSM.json")
            with open(filename) as f:
                return json.load(f)

        def mocked_json_nominatim():
            filename = os.path.join(os.path.dirname(__file__), "data", nominatim_file)
            with open(filename) as f:
                return json.load(f)

        response1 = mock.Mock()
        response1.json = mocked_json_overpass
        response1.status_code = 200

        response2 = mock.Mock()
        response2.json = mocked_json_nominatim
        response2.status_code = status_code

        mocked.side_effect = [response1, response2]

        output = StringIO()
        call_command(
            "import",
            "geotrek.zoning.tests.test_parsers.TestCityOpenStreetMapParser",
            verbosity=2,
            stdout=output,
        )

        self.output = output.getvalue()
        self.cities = City.objects.order_by("pk").all()

    def test_multipolygon_OSM(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_multipolygon.json"
        )
        self.import_cities(nominatim_file, 200)

        self.assertEqual(self.cities.count(), 1)
        self.assertEqual(type(self.cities[0].geom), MultiPolygon)
        self.assertEqual(len(self.cities[0].geom), 2)

        # test the first point of each polygon
        self.assertAlmostEqual(
            self.cities[0].geom.coords[0][0][0][0], 869953.433, places=2
        )
        self.assertAlmostEqual(
            self.cities[0].geom.coords[0][0][0][1], 6365109.915, places=2
        )

        self.assertAlmostEqual(
            self.cities[0].geom.coords[1][0][0][0], 872596.909, places=2
        )
        self.assertAlmostEqual(
            self.cities[0].geom.coords[1][0][0][1], 6367024.025, places=2
        )

    def test_polygon_OSM(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_polygon.json"
        )
        self.import_cities(nominatim_file, 200)

        self.assertEqual(self.cities.count(), 1)
        self.assertEqual(type(self.cities[0].geom), MultiPolygon)
        self.assertEqual(len(self.cities[0].geom), 1)

        # test the first point of each polygon
        self.assertAlmostEqual(
            self.cities[0].geom.coords[0][0][0][0], 872596.909, places=2
        )
        self.assertAlmostEqual(
            self.cities[0].geom.coords[0][0][0][1], 6367024.025, places=2
        )

    def test_geom_does_not_exist(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_polygon.json"
        )
        self.import_cities(nominatim_file, 404)

        self.assertEqual(self.cities.count(), 0)

        self.assertIn(
            "Failed to fetch https://nominatim.openstreetmap.org/lookup after 1 attempt(s).",
            self.output,
        )

    def test_create_OSM(self):
        nominatim_file = os.path.join(
            os.path.dirname(__file__), "data", "OSM_polygon.json"
        )
        self.import_cities(nominatim_file, 200)

        self.assertEqual(self.cities.count(), 1)

        self.assertEqual(self.cities[0].name, "Paizay-le-Sec")
        self.assertEqual(
            self.cities[0].code,
            "86187",
        )
