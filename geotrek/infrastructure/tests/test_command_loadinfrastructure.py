import os
from io import StringIO

from django.contrib.gis.geos.error import GEOSException
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from geotrek.authent.tests.factories import StructureFactory
from geotrek.core.tests.factories import PathFactory
from geotrek.infrastructure.models import Infrastructure
from geotrek.infrastructure.tests.factories import InfrastructureFactory


class InfrastructureCommandTest(TestCase):
    """
    There are 2 infrastructures in the file infrastructure.shp
    """

    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory.create()

    def test_load_infrastructure(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "infrastructure.shp")
        call_command(
            "loadinfrastructure",
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
        self.assertIn(
            "Infrastructures will be linked to %s" % structure, output.getvalue()
        )
        self.assertIn("2 objects created.", output.getvalue())
        value = Infrastructure.objects.filter(name="name").order_by("pk")
        self.assertEqual(2010, value[0].implantation_year)
        self.assertEqual(value.count(), 2)
        self.assertAlmostEqual(value[0].geom.x, -436345.704831, places=5)
        self.assertAlmostEqual(value[0].geom.y, 1176487.742917, places=5)
        self.assertAlmostEqual(value[1].geom.x, -436345.505347, places=5)
        self.assertAlmostEqual(value[1].geom.y, 1176480.918334, places=5)

    def test_load_infrastructure_multipoints(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(
            os.path.dirname(__file__), "data", "infrastructure_good_multipoint.geojson"
        )
        call_command(
            "loadinfrastructure",
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
        self.assertIn(
            "Infrastructures will be linked to %s" % structure, output.getvalue()
        )
        self.assertIn("1 objects created.", output.getvalue())
        value = Infrastructure.objects.first()
        self.assertEqual("name", value.name)
        self.assertEqual(2010, value.implantation_year)
        self.assertEqual(Infrastructure.objects.count(), 1)

    def test_load_infrastructure_bad_multipoints_error(self):
        output = StringIO()
        StructureFactory.create(name="structure")
        filename = os.path.join(
            os.path.dirname(__file__), "data", "infrastructure_bad_multipoint.geojson"
        )
        with self.assertRaisesRegex(
            CommandError,
            "One of your geometry is a MultiPoint object with multiple points",
        ):
            call_command(
                "loadinfrastructure",
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

    def test_load_infrastructure_with_fields_use_structure(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "infrastructure.shp")
        call_command(
            "loadinfrastructure",
            filename,
            type_field="label",
            name_field="name",
            condition_field="conditions",
            structure_default="structure",
            use_structure=True,
            description_field="descriptio",
            year_field="year",
            verbosity=1,
            stdout=output,
        )
        self.assertIn(
            "Infrastructures will be linked to %s" % structure, output.getvalue()
        )
        self.assertIn(
            "InfrastructureType 'type (%s)' created" % structure, output.getvalue()
        )
        self.assertIn(
            "Condition Type 'condition (%s)' created" % structure, output.getvalue()
        )
        value = Infrastructure.objects.all()
        names = [val.name for val in value]
        years = [val.implantation_year for val in value]
        self.assertIn("coucou", names)
        self.assertIn(2010, years)
        self.assertIn(2012, years)
        self.assertEqual(value.count(), 2)

    def test_load_infrastructure_with_fields(self):
        output = StringIO()
        structure = StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "infrastructure.shp")
        call_command(
            "loadinfrastructure",
            filename,
            type_field="label",
            name_field="name",
            condition_field="conditions",
            structure_default="structure",
            description_field="descriptio",
            year_field="year",
            verbosity=1,
            stdout=output,
        )
        self.assertIn(
            "Infrastructures will be linked to %s" % structure, output.getvalue()
        )
        self.assertIn("InfrastructureType 'type' created", output.getvalue())
        self.assertIn("Condition Type 'condition' created", output.getvalue())
        value = Infrastructure.objects.all()
        names = [val.name for val in value]
        years = [val.implantation_year for val in value]
        self.assertIn("coucou", names)
        self.assertIn(2010, years)
        self.assertIn(2012, years)
        self.assertEqual(value.count(), 2)

    def test_no_file_fail(self):
        with self.assertRaisesRegex(CommandError, "File does not exists at: toto.shp"):
            call_command("loadinfrastructure", "toto.shp")

    def test_missing_defaults(self):
        StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "infrastructure.shp")
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
        filename = os.path.join(os.path.dirname(__file__), "data", "infrastructure.shp")
        output = StringIO()
        call_command(
            "loadinfrastructure", filename, type_field="wrong_type_field", stdout=output
        )
        call_command(
            "loadinfrastructure",
            filename,
            type_default="label",
            name_field="wrong_name_field",
            stdout=output,
        )
        call_command(
            "loadinfrastructure",
            filename,
            type_default="label",
            name_field="name",
            condition_field="wrong_condition_field",
            stdout=output,
        )
        call_command(
            "loadinfrastructure",
            filename,
            type_default="label",
            name_field="name",
            description_field="wrong_description_field",
            stdout=output,
        )
        call_command(
            "loadinfrastructure",
            filename,
            type_default="label",
            name_field="name",
            year_field="wrong_implantation_year_field",
            stdout=output,
        )
        call_command(
            "loadinfrastructure",
            filename,
            type_default="label",
            name_field="name",
            structure_field="wrong_structure_field",
            stdout=output,
        )
        call_command(
            "loadinfrastructure",
            filename,
            type_default="label",
            name_field="name",
            eid_field="wrong_eid_field",
            stdout=output,
        )
        call_command(
            "loadinfrastructure",
            filename,
            type_default="label",
            name_field="name",
            category_field="wrong_category_field",
            stdout=output,
        )
        elements_to_check = [
            "wrong_type_field",
            "wrong_name_field",
            "wrong_condition_field",
            "wrong_description_field",
            "wrong_implantation_year_field",
            "wrong_structure_field",
            "wrong_eid_field",
            "wrong_category_field",
        ]
        self.assertEqual(output.getvalue().count("set a default value"), 2)
        self.assertEqual(output.getvalue().count("Change your"), 6)
        for element in elements_to_check:
            self.assertIn(
                f"Field '{element}' not found in data source", output.getvalue()
            )

    def test_line_fail_rolling_back(self):
        self.path.delete()
        StructureFactory.create(name="structure")
        filename = os.path.join(os.path.dirname(__file__), "data", "line.geojson")
        output = StringIO()
        with self.assertRaises(GEOSException):
            call_command(
                "loadinfrastructure",
                filename,
                type_default="label",
                name_default="name",
                stdout=output,
            )
        self.assertIn("An error occured, rolling back operations.", output.getvalue())
        self.assertEqual(Infrastructure.objects.count(), 0)

    def test_update_same_eid(self):
        output = StringIO()
        filename = os.path.join(os.path.dirname(__file__), "data", "infrastructure.shp")
        InfrastructureFactory(name="name", eid="eid_2")
        call_command(
            "loadinfrastructure",
            filename,
            eid_field="eid",
            type_default="label",
            condition_field="conditions",
            name_default="name",
            verbosity=2,
            stdout=output,
        )
        self.assertIn("Update : name with eid eid1", output.getvalue())
        self.assertEqual(Infrastructure.objects.count(), 2)

    def test_fail_structure_default_do_not_exist(self):
        output = StringIO()
        filename = os.path.join(os.path.dirname(__file__), "data", "infrastructure.shp")
        call_command(
            "loadinfrastructure",
            filename,
            type_default="label",
            name_default="name",
            condition_default="conditions",
            structure_default="wrong_structure_default",
            description_default="description",
            year_default=2010,
            category_default="E",
            verbosity=0,
            stdout=output,
        )
        self.assertIn(
            "Structure wrong_structure_default set in options doesn't exist",
            output.getvalue(),
        )
