from unittest import mock
import json
import os

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.common.models import FileType
from geotrek.signage.models import Signage
from geotrek.signage.parsers import GeotrekSignageParser


class TestGeotrekSignageParser(GeotrekSignageParser):
    url = "https://test.fr"

    field_options = {
        'sealing': {'create': True, },
        'condition': {'create': True, },
        'type': {'create': True},
        'geom': {'required': True}
    }


class SignageGeotrekParserTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = ['signage_sealing.json', 'signage_condition.json', 'signage_type.json', 'signage.json', ]

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

        call_command('import', 'geotrek.signage.tests.test_parsers.TestGeotrekSignageParser', verbosity=0)
        self.assertEqual(Signage.objects.count(), 2)
        signage = Signage.objects.all().first()
        self.assertEqual(str(signage.name), 'test gard')
        self.assertEqual(str(signage.type), 'Limite Cœur')
        self.assertEqual(str(signage.sealing), 'Socle béton')
        self.assertEqual(str(signage.geom.ewkt), 'SRID=2154;POINT (572941.1308660918 6189000.155980503)')
