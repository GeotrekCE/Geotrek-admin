import os
from io import StringIO
from unittest import skipIf

from django.contrib.gis.geos import GEOSGeometry
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
    fields = {"geom": "geometry"}

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

    def test_parsing_fails_when_geom_is_not_a_point(self):
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

    # def test_parsing_succeeds_when_geom_is_a_point_several_objects(self):
    #     if settings.TREKKING_TOPOLOGY_ENABLED:
    #         PathFactory.create()
    #     filename = self.get_test_data_file_path("point_topology_test_model_objects.json")
    #     # TODO
