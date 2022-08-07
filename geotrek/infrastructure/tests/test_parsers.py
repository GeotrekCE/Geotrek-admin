from unittest import mock
import json
import os

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.common.models import FileType
from geotrek.infrastructure.models import Infrastructure
from geotrek.infrastructure.parsers import GeotrekInfrastructureParser


class TestGeotrekInfrastructureParser(GeotrekInfrastructureParser):
    url = "https://test.fr"

    field_options = {
        'condition': {'create': True, },
        'type': {'create': True},
        'geom': {'required': True},
    }


class InfrastructureGeotrekParserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['infrastructure_condition.json', 'infrastructure_type.json', 'infrastructure_ids.json',
                                'infrastructure.json', ]

        def mocked_json():
            filename = os.path.join(os.path.dirname(__file__), 'data', 'geotrek_parser_v2',
                                    self.mock_json_order[self.mock_time])
            self.mock_time += 1
            with open(filename, 'r') as f:
                return json.load(f)

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = mocked_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.infrastructure.tests.test_parsers.TestGeotrekInfrastructureParser', verbosity=0)
        self.assertEqual(Infrastructure.objects.count(), 2)
        infrastructure = Infrastructure.objects.all().first()
        self.assertEqual(str(infrastructure.name), 'Table pic-nique')
        self.assertEqual(str(infrastructure.type), 'Table')
        self.assertAlmostEqual(infrastructure.geom.x, 565008.6693905985, places=5)
        self.assertAlmostEqual(infrastructure.geom.y, 6188246.533542466, places=5)
