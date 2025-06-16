import json
import os
from unittest import mock, skipIf

from django.conf import settings
from django.contrib.gis.geos import LineString
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.common.models import FileType
from geotrek.common.tests.mixins import GeotrekParserTestMixin
from geotrek.core.tests.factories import PathFactory
from geotrek.infrastructure.models import Infrastructure, InfrastructureType
from geotrek.infrastructure.parsers import (
    GeotrekInfrastructureParser,
    OpenStreetMapInfrastructureParser,
)


class TestGeotrekInfrastructureParser(GeotrekInfrastructureParser):
    url = "https://test.fr"

    field_options = {
        "condition": {
            "create": True,
        },
        "structure": {
            "create": True,
        },
        "type": {"create": True},
        "geom": {"required": True},
    }


class InfrastructureGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = "infrastructure"

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("infrastructure", "structure.json"),
            ("infrastructure", "infrastructure_condition.json"),
            ("infrastructure", "infrastructure_type.json"),
            ("infrastructure", "infrastructure_ids.json"),
            ("infrastructure", "infrastructure.json"),
        ]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.infrastructure.tests.test_parsers.TestGeotrekInfrastructureParser",
            verbosity=0,
        )
        self.assertEqual(Infrastructure.objects.count(), 2)
        infrastructure = Infrastructure.objects.all().first()
        self.assertEqual(str(infrastructure.name), "Table pic-nique")
        self.assertEqual(str(infrastructure.type), "Table")
        self.assertEqual(str(infrastructure.structure), "Struct1")
        self.assertAlmostEqual(infrastructure.geom.x, 565008.6693905985, places=5)
        self.assertAlmostEqual(infrastructure.geom.y, 6188246.533542466, places=5)


class TestInfrastructureOpenStreetMapParser(OpenStreetMapInfrastructureParser):
    provider = "OpenStreetMap"
    tags = [
        {"amenity": "shelter"},
        {"amenity": "bicycle_parking"},
        {"bridge": "yes"},
    ]
    default_fields_values = {"name": "Test"}
    type = "Test"


class OpenStreetMapInfrastructureParser(TestCase):
    @classmethod
    @mock.patch("geotrek.common.parsers.requests.get")
    def import_Infrastructure(cls, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "Infrastructure_OSM.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json

        call_command(
            "import",
            "geotrek.infrastructure.tests.test_parsers.TestInfrastructureOpenStreetMapParser",
        )

    @classmethod
    def setUpTestData(cls):
        cls.type = InfrastructureType.objects.create(label="Test")
        cls.path = PathFactory.create(
            geom=LineString((5.8394587, 44.6918860), (5.9527022, 44.7752786), srid=4326)
        )
        cls.import_Infrastructure()
        cls.objects = Infrastructure.objects.all()

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_import_cmd_raises_error_when_no_path(self):
        self.path.delete()
        with self.assertRaisesRegex(
            CommandError,
            "You need to add a network of paths before importing Infrastructures",
        ):
            call_command(
                "import",
                "geotrek.infrastructure.tests.test_parsers.TestInfrastructureOpenStreetMapParser",
                verbosity=0,
            )

    def test_create_Infrastructure_OSM(self):
        self.assertEqual(self.objects.count(), 4)

    def test_Infrastructure_eid_filter_OSM(self):
        infrastructure_eid = self.objects.all().values_list("eid", flat=True)
        self.assertListEqual(list(infrastructure_eid), ["N1", "W2", "W3", "R4"])
        self.assertNotEqual(infrastructure_eid, ["1", "2", "3", "4"])

    def test_default_name(self):
        poi1 = self.objects.get(eid="N1")
        self.assertEqual(poi1.name, "Abri de la Muande Bellone")

        poi3 = self.objects.get(eid="W2")
        self.assertEqual(poi3.name, "Test")

    def test_type(self):
        poi = self.objects.get(eid="N1")
        self.assertEqual(poi.type.label, "Test")

    def test_topology_point(self):
        infrastructure = self.objects.get(eid="N1")

        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.assertAlmostEqual(
                infrastructure.topo_object.offset, 27225.536, places=2
            )
            self.assertEqual(infrastructure.topo_object.paths.count(), 1)
            infrastructure_path = infrastructure.topo_object.paths.get()
            self.assertEqual(infrastructure_path, self.path)
            self.assertEqual(infrastructure.topo_object.kind, "INFRASTRUCTURE")

        self.assertAlmostEqual(infrastructure.geom.x, 958978.005, places=2)
        self.assertAlmostEqual(infrastructure.geom.y, 6422555.230, places=2)

    def test_topology_way(self):
        infrastructure = self.objects.get(eid="W2")

        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.assertAlmostEqual(
                infrastructure.topo_object.offset, -31942.149, places=2
            )
            infrastructure_path = infrastructure.topo_object.paths.get()
            self.assertEqual(infrastructure_path, self.path)
            self.assertEqual(infrastructure.topo_object.kind, "INFRASTRUCTURE")

        self.assertAlmostEqual(infrastructure.geom.x, 962840.506, places=2)
        self.assertAlmostEqual(infrastructure.geom.y, 6425568.935, places=2)

    def test_topology_polygon(self):
        infrastructure = self.objects.get(eid="W3")

        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.assertAlmostEqual(
                infrastructure.topo_object.offset, 48632.872, places=2
            )
            infrastructure_path = infrastructure.topo_object.paths.get()
            self.assertEqual(infrastructure_path, self.path)
            self.assertEqual(infrastructure.topo_object.kind, "INFRASTRUCTURE")

        self.assertAlmostEqual(infrastructure.geom.x, 917407.272, places=2)
        self.assertAlmostEqual(infrastructure.geom.y, 6458702.232, places=2)

    def test_topology_relation(self):
        infrastructure = self.objects.get(eid="R4")

        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.assertAlmostEqual(
                infrastructure.topo_object.offset, -31942.149, places=2
            )
            infrastructure_path = infrastructure.topo_object.paths.get()
            self.assertEqual(infrastructure_path, self.path)
            self.assertEqual(infrastructure.topo_object.kind, "INFRASTRUCTURE")

        self.assertAlmostEqual(infrastructure.geom.x, 962840.506, places=2)
        self.assertAlmostEqual(infrastructure.geom.y, 6425568.935, places=2)
