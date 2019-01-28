# -*- coding: utf-8 -*-
import os

from django.contrib.auth.models import User, Permission
from django.conf import settings
from django.test import TestCase

from geotrek.authent.factories import StructureFactory, UserProfileFactory
from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.trekking.tests import TrekkingManagerTest
from geotrek.common.tests import TranslationResetMixin
from geotrek.sensitivity.factories import SensitiveAreaFactory


class SensitiveAreaViewsSameStructureTests(AuthentFixturesTest):
    def setUp(self):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        user = profile.user
        user.user_permissions.add(Permission.objects.get(codename="add_sensitivearea"))
        user.user_permissions.add(Permission.objects.get(codename="change_sensitivearea"))
        user.user_permissions.add(Permission.objects.get(codename="delete_sensitivearea"))
        user.user_permissions.add(Permission.objects.get(codename="read_sensitivearea"))
        user.user_permissions.add(Permission.objects.get(codename="export_sensitivearea"))
        self.client.login(username=user.username, password='dooh')
        self.area1 = SensitiveAreaFactory.create()
        structure = StructureFactory.create()
        self.area2 = SensitiveAreaFactory.create(structure=structure)

    def tearDown(self):
        self.client.logout()

    def test_can_edit_same_structure(self):
        url = "/sensitivearea/edit/{pk}/".format(pk=self.area1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_other_structure(self):
        url = "/sensitivearea/edit/{pk}/".format(pk=self.area2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/sensitivearea/{pk}/".format(pk=self.area2.pk))

    def test_can_delete_same_structure(self):
        url = "/sensitivearea/delete/{pk}/".format(pk=self.area1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_other_structure(self):
        url = "/sensitivearea/delete/{pk}/".format(pk=self.area2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/sensitivearea/{pk}/".format(pk=self.area2.pk))


class SensitiveAreaTemplatesTest(TestCase):
    def setUp(self):
        self.area = SensitiveAreaFactory.create()
        self.login()

    def login(self):
        User.objects.create_superuser('splash', 'splash@toto.com', password='booh')
        success = self.client.login(username='splash', password='booh')
        self.assertTrue(success)

    def tearDown(self):
        self.client.logout()

    def test_species_name_shown_in_detail_page(self):
        url = "/sensitivearea/{pk}/".format(pk=self.area.pk)
        response = self.client.get(url)
        self.assertContains(response, self.area.species.name)


class BasicJSONAPITest(TranslationResetMixin, TrekkingManagerTest):
    maxDiff = None

    def setUp(self):
        super(TrekkingManagerTest, self).setUp()
        self.sensitivearea = SensitiveAreaFactory.create()
        self.species = self.sensitivearea.species
        self.pk = self.sensitivearea.pk
        self.expected_properties = {
            'publication_date': str(self.sensitivearea.publication_date.strftime('%Y-%m-%d')),
            'published': True,
            'description': "Blabla",
            'contact': '<a href="mailto:toto@tata.com">toto@tata.com</a>',
            'kml_url': '/api/en/sensitiveareas/{pk}.kml'.format(pk=self.pk),
            'species': {
                "id": self.species.id,
                "name": self.species.name,
                'pictogram': os.path.join(settings.MEDIA_URL, self.species.pictogram.name),
                "period": [False, False, False, False, False, True, True, False, False, False, False, False],
                'practices': [
                    {'id': self.species.practices.all()[0].pk, 'name': self.species.practices.all()[0].name},
                    {'id': self.species.practices.all()[1].pk, 'name': self.species.practices.all()[1].name},
                ],
                'url': self.species.url,
            },
        }
        self.expected_geom = {
            u'type': u'Polygon',
            u'coordinates': [[
                [3.0000000000000004, 46.499999999999936],
                [3.0000000000000004, 46.500027013495476],
                [3.000039118674989, 46.50002701348879],
                [3.0000391186556095, 46.49999999999324],
                [3.0000000000000004, 46.499999999999936],
            ]],
        }
        self.expected_result = dict(self.expected_properties)
        self.expected_result['id'] = self.pk
        self.expected_result['geometry'] = self.expected_geom
        self.expected_geo_result = {
            'geometry': self.expected_geom,
            'type': 'Feature',
            'id': self.pk,
            'properties': self.expected_properties,
        }

    def test_object(self):
        url = '/api/en/sensitiveareas/{pk}.json'.format(pk=self.pk)
        response = self.client.get(url)
        self.assertJSONEqual(response.content, self.expected_result)

    def test_list(self):
        url = '/api/en/sensitiveareas.json'
        response = self.client.get(url)
        self.assertJSONEqual(response.content, [self.expected_result])

    def test_geo_object(self):
        url = '/api/en/sensitiveareas/{pk}.geojson'.format(pk=self.pk)
        response = self.client.get(url)
        self.assertJSONEqual(response.content, self.expected_geo_result)

    def test_geo_list(self):
        url = '/api/en/sensitiveareas.geojson'
        response = self.client.get(url)
        self.assertJSONEqual(response.content, {'type': 'FeatureCollection', 'features': [self.expected_geo_result]})


class APIv2Test(TranslationResetMixin, TrekkingManagerTest):
    maxDiff = None

    def setUp(self):
        super(TrekkingManagerTest, self).setUp()
        self.sensitivearea = SensitiveAreaFactory.create()
        self.species = self.sensitivearea.species
        self.pk = self.sensitivearea.pk
        self.expected_properties = {
            'create_datetime': str(self.sensitivearea.date_insert.isoformat().replace('+00:00', 'Z')),
            'update_datetime': str(self.sensitivearea.date_update.isoformat().replace('+00:00', 'Z')),
            'description': "Blabla",
            'contact': '<a href="mailto:toto@tata.com">toto@tata.com</a>',
            'kml_url': 'http://testserver/api/en/sensitiveareas/{pk}.kml'.format(pk=self.pk),
            'info_url': self.species.url,
            'species_id': self.species.id,
            "name": self.species.name,
            "period": [False, False, False, False, False, True, True, False, False, False, False, False],
            'practices': [p.pk for p in self.species.practices.all()],
            'structure': 'GEOTEAM',
            'published': True,
        }
        self.expected_geom = {
            'type': 'Polygon',
            'coordinates': [[
                [3.0000000000000004, 46.499999999999936],
                [3.0000000000000004, 46.500027013495476],
                [3.000039118674989, 46.50002701348879],
                [3.0000391186556095, 46.49999999999324],
                [3.0000000000000004, 46.499999999999936],
            ]],
        }
        self.expected_result = dict(self.expected_properties)
        self.expected_result['id'] = self.pk
        self.expected_result['geometry'] = self.expected_geom
        self.expected_result['url'] = 'http://testserver/api/v2/sensitivearea/{}/?format=json'.format(self.pk)
        self.expected_geo_result = {
            'bbox': [2.9999999999999996, 46.49999999999323, 3.000039118674988, 46.50002701349546],
            'geometry': self.expected_geom,
            'type': 'Feature',
            'id': self.pk,
            'properties': dict(self.expected_properties),
        }
        self.expected_geo_result['properties']['url'] = 'http://testserver/api/v2/sensitivearea/{}/?format=geojson'.format(self.pk)

    def test_object(self):
        url = '/api/v2/sensitivearea/{pk}/?format=json&period=ignore&language=en'.format(pk=self.pk)
        response = self.client.get(url)
        self.assertJSONEqual(response.content, self.expected_result)

    def test_list(self):
        url = '/api/v2/sensitivearea/?format=json&period=ignore&language=en'
        response = self.client.get(url)
        self.assertJSONEqual(response.content, {
            u'count': 1,
            u'previous': None,
            u'next': None,
            u'results': [self.expected_result],
        })

    def test_geo_object(self):
        url = '/api/v2/sensitivearea/{pk}/?format=geojson&period=ignore&language=en'.format(pk=self.pk)
        response = self.client.get(url)
        self.assertJSONEqual(response.content, self.expected_geo_result)

    def test_geo_list(self):
        url = '/api/v2/sensitivearea/?format=geojson&period=ignore&language=en'
        response = self.client.get(url)
        self.assertJSONEqual(response.content, {
            'count': 1,
            'next': None,
            'previous': None,
            'type': 'FeatureCollection',
            'features': [self.expected_geo_result]
        })

    def test_no_duplicates(self):
        url = '/api/v2/sensitivearea/?format=geojson&period=ignore&language=en&practices={}'.format(
            ','.join([str(p.pk) for p in self.species.practices.all()])
        )
        response = self.client.get(url)
        self.assertEqual(response.json()['count'], 1)
