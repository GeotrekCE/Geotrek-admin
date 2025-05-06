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
from geotrek.signage.models import Signage, SignageType
from geotrek.signage.parsers import GeotrekSignageParser, OpenStreetMapSignageParser


class TestGeotrekSignageParser(GeotrekSignageParser):
    url = "https://test.fr"

    field_options = {
        "sealing": {
            "create": True,
        },
        "conditions": {
            "create": True,
        },
        "type": {"create": True},
        "geom": {"required": True},
        "structure": {"create": True},
    }


class SignageGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = "signage"

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch("requests.get")
    @mock.patch("requests.head")
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_CODE="fr")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [
            ("signage", "structure.json"),
            ("signage", "signage_sealing.json"),
            ("signage", "signage_conditions.json"),
            ("signage", "signage_type.json"),
            ("signage", "signage_ids.json"),
            ("signage", "signage.json"),
        ]
        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b""
        mocked_head.return_value.status_code = 200

        call_command(
            "import",
            "geotrek.signage.tests.test_parsers.TestGeotrekSignageParser",
            verbosity=0,
        )
        self.assertEqual(Signage.objects.count(), 2)
        signage = Signage.objects.all().first()
        self.assertEqual(str(signage.name), "test gard")
        self.assertEqual(str(signage.type), "Limite Cœur")
        self.assertEqual(str(signage.structure), "Struct1")
        self.assertEqual(str(signage.sealing), "Socle béton")
        conditions = [str(c.label) for c in signage.conditions.all()]
        self.assertEqual(conditions, ["Dégradé"])
        self.assertAlmostEqual(signage.geom.x, 572941.1308660918, places=5)
        self.assertAlmostEqual(signage.geom.y, 6189000.155980503, places=5)


class TestSignageOpenStreetMapParser(OpenStreetMapSignageParser):
    provider = "OpenStreetMap"
    tags = [{"information": "board"}]
    default_fields_values = {"name": "Test"}
    type = "Test"


class OpenStreetMapSignageParserTests(TestCase):
    @classmethod
    @mock.patch("geotrek.common.parsers.requests.get")
    def import_signage(cls, mocked):
        def mocked_json():
            filename = os.path.join(
                os.path.dirname(__file__), "data", "signage_OSM.json"
            )
            with open(filename) as f:
                return json.load(f)

        mocked.return_value.status_code = 200
        mocked.return_value.json = mocked_json

        call_command(
            "import",
            "geotrek.signage.tests.test_parsers.TestSignageOpenStreetMapParser",
        )

    @classmethod
    def setUpTestData(cls):
        cls.type = SignageType.objects.create(label="Test")
        cls.path = PathFactory.create(
            geom=LineString((6.3737905, 44.8337000), (6.3757905, 44.8357000), srid=4326)
        )
        cls.import_Signage()
        cls.objects = Signage.objects.all()

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_import_cmd_raises_error_when_no_path(self):
        self.path.delete()
        with self.assertRaisesRegex(
            CommandError, "You need to add a network of paths before importing Signages"
        ):
            call_command(
                "import",
                "geotrek.signage.tests.test_parsers.TestSignageOpenStreetMapParser",
                verbosity=0,
            )

    def test_create_Signage_OSM(self):
        self.assertEqual(self.objects.count(), 1)

    def test_Signage_eid_filter_OSM(self):
        signage_eid = self.objects.order_by("eid").all().values_list("eid", flat=True)
        self.assertListEqual(list(signage_eid), ["N7872800265"])
        self.assertNotEqual(signage_eid, ["7872800265"])

    @skipIf(
        not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only"
    )
    def test_topology_point(self):
        signage = self.objects.get(eid="N7872800265")
        self.assertAlmostEqual(signage.topo_object.offset, 0.0)
        self.assertEqual(signage.topo_object.paths.count(), 1)
        signage_path = signage.topo_object.paths.get()
        self.assertEqual(signage_path, self.path)
        self.assertEqual(signage.topo_object.kind, "SIGNAGE")

    def test_topology_point_no_dynamic_segmentation(self):
        signage = self.objects.get(eid="N7872800265")
        self.assertAlmostEqual(signage.geom.x, 966634.858, places=2)
        self.assertAlmostEqual(signage.geom.y, 6420758.255, places=2)
