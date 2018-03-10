# -*- encoding: utf-8 -*-

import os
import mock
import requests

from django.contrib.auth.models import Permission
from django.core.management import call_command
from django.test import TestCase

from geotrek.authent.factories import UserProfileFactory, StructureFactory, UserFactory
from geotrek.sensitivity.models import SportPractice, Species, SensitiveArea
from geotrek.sensitivity.factories import SpeciesFactory


class BiodivParserTests(TestCase):
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
        self.assertEqual(practice.name_fr, "Terrestre")
        self.assertEqual(species.name, u"Black grouse")
        self.assertEqual(species.name_fr, u"Tétras lyre")
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
        species = SpeciesFactory(name=u"Aigle royal")
        call_command('import', 'geotrek.sensitivity.parsers.SpeciesSensitiveAreaShapeParser', filename, verbosity=0)
        area = SensitiveArea.objects.get()
        self.assertEqual(area.species, species)
        self.assertEqual(area.contact, u"Contact")
        self.assertEqual(area.description, u"Test UTF8 éêè")
        self.assertEqual(
            area.geom.wkt,
            'POLYGON ((929315.3613368584774435 6483309.4435053952038288, '
            '929200.3539448172086850 6483204.0200626906007528, 928404.8861498644109815 6482494.8078117696568370, '
            '928194.0392644553212449 6482082.6979902880266309, 927925.6886830255389214 6481210.5586006408557296, '
            '927676.5060002692043781 6481287.2301953341811895, 927772.3454936370253563 6481498.0770807461813092, '
            '927887.3528856782941148 6481900.6029528900980949, 928184.4553151186555624 6482600.2312544705346227, '
            '928625.3169846105156466 6483520.2903908034786582, 929162.0181474700802937 6483664.0496308589354157, '
            '929315.3613368584774435 6483309.4435053952038288))')

    def test_ui(self):
        structure = StructureFactory()
        user = UserFactory.create(username='homer', password='dooh')
        UserProfileFactory(structure=structure, user=user)
        user.user_permissions.add(Permission.objects.get(codename='import_sensitivearea'))
        self.client.login(username='homer', password='dooh')

        filename = os.path.join(os.path.dirname(__file__), 'data', 'species.zip')
        f = open(filename, 'r')
        species = SpeciesFactory(name=u"Aigle royal")

        response_real = self.client.post(
            '/commands/import', {
                'upload-file': 'Upload',
                'with-file-parser': '1',
                'with-file-zipfile': f,
            }
        )
        self.assertEqual(response_real.status_code, 200)
        area = SensitiveArea.objects.get()
        self.assertEqual(area.species, species)
        self.assertEqual(area.contact, u"Contact")
        self.assertEqual(area.description, u"Test UTF8 éêè")
        self.assertEqual(
            area.geom.wkt,
            'POLYGON ((929315.3613368584774435 6483309.4435053952038288, '
            '929200.3539448172086850 6483204.0200626906007528, 928404.8861498644109815 6482494.8078117696568370, '
            '928194.0392644553212449 6482082.6979902880266309, 927925.6886830255389214 6481210.5586006408557296, '
            '927676.5060002692043781 6481287.2301953341811895, 927772.3454936370253563 6481498.0770807461813092, '
            '927887.3528856782941148 6481900.6029528900980949, 928184.4553151186555624 6482600.2312544705346227, '
            '928625.3169846105156466 6483520.2903908034786582, 929162.0181474700802937 6483664.0496308589354157, '
            '929315.3613368584774435 6483309.4435053952038288))')
        self.assertEqual(area.structure, structure)
