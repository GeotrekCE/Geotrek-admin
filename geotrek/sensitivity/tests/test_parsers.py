# -*- encoding: utf-8 -*-
import os
import mock
import requests

from django.core.management import call_command
from django.test import TestCase

from geotrek.common.tests import TranslationResetMixin
from geotrek.sensitivity.models import SportPractice, Species, SensitiveArea
from geotrek.sensitivity.factories import SpeciesFactory


class BiodivParserTests(TranslationResetMixin, TestCase):
    @mock.patch('geotrek.sensitivity.parsers.requests')
    def test_create(self, mocked):
        def side_effect(url):
            response = requests.Response()
            response.status_code = 200
            if 'sportpractice' in url:
                response.json = lambda: {
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "name": {
                                "fr": "Terrestre",
                                "en": "Land",
                                "it": None,
                            },
                        },
                    ],
                }
            else:
                response.json = lambda: {
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [{
                        "id": 1,
                        "url": "https://biodiv-sports.fr/api/v2/sensitivearea/46/?format=json",
                        "name": {"fr": "Tétras lyre", "en": "Black grouse", "it": "Fagiano di monte"},
                        "description": {"fr": "Blabla", "en": "Blahblah", "it": ""},
                        "period": [True, True, True, True, False, False, False, False, False, False, False, True],
                        "contact": "",
                        "practices": [1],
                        "info_url": "",
                        "published": True,
                        "structure": "LPO",
                        "species_id": 7,
                        "kml_url": "https://biodiv-sports.fr/api/fr/sensitiveareas/46.kml",
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
            return response
        mocked.get.side_effect = side_effect
        call_command('import', 'geotrek.sensitivity.parsers.BiodivParser', verbosity=0)
        practice = SportPractice.objects.get()
        species = Species.objects.get()
        area = SensitiveArea.objects.get()
        self.assertEqual(practice.name, "Land")
        self.assertEqual(species.name, "Black grouse")
        self.assertEqual(species.name_fr, "Tétras lyre")
        self.assertTrue(species.period01)
        self.assertFalse(species.period06)
        self.assertEqual(species.eid, '7')
        self.assertQuerysetEqual(species.practices.all(), ['<SportPractice: Land>'])
        self.assertEqual(area.species, species)
        self.assertEqual(area.description, "Blahblah")
        self.assertEqual(area.description_fr, "Blabla")
        self.assertEqual(area.eid, '1')


class SpeciesSensitiveAreaShapeParserTest(TestCase):
    def test_cli(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'species.shp')
        species = SpeciesFactory(name="Aigle royal")
        call_command('import', 'geotrek.sensitivity.parsers.SpeciesSensitiveAreaShapeParser', filename, verbosity=0)
        area = SensitiveArea.objects.get()
        self.assertEqual(area.species, species)
        self.assertEqual(area.contact, "Contact")
        self.assertEqual(area.description, "Test UTF8 éêè")
        self.assertEqual(
            area.geom.wkt,
            'POLYGON ((929315.3613368585 6483309.443505396, 929200.3539448171 6483204.020062691, '
            '928404.8861498644 6482494.807811771, 928194.0392644553 6482082.697990287, '
            '927925.6886830255 6481210.558600639, 927676.5060002692 6481287.230195334, '
            '927772.345493637 6481498.077080746, 927887.3528856782 6481900.602952889, '
            '928184.4553151187 6482600.231254471, 928625.3169846105 6483520.290390805, '
            '929162.0181474701 6483664.049630859, 929315.3613368585 6483309.443505396))')
