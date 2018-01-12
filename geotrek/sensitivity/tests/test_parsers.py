# -*- encoding: utf-8 -*-

import mock

from django.core.management import call_command
from django.test import TestCase

from geotrek.sensitivity.models import SportPractice, Species, SensitiveArea


class BiodivParserTests(TestCase):
    @mock.patch('geotrek.sensitivity.parsers.requests.get')
    def test_create(self, mocked):
        def json():
            return {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [{
                    "id": 1,
                    "url": "http://biodiv-sports.fr/api/v2/sensitivearea/46/?format=json",
                    "name": {"fr": "Tétras lyre", "en": "Black grouse", "it": "Fagiano di monte"},
                    "description": {"fr": "Blabla", "en": "Blahblah", "it": ""},
                    "period": [True, True, True, True, False, False, False, False, False, False, False, True],
                    "contact": "",
                    "practices": ["Terrestre"],
                    "info_url": "",
                    "published": True,
                    "structure": "LPO",
                    "species_id": 7,
                    "kml_url": "http://biodiv-sports.fr/api/fr/sensitiveareas/46.kml",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[6.098245801813527, 45.26257781325591],
                                         [6.098266512921538, 45.26330956917618],
                                         [6.098455143566011, 45.26390601480551],
                                         [6.098245801813527, 45.26257781325591]]]
                    },
                    "update_datetime": "2017-11-29T14:53:35.949097Z",
                    "create_datetime": "2017-11-29T14:49:01.317155Z",
                    "radius": None
                }]
            }
        mocked.return_value.status_code = 200
        mocked.return_value.json = json
        call_command('import', 'geotrek.sensitivity.parsers.BiodivParser', verbosity=0)
        practice = SportPractice.objects.get()
        species = Species.objects.get()
        area = SensitiveArea.objects.get()
        self.assertEqual(practice.name, "Terrestre")
        self.assertEqual(species.name, u"Black grouse")
        self.assertEqual(species.name_fr, u"Tétras lyre")
        self.assertTrue(species.period01)
        self.assertFalse(species.period06)
        self.assertEqual(species.eid, '7')
        self.assertQuerysetEqual(species.practices.all(), ['<SportPractice: Terrestre>'])
        self.assertEqual(area.species, species)
        self.assertEqual(area.description, "Blahblah")
        self.assertEqual(area.description_fr, "Blabla")
        self.assertEqual(area.eid, '1')
