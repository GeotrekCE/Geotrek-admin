from unittest import mock

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.common.models import FileType
from geotrek.common.tests.mixins import GeotrekParserTestMixin
from geotrek.infrastructure.models import Infrastructure
from geotrek.infrastructure.parsers import GeotrekInfrastructureParser


class TestGeotrekInfrastructureParser(GeotrekInfrastructureParser):
    url = "https://test.fr"

    field_options = {
        'condition': {'create': True, },
        'structure': {'create': True, },
        'type': {'create': True},
        'geom': {'required': True},
    }


class InfrastructureGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = 'infrastructure'

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr", LANGUAGE_COE="fr")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [('infrastructure', 'structure.json'),
                                ('infrastructure', 'infrastructure_condition.json'),
                                ('infrastructure', 'infrastructure_type.json'),
                                ('infrastructure', 'infrastructure_ids.json'),
                                ('infrastructure', 'infrastructure.json')]

        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.infrastructure.tests.test_parsers.TestGeotrekInfrastructureParser', verbosity=0)
        self.assertEqual(Infrastructure.objects.count(), 2)
        infrastructure = Infrastructure.objects.all().first()
        self.assertEqual(str(infrastructure.name), 'Table pic-nique')
        self.assertEqual(str(infrastructure.type), 'Table')
        self.assertEqual(str(infrastructure.structure), 'Struct1')
        self.assertAlmostEqual(infrastructure.geom.x, 565008.6693905985, places=5)
        self.assertAlmostEqual(infrastructure.geom.y, 6188246.533542466, places=5)
