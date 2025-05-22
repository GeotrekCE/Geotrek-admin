import os
from io import StringIO

from django.contrib.gis.gdal import GDALException
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from geotrek.zoning.models import City, District, RestrictedArea, RestrictedAreaType


class RestrictedAreasCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filename_out_in = os.path.join(
            os.path.dirname(__file__), "data", "polygons_in_out.geojson"
        )
        cls.filename = os.path.join(os.path.dirname(__file__), "data", "city.shp")

    """
    Get Restricted Area
    """

    def test_load_restricted_areas_without_file(self):
        with self.assertRaisesRegex(
            CommandError,
            "Error: the following arguments are required: file_path, area_type",
        ):
            call_command("loadrestrictedareas")

    def test_load_cities_without_type(self):
        with self.assertRaisesRegex(
            CommandError, "Error: the following arguments are required: area_type"
        ):
            call_command("loadrestrictedareas", self.filename_out_in)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_restrictedareas_with_one_inside_one_outside_within(self):
        output = StringIO()
        call_command(
            "loadrestrictedareas",
            self.filename_out_in,
            "type_area",
            name="NOM",
            verbosity=2,
            stdout=output,
        )
        self.assertEqual(RestrictedArea.objects.count(), 1)
        self.assertEqual(RestrictedAreaType.objects.first().name, "type_area")
        value = RestrictedArea.objects.first()
        self.assertEqual("coucou", value.name)
        self.assertIn("RestrictedArea Type's type_area created", output.getvalue())
        self.assertIn("Created coucou", output.getvalue())

    @override_settings(SRID=4326, SPATIAL_EXTENT=(10, 11, 11, 12))
    def test_load_restrictedareas_not_within(self):
        call_command(
            "loadrestrictedareas",
            self.filename_out_in,
            "type_area",
            name="NOM",
            verbosity=0,
        )
        self.assertEqual(RestrictedArea.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(10, 11, 11, 12))
    def test_load_restrictedareas_not_intersect(self):
        call_command(
            "loadrestrictedareas",
            self.filename_out_in,
            "type_area",
            "-i",
            name="NOM",
            verbosity=0,
        )
        self.assertEqual(RestrictedArea.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_restrictedareas_with_one_inside_one_outside_intersect(self):
        output = StringIO()
        call_command(
            "loadrestrictedareas",
            self.filename_out_in,
            "type_area",
            "-i",
            name="NOM",
            verbosity=2,
            stdout=output,
        )
        self.assertEqual(RestrictedArea.objects.count(), 2)
        value_1 = RestrictedArea.objects.first()
        self.assertEqual("coucou", value_1.name)
        value_2 = RestrictedArea.objects.last()
        self.assertEqual("lulu", value_2.name)
        output = output.getvalue()
        self.assertIn("Created coucou", output)
        self.assertIn("Created lulu", output)

        output_2 = StringIO()
        call_command(
            "loadrestrictedareas",
            self.filename_out_in,
            "type_area",
            "-i",
            name="NOM",
            verbosity=2,
            stdout=output_2,
        )
        output = output_2.getvalue()
        self.assertIn("Updated coucou", output)
        self.assertIn("Updated lulu", output)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_restricted_areas_no_match_properties(self):
        output = StringIO()
        call_command(
            "loadrestrictedareas",
            self.filename_out_in,
            "type_area",
            name="toto",
            stdout=output,
        )
        self.assertIn("NOM, Insee", output.getvalue())
        output_2 = StringIO()
        call_command(
            "loadrestrictedareas",
            self.filename_out_in,
            "type_area",
            "-i",
            name="toto",
            stdout=output_2,
        )
        self.assertIn("NOM, Insee", output.getvalue())

    def test_load_restricted_areas_fail_bad_srid(self):
        with self.assertRaisesRegex(
            CommandError, "SRID is not well configurate, change/add option srid"
        ):
            call_command(
                "loadrestrictedareas",
                self.filename,
                "type_area",
                name="NOM",
                verbosity=0,
            )

    def test_load_restricted_areas_with_geom_not_valid(self):
        output = StringIO()
        call_command(
            "loadrestrictedareas",
            os.path.join(
                os.path.dirname(__file__), "data", "polygon_not_valid.geojson"
            ),
            "type_area",
            name="NOM",
            srid=2154,
            verbosity=1,
            stdout=output,
        )
        self.assertEqual(RestrictedArea.objects.count(), 0)
        self.assertIn("wrong_polygon's geometry is not valid", output.getvalue())

    def test_load_restricted_areas_with_line(self):
        output = StringIO()
        filename_line = os.path.join(os.path.dirname(__file__), "data", "line.geojson")
        call_command(
            "loadrestrictedareas",
            filename_line,
            "type_area",
            name="NOM",
            srid=2154,
            verbosity=2,
            stdout=output,
        )
        self.assertIn("coucou's geometry is not a polygon", output.getvalue())


class CitiesCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filename = os.path.join(os.path.dirname(__file__), "data", "city.shp")
        cls.filename_out_in = os.path.join(
            os.path.dirname(__file__), "data", "polygons_in_out.geojson"
        )

    """
    Get cities
    """

    def test_load_cities_without_file(self):
        with self.assertRaisesRegex(
            CommandError, "Error: the following arguments are required: file_path"
        ):
            call_command("loadcities")

    @override_settings(SPATIAL_EXTENT=(0, 10.0, 1, 11))
    def test_load_cities_out_of_spatial_extent(self):
        call_command(
            "loadcities",
            self.filename,
            name="NOM",
            code="Insee",
            srid=2154,
            verbosity=0,
        )
        self.assertEqual(City.objects.count(), 0)

    @override_settings(SPATIAL_EXTENT=(0, 6000000.0, 400000.0, 7000000))
    def test_load_cities_within_spatial_extent(self):
        output = StringIO()
        call_command(
            "loadcities",
            self.filename,
            name="NOM",
            code="Insee",
            srid=2154,
            verbosity=2,
            stdout=output,
        )
        value = City.objects.first()
        self.assertEqual("99999", value.code)
        self.assertEqual("Trifouilli-les-Oies", value.name)
        self.assertEqual(City.objects.count(), 1)
        self.assertIn("Created Trifouilli-les-Oies", output.getvalue())
        call_command(
            "loadcities",
            self.filename,
            name="NOM",
            code="Insee",
            srid=2154,
            verbosity=2,
            stdout=output,
        )
        self.assertIn("Updated Trifouilli-les-Oies", output.getvalue())

    def test_load_cities_with_geom_not_valid(self):
        output = StringIO()
        call_command(
            "loadcities",
            os.path.join(
                os.path.dirname(__file__), "data", "polygon_not_valid.geojson"
            ),
            name="NOM",
            code="Insee",
            srid=2154,
            verbosity=1,
            stdout=output,
        )
        self.assertEqual(City.objects.count(), 0)
        self.assertIn("wrong_polygon's geometry is not valid", output.getvalue())

    def test_load_cities_fail_bad_srid(self):
        with self.assertRaisesRegex(
            CommandError, "SRID is not well configurate, change/add option srid"
        ):
            call_command(
                "loadcities", self.filename, name="NOM", code="Insee", verbosity=0
            )

    def test_load_cities_with_bad_file(self):
        with self.assertRaisesRegex(
            GDALException, 'Could not open the datasource at "toto.geojson"'
        ):
            call_command(
                "loadcities",
                "toto.geojson",
                name="NOM",
                code="Insee",
                srid=2154,
                verbosity=0,
            )

    def test_load_cities_with_line(self):
        output = StringIO()
        filename_line = os.path.join(os.path.dirname(__file__), "data", "line.geojson")
        call_command(
            "loadcities",
            filename_line,
            name="NOM",
            code="Insee",
            verbosity=2,
            stdout=output,
        )
        self.assertIn("coucou's geometry is not a polygon", output.getvalue())

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_cities_with_one_inside_one_outside_within(self):
        call_command(
            "loadcities", self.filename_out_in, name="NOM", code="Insee", verbosity=0
        )
        self.assertEqual(City.objects.count(), 1)
        value = City.objects.first()
        self.assertEqual("0", value.code)
        self.assertEqual("coucou", value.name)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(10, 11, 11, 12))
    def test_load_cities_not_within(self):
        call_command(
            "loadcities", self.filename_out_in, name="NOM", code="Insee", verbosity=0
        )
        self.assertEqual(City.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(10, 11, 11, 12))
    def test_load_cities_not_intersect(self):
        call_command(
            "loadcities",
            self.filename_out_in,
            "-i",
            name="NOM",
            code="Insee",
            verbosity=0,
        )
        self.assertEqual(City.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_cities_with_one_inside_one_outside_intersect(self):
        output = StringIO()
        call_command(
            "loadcities",
            self.filename_out_in,
            "-i",
            name="NOM",
            code="Insee",
            verbosity=2,
            stdout=output,
        )
        self.assertEqual(City.objects.count(), 2)
        value_1 = City.objects.first()
        self.assertEqual("0", value_1.code)
        self.assertEqual("coucou", value_1.name)
        value_2 = City.objects.last()
        self.assertEqual("1", value_2.code)
        self.assertEqual("lulu", value_2.name)
        output = output.getvalue()
        output_2 = StringIO()
        self.assertIn("Created coucou", output)
        self.assertIn("Created lulu", output)
        call_command(
            "loadcities",
            self.filename_out_in,
            "-i",
            name="NOM",
            code="Insee",
            verbosity=2,
            stdout=output_2,
        )
        output = output_2.getvalue()
        self.assertIn("Updated coucou", output)
        self.assertIn("Updated lulu", output)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_cities_no_match_properties(self):
        output = StringIO()
        call_command(
            "loadcities", self.filename_out_in, name="toto", code="tata", stdout=output
        )
        self.assertIn("NOM, Insee", output.getvalue())
        call_command(
            "loadcities",
            self.filename_out_in,
            "-i",
            name="toto",
            code="tata",
            stdout=output,
        )
        self.assertIn("NOM, Insee", output.getvalue())


class DistrictsCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filename = os.path.join(
            os.path.dirname(__file__), "data", "polygons_in_out.geojson"
        )

    """
    Get cities
    """

    def test_load_districts_without_file(self):
        with self.assertRaisesRegex(
            CommandError, "Error: the following arguments are required: file_path"
        ):
            call_command("loaddistricts")

    def test_load_districts_with_geom_not_valid(self):
        output = StringIO()
        call_command(
            "loaddistricts",
            os.path.join(
                os.path.dirname(__file__), "data", "polygon_not_valid.geojson"
            ),
            name="NOM",
            srid=2154,
            verbosity=1,
            stdout=output,
        )
        self.assertEqual(District.objects.count(), 0)
        self.assertIn("wrong_polygon's geometry is not valid", output.getvalue())

    @override_settings(SPATIAL_EXTENT=(0, 10.0, 1, 11))
    def test_load_districts_out_of_spatial_extent(self):
        call_command("loaddistricts", self.filename, name="NOM", srid=2154, verbosity=0)
        self.assertEqual(District.objects.count(), 0)

    def test_load_districts_fail_bad_srid(self):
        filename = os.path.join(os.path.dirname(__file__), "data", "bad_srid.geojson")
        with self.assertRaisesRegex(
            CommandError, "SRID is not well configurate, change/add option srid"
        ):
            call_command("loaddistricts", filename, name="NOM", verbosity=0)

    def test_load_districts_with_bad_file(self):
        with self.assertRaisesRegex(
            GDALException, 'Could not open the datasource at "toto.geojson"'
        ):
            call_command(
                "loaddistricts", "toto.geojson", name="NOM", srid=2154, verbosity=0
            )

    def test_load_districts_with_line(self):
        output = StringIO()
        filename_line = os.path.join(os.path.dirname(__file__), "data", "line.geojson")
        call_command(
            "loaddistricts", filename_line, name="NOM", verbosity=2, stdout=output
        )
        self.assertIn("coucou's geometry is not a polygon", output.getvalue())

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_districts_with_one_inside_one_outside_within(self):
        output = StringIO()
        call_command(
            "loaddistricts", self.filename, name="NOM", verbosity=2, stdout=output
        )
        self.assertEqual(District.objects.count(), 1)
        value = District.objects.first()
        self.assertEqual("coucou", value.name)
        output = output.getvalue()
        self.assertIn("Created coucou", output)
        output_2 = StringIO()
        call_command(
            "loaddistricts", self.filename, name="NOM", verbosity=2, stdout=output_2
        )
        output = output_2.getvalue()
        self.assertIn("Updated coucou", output)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(10, 11, 11, 12))
    def test_load_districts_not_within(self):
        call_command("loaddistricts", self.filename, name="NOM", verbosity=0)
        self.assertEqual(District.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(10, 11, 11, 12))
    def test_load_districts_not_intersect(self):
        call_command("loaddistricts", self.filename, "-i", name="NOM", verbosity=0)
        self.assertEqual(District.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_districts_with_one_inside_one_outside_intersect(self):
        output = StringIO()
        call_command(
            "loaddistricts", self.filename, "-i", name="NOM", verbosity=2, stdout=output
        )
        self.assertEqual(District.objects.count(), 2)
        value_1 = District.objects.first()
        self.assertEqual("coucou", value_1.name)
        value_2 = District.objects.last()
        self.assertEqual("lulu", value_2.name)
        output = output.getvalue()
        self.assertIn("Created coucou", output)
        self.assertIn("Created lulu", output)
        output_2 = StringIO()
        call_command(
            "loaddistricts",
            self.filename,
            "-i",
            name="NOM",
            verbosity=2,
            stdout=output_2,
        )
        output = output_2.getvalue()
        self.assertIn("Updated coucou", output)
        self.assertIn("Updated lulu", output)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -3, 2, 2))
    def test_load_districts_no_match_properties(self):
        output = StringIO()
        call_command("loaddistricts", self.filename, name="toto", stdout=output)
        self.assertIn("NOM, Insee", output.getvalue())
        call_command("loaddistricts", self.filename, "-i", name="toto", stdout=output)
        self.assertIn("NOM, Insee", output.getvalue())
