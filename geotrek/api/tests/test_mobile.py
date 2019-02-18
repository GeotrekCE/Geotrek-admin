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
    'features', 'type'
])

GEOJSON_STRUCTURE = sorted([
    'geometry',
    'type',
    'bbox',
    'properties'
])

TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'thumbnail', 'name', 'accessibilities', 'description_teaser', 'cities', 'description', 'departure', 'arrival', 'duration',
    'access', 'advised_parking', 'advice', 'difficulty', 'length_2d', 'ascent', 'descent', 'route',
    'is_park_centered', 'min_elevation', 'max_elevation', 'themes', 'networks', 'practice', 'pictures',
    'information_desks'
])


MINIMAL_TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'thumbnail', 'name', 'departure', 'accessibilities',
    'difficulty', 'practice', 'themes', 'length_2d',
])

POI_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'description', 'type', 'id', 'name', 'pictures', 'thumbnail',
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
        cls.treks = trek_factory.TrekWithPOIsFactory.create_batch(cls.nb_treks, name_fr='Coucou', description_fr="Sisi",
                                                                  description_teaser_fr="mini")

    def login(self):
        pass

    def get_trek_list(self, params=None):
        self.login()
        return self.client.get(reverse('apimobile:trek-list'), params, HTTP_ACCEPT_LANGUAGE='fr')

    def get_trek_detail(self, id_trek, params=None):
        self.login()
        return self.client.get(reverse('apimobile:trek-detail', args=(id_trek,)), params, HTTP_ACCEPT_LANGUAGE='fr')

    def get_minimal_trek_list(self, params=None):
        self.login()
        return self.client.get(reverse('apimobile:minimal_trek-list'), params, HTTP_ACCEPT_LANGUAGE='fr')

    def get_minimal_trek_detail(self, id_trek, params=None):
        self.login()
        return self.client.get(reverse('apimobile:minimal_trek-detail', args=(id_trek,)), params,
                               HTTP_ACCEPT_LANGUAGE='fr')

    def get_poi_list(self, params=None):
        self.login()
        return self.client.get(reverse('apimobile:poi-list'), params, HTTP_ACCEPT_LANGUAGE='fr')

    def get_poi_detail(self, id_poi, params=None):
        self.login()
        return self.client.get(reverse('apimobile:poi-detail', args=(id_poi,)), params, HTTP_ACCEPT_LANGUAGE='fr')


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

    def test_minimal_trek_list(self):
        self.client.logout()
        response = self.get_minimal_trek_list()
        self.assertEqual(response.status_code, 401)

    def test_minimal_trek_detail(self):
        self.client.logout()
        response = self.get_minimal_trek_detail(trek_models.Trek.objects.order_by('?').first().pk)
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

    def test_trek(self):
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

        self.assertEqual('Coucou', json_response.get('features')[0].get('properties').get('name'))
        self.assertEqual('Sisi', json_response.get('features')[0].get('properties').get('description'))
        self.assertEqual('mini', json_response.get('features')[0].get('properties').get('description_teaser'))

    def test_minimal_trek(self):
        response = self.get_minimal_trek_list()
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
        response = self.get_minimal_trek_list({'format': 'geojson', 'dim': '3'})
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
                         MINIMAL_TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE)

        self.assertEqual('Coucou', json_response.get('features')[0].get('properties').get('name'))
        self.assertIsNone(json_response.get('features')[0].get('properties').get('description'))
        self.assertIsNone(json_response.get('features')[0].get('properties').get('description_teaser'))

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
