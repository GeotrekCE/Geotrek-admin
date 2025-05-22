import os
import tempfile
from io import StringIO

from django.contrib.gis.geos.error import GEOSException
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from geotrek.authent.tests.factories import StructureFactory
from geotrek.common.tests.utils import update_gis
from geotrek.core.tests.factories import PathFactory
from geotrek.signage.models import Signage
from geotrek.signage.tests.factories import SignageFactory


class SignageCommandTest(TestCase):
    """
    There are 3 signages in the file signage.shp
    """

    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory.create()

    def test_load_signage(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "signage.shp")
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_default="name",
            condition_default="conditions",
            condition_field="conditions",
            structure_default="structure",
            description_default="description",
            year_default=2010,
            verbosity=2,
            stdout=output,
        )
        self.assertIn(f"Signages will be linked to {structure}", output.getvalue())
        self.assertIn("3 objects created.", output.getvalue())
        qs_signages = Signage.objects.filter(name="name")
        self.assertEqual(2010, qs_signages[0].implantation_year)
        self.assertEqual(qs_signages.count(), 3)
        self.assertAlmostEqual(qs_signages[0].geom.x, -436345.704831, places=5)
        self.assertAlmostEqual(qs_signages[0].geom.y, 1176487.742917, places=5)
        self.assertAlmostEqual(qs_signages[1].geom.x, -436345.505347, places=5)
        self.assertAlmostEqual(qs_signages[1].geom.y, 1176480.918334, places=5)
        self.assertEqual("condition", qs_signages[0].conditions.first().label)
        self.assertEqual("condition", qs_signages[1].conditions.first().label)
        self.assertEqual("condition", qs_signages[2].conditions.first().label)

    def test_load_signage_multipoints(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(
            os.path.dirname(__file__), "data", "signage_good_multipoint.geojson"
        )
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_default="name",
            condition_default="conditions",
            structure_default="structure",
            description_default="description",
            year_default=2010,
            verbosity=2,
            stdout=output,
        )
        self.assertIn(f"Signages will be linked to {structure}", output.getvalue())
        self.assertIn("1 objects created.", output.getvalue())
        value = Signage.objects.first()
        self.assertEqual("name", value.name)
        self.assertEqual(2010, value.implantation_year)
        self.assertEqual(Signage.objects.count(), 1)

    def test_load_signage_none_year(self):
        """Loading a signage with a year set to None should not fail."""

        input_file_path = os.path.join(os.path.dirname(__file__), "data", "signage.shp")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file_path = os.path.join(tmp_dir, "signage_none_year.shp")
            update_gis(input_file_path, output_file_path, {"year": None})

            output = StringIO()
            StructureFactory.create(name="structure")
            call_command(
                "loadsignage",
                output_file_path,
                type_default="label",
                name_default="name",
                condition_default="conditions",
                structure_default="structure",
                description_default="description",
                year_field="year",
                stdout=output,
            )

            value = Signage.objects.first()
            self.assertEqual(None, value.implantation_year)

    def test_load_signage_bad_year(self):
        """Loading a signage with an invalid year should fail."""

        input_file_path = os.path.join(os.path.dirname(__file__), "data", "signage.shp")

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_file_path = os.path.join(tmp_dir, "signage_none_year.shp")
            update_gis(input_file_path, output_file_path, {"year": "not a number"})

            output = StringIO()
            StructureFactory.create(name="structure")

            with self.assertRaisesRegex(
                CommandError, 'Invalid year: "not a number" is not a number.'
            ):
                call_command(
                    "loadsignage",
                    output_file_path,
                    type_default="label",
                    name_default="name",
                    condition_default="conditions",
                    structure_default="structure",
                    description_default="description",
                    year_field="year",
                    stdout=output,
                )

    def test_load_signage_bad_multipoints_error(self):
        output = StringIO()
        StructureFactory.create(name="structure")
        filename = os.path.join(
            os.path.dirname(__file__), "data", "signage_bad_multipoint.geojson"
        )
        with self.assertRaisesRegex(
            CommandError,
            "One of your geometry is a MultiPoint object with multiple points",
        ):
            call_command(
                "loadsignage",
                filename,
                type_default="label",
                name_default="name",
                condition_default="conditions",
                structure_default="structure",
                description_default="description",
                year_default=2010,
                verbosity=2,
                stdout=output,
            )

    def test_load_signage_with_fields(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "signage.shp")
        call_command(
            "loadsignage",
            filename,
            type_field="label",
            name_field="name",
            structure_default="structure",
            eid_field="eid",
            condition_field="conditions",
            manager_field="manager",
            sealing_field="sealing",
            description_field="descriptio",
            year_field="year",
            code_field="name",
            verbosity=1,
            stdout=output,
        )
        self.assertIn(f"Signages will be linked to {structure}", output.getvalue())
        self.assertIn("SignageType 'type' created", output.getvalue())
        self.assertIn("Condition Type 'condition' created", output.getvalue())
        self.assertIn("Organism 'manager' created", output.getvalue())
        self.assertIn("Organism 'manager2' created", output.getvalue())
        self.assertIn("Sealing 'sealing' created", output.getvalue())
        self.assertIn("Sealing 'sealing2' created", output.getvalue())
        value = Signage.objects.all()
        names = [val.name for val in value]
        years = [val.implantation_year for val in value]
        codes = [val.code for val in value]
        self.assertIn("coucou", names)
        self.assertIn("name", codes)
        self.assertIn(2010, years)
        self.assertIn(2012, years)
        self.assertEqual(value.count(), 2)

    def test_no_file_fail(self):
        with self.assertRaisesRegex(CommandError, "File does not exists at: toto.shp"):
            call_command("loadsignage", "toto.shp")

    def test_missing_defaults(self):
        StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "signage.shp")
        output = StringIO()

        call_command("loadinfrastructure", filename, stdout=output)
        call_command(
            "loadinfrastructure", filename, type_default="label", stdout=output
        )

        elements_to_check = ["type", "name"]
        self.assertEqual(
            output.getvalue().count("Field 'None' not found in data source."), 2
        )
        for element in elements_to_check:
            self.assertIn(
                f"Set it with --{element}-field, or set a default value with --{element}-default",
                output.getvalue(),
            )

    def test_wrong_fields_fail(self):
        StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "signage.shp")
        output = StringIO()
        call_command(
            "loadsignage", filename, type_field="wrong_type_field", stdout=output
        )
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_field="wrong_name_field",
            stdout=output,
        )
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_field="name",
            condition_field="wrong_condition_field",
            stdout=output,
        )
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_field="name",
            manager_field="wrong_manager_field",
            stdout=output,
        )
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_field="name",
            sealing_field="wrong_sealing_field",
            stdout=output,
        )
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_field="name",
            description_field="wrong_description_field",
            stdout=output,
        )
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_field="name",
            year_field="wrong_implantation_year_field",
            stdout=output,
        )
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_field="name",
            code_field="wrong_code_field",
            stdout=output,
        )
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_field="name",
            structure_field="wrong_structure_field",
            stdout=output,
        )
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_field="name",
            eid_field="wrong_eid_field",
            stdout=output,
        )
        elements_to_check = [
            "wrong_type_field",
            "wrong_name_field",
            "wrong_condition_field",
            "wrong_code_field",
            "wrong_description_field",
            "wrong_implantation_year_field",
            "wrong_structure_field",
            "wrong_eid_field",
            "wrong_sealing_field",
            "wrong_manager_field",
        ]
        self.assertEqual(output.getvalue().count("set a default value"), 2)
        self.assertEqual(output.getvalue().count("Change your"), 8)
        for element in elements_to_check:
            self.assertIn(
                f"Field '{element}' not found in data source", output.getvalue()
            )

    def test_no_line_fail_rolling_back(self):
        self.path.delete()
        StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "line.geojson")
        output = StringIO()
        with self.assertRaises(GEOSException):
            call_command(
                "loadsignage",
                filename,
                type_default="label",
                name_default="name",
                stdout=output,
            )
        self.assertIn("An error occured, rolling back operations.", output.getvalue())
        self.assertEqual(Signage.objects.count(), 0)

    def test_update_same_eid(self):
        output = StringIO()
        filename = os.path.join(os.path.dirname(__file__), "data", "signage.shp")
        SignageFactory(name="name", eid="eid_2")
        call_command(
            "loadsignage",
            filename,
            eid_field="eid",
            type_default="label",
            name_default="name",
            verbosity=2,
            stdout=output,
        )
        self.assertIn("Update : name with eid eid1", output.getvalue())
        self.assertEqual(Signage.objects.count(), 3)

    def test_fail_structure_default_do_not_exist(self):
        output = StringIO()
        filename = os.path.join(os.path.dirname(__file__), "data", "signage.shp")
        call_command(
            "loadsignage",
            filename,
            type_default="label",
            name_default="name",
            condition_default="condition",
            structure_default="wrong_structure_default",
            description_default="description",
            year_default=2010,
            verbosity=0,
            stdout=output,
        )
        self.assertIn(
            "Structure wrong_structure_default set in options doesn't exist",
            output.getvalue(),
        )
