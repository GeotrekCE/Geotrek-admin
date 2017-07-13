from __future__ import unicode_literals

import json

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.testcases import TestCase

from geotrek.trekking import factories as trek_factory, models as trek_models

PAGINATED_JSON_STRUCTURE = sorted([
    'count', 'next', 'previous', 'results',
])

PAGINATED_GEOJSON_STRUCTURE = sorted([
    'count', 'next', 'previous', 'features', 'type'
])

GEOJSON_STRUCTURE = sorted([
    'geometry',
    'type',
    'bbox',
    'properties'
])

TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'arrival', 'ascent', 'create_datetime', 'departure', 'descent', 'description', 'description_teaser',
    'difficulty', 'duration', 'id', 'length_2d', 'length_3d', 'max_elevation', 'min_elevation',
    'name', 'networks', 'themes', 'update_datetime', 'url', 'practice', 'external_id', 'published'
])

TREK_DETAIL_JSON_STRUCTURE = sorted([
    'arrival', 'ascent', 'create_datetime', 'departure', 'descent', 'description', 'description_teaser',
    'difficulty', 'duration', 'id', 'length_2d', 'length_3d', 'max_elevation', 'min_elevation',
    'name', 'networks', 'themes', 'update_datetime', 'geometry', 'pictures', 'practice', 'external_id', 'published'
])

TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'arrival', 'ascent', 'create_datetime', 'departure', 'descent', 'description', 'description_teaser',
    'difficulty', 'duration', 'length_2d', 'length_3d', 'max_elevation', 'min_elevation',
    'name', 'networks', 'themes', 'update_datetime', 'pictures', 'practice', 'external_id', 'published'
])

POI_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'create_datetime', 'description', 'type', 'external_id', 'id', 'name', 'update_datetime', 'url', 'published'
])

POI_DETAIL_JSON_STRUCTURE = sorted([
    'create_datetime', 'description',
    'id', 'external_id', 'type',
    'name', 'update_datetime', 'geometry', 'pictures', 'published'
])

POI_DETAIL_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'create_datetime', 'description', 'external_id', 'type',
    'name', 'update_datetime', 'pictures', 'published'
])


class BaseApiTest(TestCase):
    """
    Base TestCase for all API profile
    """

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.nb_treks = 15
        cls.nb_pois = 55
        cls.treks = trek_factory.TrekWithPOIsFactory.create_batch(cls.nb_treks)

    def login(self):
        pass

    def get_trek_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-list'), params)

    def get_trek_detail(self, id_trek, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-detail', args=(id_trek,)), params)

    def get_trek_all_difficulties_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-all-difficulties'), params)

    def get_trek_all_practices_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-all-practices'), params)

    def get_trek_all_networks_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-all-networks'), params)

    def get_trek_all_themes_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-all-themes'), params)

    def get_poi_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:poi-list'), params)

    def get_poi_detail(self, id_poi, params=None):
        self.login()
        return self.client.get(reverse('apiv2:poi-detail', args=(id_poi,)), params)


class APIAnonymousTestCase(BaseApiTest):
    """
    TestCase for anonymous API profile
    """

    def test_trek_list(self):
        self.client.logout()
        response = self.get_trek_list()
        self.assertEqual(response.status_code, 401)

    def test_trek_detail(self):
        self.client.logout()
        response = self.get_trek_detail(trek_models.Trek.objects.order_by('?').first().pk)
        self.assertEqual(response.status_code, 401)

    def test_trek_difficulty_list(self):
        self.client.logout()
        response = self.get_trek_all_difficulties_list()
        self.assertEqual(response.status_code, 401)

    def test_trek_practice_list(self):
        self.client.logout()
        response = self.get_trek_all_practices_list()
        self.assertEqual(response.status_code, 401)

    def test_trek_theme_list(self):
        self.client.logout()
        response = self.get_trek_all_themes_list()
        self.assertEqual(response.status_code, 401)

    def test_trek_network_list(self):
        self.client.logout()
        response = self.get_trek_all_networks_list()
        self.assertEqual(response.status_code, 401)

    def test_poi_list(self):
        self.client.logout()
        response = self.get_poi_list()
        self.assertEqual(response.status_code, 401)

    def test_poi_detail(self):
        self.client.logout()
        response = self.get_poi_detail(trek_models.POI.objects.order_by('?').first().pk)
        self.assertEqual(response.status_code, 401)


class APIAccessAdministratorTestCase(BaseApiTest):
    """
    TestCase for administrator API profile
    """

    @classmethod
    def setUpTestData(cls):
        #  created user
        cls.administrator = User.objects.create(username="administrator", is_superuser=True,
                                                is_staff=True, is_active=True)
        cls.administrator.set_password('administrator')
        cls.administrator.save()
        cls.administrator.refresh_from_db()

        BaseApiTest.setUpTestData()

    def login(self):
        """
        Override base class login method, used before all function request 'get_api_element'
        """
        self.client.login(username="administrator", password="administrator")

    def test_trek_list(self):
        response = self.get_trek_list()
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_JSON_STRUCTURE)

        # trek count is ok
        self.assertEqual(len(json_response.get('results')),
                         self.nb_treks, json_response)

        # test dim 2 ok
        self.assertEqual(len(json_response.get('results')[0].get('geometry').get('coordinates')[0]),
                         2)

        # regenrate with geojson 3D
        response = self.get_trek_list({'format': 'geojson', 'dim': '3'})
        json_response = json.loads(response.content.decode('utf-8'))

        # test geojson format
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_GEOJSON_STRUCTURE)

        self.assertEqual(len(json_response.get('features')),
                         self.nb_treks, json_response)
        # test dim 3 ok
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')[0]),
                         3, json_response.get('features')[0].get('geometry').get('coordinates')[0])

        self.assertEqual(sorted(json_response.get('features')[0].keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE)

    def test_trek_detail(self):
        self.client.logout()
        id_trek = trek_models.Trek.objects.order_by('?').first().pk
        response = self.get_trek_detail(id_trek)
        # test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))
        # test default structure
        self.assertEqual(sorted(json_response.keys()),
                         TREK_DETAIL_JSON_STRUCTURE)

        response = self.get_trek_detail(id_trek, {'format': "geojson", "dim": "3"})
        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(sorted(json_response.keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('properties').keys()),
                         TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE)

    def test_trek_difficulty_list(self):
        self.client.logout()
        response = self.get_trek_all_difficulties_list()
        self.assertEqual(response.status_code, 200)

    def test_trek_practice_list(self):
        self.client.logout()
        response = self.get_trek_all_practices_list()
        self.assertEqual(response.status_code, 200)

    def test_trek_theme_list(self):
        self.client.logout()
        response = self.get_trek_all_themes_list()
        self.assertEqual(response.status_code, 200)

    def test_trek_network_list(self):
        self.client.logout()
        response = self.get_trek_all_networks_list()
        self.assertEqual(response.status_code, 200)

    def test_poi_list(self):
        response = self.get_poi_list()
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = json.loads(response.content.decode('utf-8'))
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_JSON_STRUCTURE)

        # trek count is ok
        self.assertEqual(len(json_response.get('results')),
                         trek_models.POI.objects.all().count())

        # test dim 2 ok
        self.assertEqual(len(json_response.get('results')[0].get('geometry').get('coordinates')),
                         2)

        # regenrate with geojson 3D
        response = self.get_poi_list({'format': 'geojson', 'dim': '3'})
        json_response = json.loads(response.content.decode('utf-8'))

        # test geojson format
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_GEOJSON_STRUCTURE)

        self.assertEqual(len(json_response.get('features')),
                         trek_models.POI.objects.all().count())
        # test dim 3
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')),
                         3)

        self.assertEqual(sorted(json_response.get('features')[0].keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         POI_LIST_PROPERTIES_GEOJSON_STRUCTURE)

    def test_poi_detail(self):
        self.client.logout()
        id_poi = trek_models.POI.objects.order_by('?').first().pk
        response = self.get_poi_detail(id_poi)
        # test response code
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.content.decode('utf-8'))
        # test default structure
        self.assertEqual(sorted(json_response.keys()),
                         POI_DETAIL_JSON_STRUCTURE)

        response = self.get_poi_detail(id_poi, {'format': "geojson", "dim": "3"})
        json_response = json.loads(response.content.decode('utf-8'))

        self.assertEqual(sorted(json_response.keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('properties').keys()),
                         POI_DETAIL_PROPERTIES_GEOJSON_STRUCTURE)
