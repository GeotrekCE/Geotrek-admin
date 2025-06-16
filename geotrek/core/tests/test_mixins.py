import os
from io import StringIO
from unittest import skipIf

from django.contrib.gis.geos import GEOSGeometry, LineString
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from geotrek import settings
from geotrek.common.tests.test_parsers import JSONParser
from geotrek.core.mixins.parsers import PointTopologyParserMixin
from geotrek.core.tests.factories import PathFactory
from geotrek.core.tests.models import PointTopologyTestModel


class PointTopologyTestModelParser(PointTopologyParserMixin, JSONParser):
    model = PointTopologyTestModel
    fields = {"name": "name", "geom": "geometry"}

    def build_geos_geometry(self, src, val):
        return GEOSGeometry(str(val))


class PointTopologyTestModelParserMissingMethod(PointTopologyParserMixin, JSONParser):
    model = PointTopologyTestModel
    fields = {"geom": "geometry"}


class PointTopologyParserMixinTest(TestCase):
    def get_test_data_file_path(self, filename):
        return os.path.join(os.path.dirname(__file__), "data", filename)

    def test_instantiation_fails_without_build_geos_geometry_definition(self):
        with self.assertRaises(TypeError):
            PointTopologyTestModelParserMissingMethod()

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_parsing_fails_without_path_in_dynamic_segmentation_mode(self):
        filename = self.get_test_data_file_path(
            "point_topology_test_model_objects.json"
        )
        with self.assertRaisesMessage(
            CommandError,
            "You need to add a network of paths before importing 'PointTopologyTestModel' objects",
        ):
            call_command(
                "import",
                "geotrek.core.tests.test_mixins.PointTopologyTestModelParser",
                filename,
                verbosity=0,
            )

    def test_object_parsing_fails_when_geom_is_incorrect(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            PathFactory.create()
        output = StringIO()
        filename = self.get_test_data_file_path(
            "point_topology_test_model_wrong_geom.json"
        )
        call_command(
            "import",
            "geotrek.core.tests.test_mixins.PointTopologyTestModelParser",
            filename,
            verbosity=2,
            stdout=output,
        )
        self.assertIn(
            "Invalid geometry type: should be 'Point', not 'LineString'",
            output.getvalue(),
        )
        self.assertIn("Cannot import object: geometry is None", output.getvalue())
        self.assertIn(
            "Could not parse geometry from value '{'type': 'Point'}'",
            output.getvalue(),
        )
        self.assertEqual(len(PointTopologyTestModel.objects.all()), 0)

    def test_object_parsing_succeeds_when_geom_is_a_point_several_objects(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create(
                geom=LineString((2.0, 45.0), (5.0, 47.0), srid=4326)
            )
        filename = self.get_test_data_file_path(
            "point_topology_test_model_objects.json"
        )
        call_command(
            "import",
            "geotrek.core.tests.test_mixins.PointTopologyTestModelParser",
            filename,
            verbosity=0,
        )
        test_objects = PointTopologyTestModel.objects.all()
        self.assertEqual(len(test_objects), 2)
        obj_1 = test_objects.get(name="test1")
        obj_2 = test_objects.get(name="test2")

        if settings.TREKKING_TOPOLOGY_ENABLED:
            obj_1_path = obj_1.topo_object.paths.get()
            self.assertEqual(obj_1_path, path)
            self.assertEqual(obj_1.topo_object.kind, "POINTTOPOLOGYTESTMODEL")
            self.assertAlmostEqual(obj_1.topo_object.offset, -55184.442, places=2)
        self.assertEqual(obj_1.geom.geom_type, "Point")
        self.assertEqual(obj_1.geom.srid, settings.SRID)
        self.assertAlmostEqual(obj_1.geom.x, 700000.000, places=2)
        self.assertAlmostEqual(obj_1.geom.y, 6433418.985, places=2)

        if settings.TREKKING_TOPOLOGY_ENABLED:
            obj_2_path = obj_2.topo_object.paths.get()
            self.assertEqual(obj_2_path, path)
            self.assertEqual(obj_2.topo_object.kind, "POINTTOPOLOGYTESTMODEL")
            self.assertAlmostEqual(obj_2.topo_object.offset, -28914.952, places=2)
        self.assertEqual(obj_2.geom.geom_type, "Point")
        self.assertEqual(obj_2.geom.srid, settings.SRID)
        self.assertAlmostEqual(obj_2.geom.x, 777390.880, places=2)
        self.assertAlmostEqual(obj_2.geom.y, 6544963.910, places=2)
