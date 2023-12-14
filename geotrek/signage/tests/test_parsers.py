from unittest import mock

from django.core.management import call_command
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.common.models import FileType
from geotrek.common.tests.mixins import GeotrekParserTestMixin
from geotrek.signage.models import Signage
from geotrek.signage.parsers import GeotrekSignageParser


class TestGeotrekSignageParser(GeotrekSignageParser):
    url = "https://test.fr"

    field_options = {
        'sealing': {'create': True, },
        'conditions': {'create': True, },
        'type': {'create': True},
        'geom': {'required': True}
    }


class SignageGeotrekParserTests(GeotrekParserTestMixin, TestCase):
    app_label = "signage"

    @classmethod
    def setUpTestData(cls):
        cls.filetype = FileType.objects.create(type="Photographie")

    @mock.patch('requests.get')
    @mock.patch('requests.head')
    @override_settings(MODELTRANSLATION_DEFAULT_LANGUAGE="fr")
    def test_create(self, mocked_head, mocked_get):
        self.mock_time = 0
        self.mock_json_order = [('signage', 'signage_sealing.json'),
                                ('signage', 'signage_conditions.json'),
                                ('signage', 'signage_type.json'),
                                ('signage', 'signage_ids.json'),
                                ('signage', 'signage.json')]
        # Mock GET
        mocked_get.return_value.status_code = 200
        mocked_get.return_value.json = self.mock_json
        mocked_get.return_value.content = b''
        mocked_head.return_value.status_code = 200

        call_command('import', 'geotrek.signage.tests.test_parsers.TestGeotrekSignageParser', verbosity=0)
        self.assertEqual(Signage.objects.count(), 2)
        signage = Signage.objects.all().first()
        self.assertEqual(str(signage.name), 'test gard')
        self.assertEqual(str(signage.type), 'Limite Cœur')
        self.assertEqual(str(signage.sealing), 'Socle béton')
        conditions = [str(c.label) for c in signage.conditions.all()]
        self.assertEqual(conditions, ["Dégradé"])
        self.assertAlmostEqual(signage.geom.x, 572941.1308660918, places=5)
        self.assertAlmostEqual(signage.geom.y, 6189000.155980503, places=5)
