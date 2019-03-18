from django.core.urlresolvers import reverse
from django.test.client import Client
from django.test.testcases import TestCase

from geotrek.trekking import factories as trek_factory, models as trek_models

POI_GEOJSON_STRUCTURE = sorted([
    'features', 'type'
])

GEOJSON_STRUCTURE = sorted([
    'geometry',
    'type',
    'properties'
])

GEOJSON_STRUCTURE_WITHOUT_BBOX = sorted([
    'geometry',
    'type',
    'properties'
])

TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'first_picture', 'name', 'accessibilities', 'description_teaser', 'cities', 'description', 'departure', 'arrival',
    'access', 'advised_parking', 'advice', 'difficulty', 'length', 'ascent', 'descent', 'route', 'duration',
    'is_park_centered', 'min_elevation', 'max_elevation', 'themes', 'networks', 'practice', 'pictures',
    'information_desks', 'departure_city', 'arrival_city', 'parking_location'
])


TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'first_picture', 'name', 'departure', 'accessibilities', 'duration',
    'difficulty', 'practice', 'themes', 'length', 'cities', 'route', 'departure_city', 'ascent', 'descent',
])

POI_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'description', 'id', 'name', 'pictures', 'type'
])


class BaseApiTest(TestCase):
    """
    Base TestCase for all API profile
    """

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.nb_treks = 1

        cls.treks = trek_factory.TrekWithPublishedPOIsFactory.create_batch(
            cls.nb_treks, name_fr='Coucou', description_fr="Sisi",
            description_teaser_fr="mini", published_fr=True)

    def login(self):
        pass

    def get_treks_list(self, params=None):
        self.login()
        return self.client.get(reverse('apimobile:treks-list'), params, HTTP_ACCEPT_LANGUAGE='fr')

    def get_treks_detail(self, id_trek, params=None):
        self.login()
        return self.client.get(reverse('apimobile:treks-detail', args=(id_trek,)), params, HTTP_ACCEPT_LANGUAGE='fr')

    def get_poi_list(self, id_trek, params=None):
        self.login()
        return self.client.get(reverse('apimobile:treks-pois', args=(id_trek, )), params, HTTP_ACCEPT_LANGUAGE='fr')


class APIAccessTestCase(BaseApiTest):
    """
    TestCase for administrator API profile
    """

    @classmethod
    def setUpTestData(cls):
        #  created user
        BaseApiTest.setUpTestData()

    def login(self):
        pass

    def test_trek_detail(self):
        response = self.get_treks_detail(trek_models.Trek.objects.order_by('?').first().pk)
        #  test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()

        # test geojson format
        self.assertEqual(sorted(json_response.keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('properties').keys()),
                         TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE)

        self.assertEqual('Coucou', json_response.get('properties').get('name'))
        self.assertEqual('Sisi', json_response.get('properties').get('description'))
        self.assertEqual('mini', json_response.get('properties').get('description_teaser'))

    def test_trek_list(self):
        response = self.get_treks_list()
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()

        # trek count is ok
        self.assertEqual(len(json_response.get('features')),
                         self.nb_treks)

        # test dim 2 ok
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')),
                         2)

        self.assertEqual(sorted(json_response.get('features')[0].keys()),
                         GEOJSON_STRUCTURE_WITHOUT_BBOX)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE)

        self.assertEqual('Coucou', json_response.get('features')[0].get('properties').get('name'))
        self.assertIsNone(json_response.get('features')[0].get('properties').get('description'))
        self.assertIsNone(json_response.get('features')[0].get('properties').get('description_teaser'))

    def test_poi_list(self):
        response = self.get_poi_list(trek_models.Trek.objects.first().pk)
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()

        # poi count by treks is ok
        self.assertEqual(len(json_response.get('features')),
                         trek_models.Trek.objects.order_by('?').last().published_pois.count())

        # test dim 2 ok
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')),
                         2)

        self.assertEqual(sorted(json_response.keys()),
                         POI_GEOJSON_STRUCTURE)

        self.assertEqual(len(json_response.get('features')),
                         trek_models.POI.objects.all().count())
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')),
                         2)

        self.assertEqual(sorted(json_response.get('features')[0].keys()),
                         GEOJSON_STRUCTURE_WITHOUT_BBOX)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         POI_LIST_PROPERTIES_GEOJSON_STRUCTURE)
