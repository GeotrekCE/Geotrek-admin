import os
from io import StringIO

from django.contrib.gis.geos.error import GEOSException
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from geotrek.authent.tests.factories import StructureFactory
from geotrek.diving.models import Dive
from geotrek.diving.tests.factories import DiveFactory


class DiveCommandTest(TestCase):
    """
    There are 2 dives in the file dive.shp

    name        eid         depth

    coucou      eid1        2010
    name        eid2        5
    """

    def test_load_dive_eid(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "dive.shp")
        DiveFactory.create(name="name", eid="eid1", depth=10)
        call_command(
            "loaddive",
            filename,
            name_field="name",
            depth_field="depth",
            eid_field="eid",
            practice_default="Practice",
            structure_default="structure",
            verbosity=2,
            stdout=output,
        )
        self.assertIn("Dives will be linked to %s" % structure, output.getvalue())
        self.assertIn("2 objects created.", output.getvalue())
        value = Dive.objects.filter(name="name")
        self.assertEqual(
            5, value[0].depth
        )  # The dive was updated because has the same eid (eid1)
        self.assertEqual("Practice", value[0].practice.name)
        self.assertEqual(value.count(), 1)
        self.assertEqual(Dive.objects.count(), 2)
        self.assertAlmostEqual(value[0].geom.x, -436345.704831, places=5)
        self.assertAlmostEqual(value[0].geom.y, 1176487.742917, places=5)

    def test_load_dive_no_eid(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "dive.shp")
        DiveFactory.create(name="name", eid="eid1", depth=10)
        call_command(
            "loaddive",
            filename,
            name_field="name",
            depth_field="depth",
            practice_default="Practice",
            structure_default="structure",
            verbosity=2,
            stdout=output,
        )
        self.assertIn("Dives will be linked to %s" % structure, output.getvalue())
        self.assertIn("2 objects created.", output.getvalue())
        value = Dive.objects.filter(name="name")
        self.assertEqual(10, value[0].depth)  # The dive was not updated
        self.assertEqual(5, value[1].depth)
        self.assertEqual("Practice", value[1].practice.name)
        self.assertEqual(value.count(), 2)
        self.assertEqual(Dive.objects.count(), 3)
        self.assertAlmostEqual(value[1].geom.x, -436345.704831, places=5)
        self.assertAlmostEqual(value[1].geom.y, 1176487.742917, places=5)

    def test_load_dive_no_eid_no_practice_default(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "dive.shp")
        call_command(
            "loaddive",
            filename,
            name_field="name",
            depth_field="depth",
            structure_default="structure",
            verbosity=2,
            stdout=output,
        )
        self.assertIn("Dives will be linked to %s" % structure, output.getvalue())
        self.assertIn("2 objects created.", output.getvalue())
        value = Dive.objects.get(name="name")
        self.assertIsNone(value.practice)

    def test_load_wrong_type_geom(self):
        output = StringIO()
        StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "line.geojson")
        with self.assertRaises(GEOSException):
            call_command(
                "loaddive",
                filename,
                name_field="name",
                depth_field="depth",
                practice_default="Practice",
                structure_default="structure",
                verbosity=2,
                stdout=output,
            )
        self.assertIn("An error occured, rolling back operations.", output.getvalue())
        self.assertEqual(Dive.objects.count(), 0)

    def test_no_file_fail(self):
        with self.assertRaisesRegex(CommandError, "File does not exists at: toto.shp"):
            call_command("loaddive", "toto.shp")

    def test_load_dive_wrong_structure_default(self):
        output = StringIO()
        StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "dive.shp")
        DiveFactory.create(name="name", eid="eid1", depth=10)
        call_command(
            "loaddive",
            filename,
            name_field="name",
            depth_field="depth",
            practice_default="Practice",
            structure_default="wrong_structure_default",
            verbosity=2,
            stdout=output,
        )
        self.assertIn(
            "Structure wrong_structure_default set in options doesn't exist",
            output.getvalue(),
        )

    def test_load_dive_good_multipoints(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(
            os.path.dirname(__file__), "data", "dive_good_multipoint.geojson"
        )
        call_command(
            "loaddive",
            filename,
            name_field="name",
            depth_field="depth",
            practice_default="Practice",
            structure_default="structure",
            verbosity=2,
            stdout=output,
        )
        self.assertIn("Dives will be linked to %s" % structure, output.getvalue())
        self.assertIn("1 objects created.", output.getvalue())
        value = Dive.objects.get(name="name")
        self.assertEqual(10, value.depth)
        self.assertEqual("Practice", value.practice.name)
        self.assertAlmostEqual(value.geom.x, 402314.30044897617)
        self.assertAlmostEqual(value.geom.y, 905126.7898456538)

    def test_load_dive_bad_multipoints(self):
        output = StringIO()
        StructureFactory.create(name="structure")
        filename = os.path.join(
            os.path.dirname(__file__), "data", "dive_bad_multipoint.geojson"
        )
        with self.assertRaisesRegex(
            CommandError,
            "One of your geometry is a MultiPoint object with multiple points",
        ):
            call_command(
                "loaddive",
                filename,
                name_field="name",
                depth_field="depth",
                practice_default="Practice",
                structure_default="structure",
                verbosity=2,
                stdout=output,
            )

    def test_wrong_fields_fail(self):
        StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "dive.shp")
        output = StringIO()
        call_command(
            "loaddive",
            filename,
            name_field="wrong_name_field",
            structure_default="structure",
            stdout=output,
        )
        call_command(
            "loaddive",
            filename,
            name_field="name",
            depth_field="wrong_depth_field",
            structure_default="structure",
            stdout=output,
        )
        call_command(
            "loaddive",
            filename,
            name_field="name",
            depth_field="depth",
            eid_field="wrong_eid_field",
            structure_default="structure",
            stdout=output,
        )
        elements_to_check = ["wrong_name_field", "wrong_depth_field", "wrong_eid_field"]
        self.assertEqual(output.getvalue().count("Set it with"), 2)
        self.assertEqual(output.getvalue().count("Change your --eid-field option"), 1)
        for element in elements_to_check:
            self.assertIn(
                "Field '{}' not found in data source".format(element), output.getvalue()
            )
