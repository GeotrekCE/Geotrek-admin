# -*- encoding: utf-8 -*-

import os
import mock
import requests

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from geotrek.common.parsers import RowImportError
from geotrek.common.tests import TranslationResetMixin
from geotrek.sensitivity.models import SportPractice, Species, SensitiveArea
from geotrek.sensitivity.factories import SpeciesFactory


json_test_sport_practice = {
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

json_test_species = {
                    "count": 2,
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
                    }, {
                        "id": 2,
                        "url": "https://biodiv-sports.fr/api/v2/sensitivearea/46/?format=json",
                        "name": {"fr": "Tétras lyre", "en": "Black grouse", "it": "Fagiano di monte"},
                        "description": {"fr": "Blabla2", "en": "Blahblah2", "it": ""},
                        "period": [True, True, True, True, False, False, False, False, False, False, False, True],
                        "contact": "",
                        "practices": [1],
                        "info_url": "",
                        "published": True,
                        "structure": "LPO",
                        "species_id": 7,
                        "kml_url": "https://biodiv-sports.fr/api/fr/sensitiveareas/47.kml",
                        "geometry": {
                            "type": "MultiPolygon",
                            "coordinates": [[[[6.098245801813527, 45.26257781325591],
                                             [6.098266512921538, 45.26330956917618],
                                             [6.098455143566011, 45.26390601480551],
                                             [6.098245801813527, 45.26257781325591]]]]
                        },
                        "update_datetime": "2017-11-29T14:53:35.949097Z",
                        "create_datetime": "2017-11-29T14:49:01.317155Z",
                        "radius": None
                    }
                    ]
                }


class BiodivParserTests(TranslationResetMixin, TestCase):
    @mock.patch('geotrek.sensitivity.parsers.requests')
    def test_create(self, mocked):
        def side_effect(url):
            response = requests.Response()
            response.status_code = 200
            if 'sportpractice' in url:
                response.json = lambda: json_test_sport_practice
            else:
                response.json = lambda: json_test_species
            return response
        mocked.get.side_effect = side_effect
        call_command('import', 'geotrek.sensitivity.parsers.BiodivParser', verbosity=0)
        practice = SportPractice.objects.get()
        species = Species.objects.first()
        area_1 = SensitiveArea.objects.first()
        self.assertEqual(practice.name, "Land")
        self.assertEqual(practice.name_fr, "Terrestre")
        self.assertEqual(species.name, u"Black grouse")
        self.assertEqual(species.name_fr, u"Tétras lyre")
        self.assertTrue(species.period01)
        self.assertFalse(species.period06)
        self.assertEqual(species.eid, '7')
        self.assertQuerysetEqual(species.practices.all(), ['<SportPractice: Land>'])
        self.assertEqual(area_1.species, species)
        self.assertEqual(area_1.description, "Blahblah")
        self.assertEqual(area_1.description_fr, "Blabla")
        self.assertEqual(area_1.eid, '1')
        area_2 = SensitiveArea.objects.last()
        self.assertQuerysetEqual(species.practices.all(), ['<SportPractice: Land>'])
        self.assertEqual(area_2.species, species)
        self.assertEqual(area_2.description, "Blahblah2")
        self.assertEqual(area_2.description_fr, "Blabla2")
        self.assertEqual(area_2.eid, '2')
        self.assertEqual(area_2.geom.geom_type, 'MultiPolygon')

    @mock.patch('geotrek.sensitivity.parsers.requests')
    def test_status_code_404(self, mocked):
        def side_effect(url):
            response = requests.Response()
            response.status_code = 404
            return response
        mocked.get.side_effect = side_effect
        with self.assertRaises(CommandError) as e:
            call_command('import', 'geotrek.sensitivity.parsers.BiodivParser', verbosity=0)
        self.assertIn("Failed to download https://biodiv-sports.fr/api/v2/sportpractice/", str(e.exception.message))

    @mock.patch('geotrek.sensitivity.parsers.requests')
    def test_create_no_id(self, mocked):
        def side_effect(url):
            response = requests.Response()
            response.status_code = 200
            if 'sportpractice' in url:
                response.json = lambda: json_test_sport_practice
            else:
                json_test_species_without_id = json_test_species.copy()
                json_test_species_without_id['results'][0]['species_id'] = None
                response.json = lambda: json_test_species_without_id
            return response
        mocked.get.side_effect = side_effect
        call_command('import', 'geotrek.sensitivity.parsers.BiodivParser', verbosity=0)
        practice = SportPractice.objects.get()
        species = Species.objects.get()
        area = SensitiveArea.objects.get()
        self.assertEqual(practice.name, "Land")
        self.assertEqual(practice.name_fr, "Terrestre")
        self.assertEqual(species.name, u"Black grouse")
        self.assertEqual(species.name_fr, u"Tétras lyre")
        self.assertEqual(species.eid, None)
        self.assertQuerysetEqual(species.practices.all(), ['<SportPractice: Land>'])
        self.assertEqual(area.eid, '1')

    @mock.patch('geotrek.sensitivity.parsers.requests')
    def test_create_species_url(self, mocked):
        def side_effect(url):
            response = requests.Response()
            response.status_code = 200
            if 'sportpractice' in url:
                response.json = lambda: json_test_sport_practice
            else:
                json_test_species_without_id = json_test_species.copy()
                json_test_species_without_id['results'][0]['info_url'] = "toto.com"
                response.json = lambda: json_test_species_without_id
            return response
        mocked.get.side_effect = side_effect
        call_command('import', 'geotrek.sensitivity.parsers.BiodivParser', verbosity=0)
        species = Species.objects.get()
        self.assertEqual(species.url, "toto.com")

    @mock.patch('geotrek.sensitivity.parsers.requests')
    def test_create_species_radius(self, mocked):
        def side_effect(url):
            response = requests.Response()
            response.status_code = 200
            if 'sportpractice' in url:
                response.json = lambda: json_test_sport_practice
            else:
                json_test_species_without_id = json_test_species.copy()
                json_test_species_without_id['results'][0]['radius'] = 5
                response.json = lambda: json_test_species_without_id
            return response
        mocked.get.side_effect = side_effect
        call_command('import', 'geotrek.sensitivity.parsers.BiodivParser', verbosity=0)
        species = Species.objects.get()
        self.assertEqual(species.radius, 5)


class SpeciesSensitiveAreaShapeParserTest(TestCase):
    def test_cli(self):
        filename = os.path.join(os.path.dirname(__file__), 'data', 'species.shp')
        with self.assertRaises(RowImportError) as rie:
            call_command('import', 'geotrek.sensitivity.parsers.SpeciesSensitiveAreaShapeParser', filename, verbosity=0)
        self.assertEqual(rie.exception.message, "L'espèce Aigle royal n'existe pas dans Geotrek. Merci de l'ajouter.")
        species = SpeciesFactory(name=u"Aigle royal")
        call_command('import', 'geotrek.sensitivity.parsers.SpeciesSensitiveAreaShapeParser', filename, verbosity=0)
        area = SensitiveArea.objects.get()
        self.assertEqual(area.species, species)
        self.assertEqual(area.contact, u"Contact")
        self.assertEqual(area.description, u"Test UTF8 éêè")
        self.assertEqual(
            area.geom.wkt,
            'POLYGON ((929315.3613368585 6483309.443505395, 929200.3539448172 6483204.020062691, '
            '928404.8861498644 6482494.80781177, 928194.0392644553 6482082.697990288, '
            '927925.6886830255 6481210.558600641, 927676.5060002692 6481287.230195334, '
            '927772.345493637 6481498.077080746, 927887.3528856783 6481900.60295289, '
            '928184.4553151187 6482600.231254471, 928625.3169846105 6483520.290390803, '
            '929162.0181474701 6483664.049630859, 929315.3613368585 6483309.443505395))')
