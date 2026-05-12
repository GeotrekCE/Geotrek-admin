import os
from io import StringIO
from unittest import mock, skipIf
from unittest.mock import patch

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.management import call_command
from django.test import TestCase

from geotrek.core.tests.factories import PathFactory
from geotrek.trekking.management.commands.loadpoi import Command
from geotrek.trekking.models import POI


class LoadPOITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filename = os.path.join(os.path.dirname(__file__), "data", "poi.shp")
        cls.path = PathFactory.create()

    def setUp(self):
        self.cmd = Command()

    def test_command_shows_number_of_objects(self):
        output = StringIO()
        call_command(
            "loadpoi",
            self.filename,
            verbosity=2,
            name_field="name",
            type_field="type",
            stdout=output,
        )
        self.assertIn("2 objects found", output.getvalue())

    def test_command_fail_type_missing(self):
        output = StringIO()
        call_command(
            "loadpoi", self.filename, verbosity=1, name_field="name", stdout=output
        )
        self.assertIn("Set it with --type-field, or set a default", output.getvalue())

    def test_command_fail_name_missing(self):
        output = StringIO()
        call_command(
            "loadpoi", self.filename, verbosity=1, type_field="type", stdout=output
        )
        self.assertIn("Set it with --name-field, or set a default", output.getvalue())

    @mock.patch("geotrek.trekking.management.commands.loadpoi.Command.create_poi")
    def test_command_fail_rollback(self, mocke):
        mocke.side_effect = Exception("This is a test")
        output = StringIO()
        with self.assertRaises(Exception):
            call_command(
                "loadpoi",
                self.filename,
                verbosity=1,
                name_field="name",
                type_field="type",
                stdout=output,
            )
        self.assertIn("An error occured, rolling back operations.", output.getvalue())
        self.assertEqual(POI.objects.count(), 0)

    def test_create_pois_is_executed(self):
        with patch.object(Command, "create_poi") as mocked:
            self.cmd.handle(
                point_layer=self.filename,
                verbosity=0,
                name_field="name",
                type_field="type",
                encoding="utf-8",
            )
            self.assertEqual(mocked.call_count, 2)

    def test_create_pois_receives_geometries(self):
        with patch.object(Command, "create_poi") as mocked:
            self.cmd.handle(
                point_layer=self.filename,
                verbosity=0,
                name_field="name",
                type_field="type",
                encoding="utf-8",
            )
            call1 = mocked.call_args_list[0][0]
            call2 = mocked.call_args_list[1][0]
            self.assertAlmostEqual(call1[0].x, -1.3630867, places=7)
            self.assertAlmostEqual(call1[0].y, -5.9835847, places=7)
            self.assertAlmostEqual(call2[0].x, -1.3630872, places=7)
            self.assertAlmostEqual(call2[0].y, -5.9835842, places=7)
            self.assertEqual(call1[0].geom_type, "Point")

    def test_create_pois_receives_fields_names_and_types(self):
        with patch.object(Command, "create_poi") as mocked:
            self.cmd.handle(
                point_layer=self.filename,
                verbosity=0,
                name_field="name",
                type_field="type",
                encoding="utf-8",
            )
            call1 = mocked.call_args_list[0][0]
            call2 = mocked.call_args_list[1][0]
            self.assertEqual(call1[1], "pont")
            self.assertEqual(call2[1], "pancarte 1")
            self.assertEqual(call1[2], "équipement")
            self.assertEqual(call2[2], "signaletique")

    def test_create_pois_name_default_if_field_missing(self):
        with patch.object(Command, "create_poi") as mocked:
            self.cmd.handle(
                point_layer=self.filename,
                verbosity=0,
                name_default="test",
                type_field="type",
                encoding="utf-8",
            )
            call1 = mocked.call_args_list[0][0]
            self.assertEqual(call1[1], "test")

    def test_pois_are_created(self):
        geom = GEOSGeometry("POINT(1 1)", srid=4326)
        before = len(POI.objects.all())
        self.cmd.create_poi(geom, "bridge", "infra", "description")
        after = len(POI.objects.all())
        self.assertEqual(after - before, 1)

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_pois_are_attached_to_paths(self):
        geom = GEOSGeometry("POINT(1 1)", srid=4326)
        poi = self.cmd.create_poi(geom, "bridge", "infra", "description")
        self.assertEqual([self.path], list(poi.paths.all()))
