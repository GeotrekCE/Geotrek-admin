from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Count
from django.test.client import Client
from django.test.testcases import TestCase

from geotrek.core import factories as core_factory, models as path_models
from geotrek.common import factories as common_factory
from geotrek.trekking import factories as trek_factory, models as trek_models
from geotrek.tourism import factories as tourism_factory, models as tourism_models

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
    'name', 'networks', 'themes', 'update_datetime', 'url', 'practice', 'external_id', 'second_external_id', 'published'
])

PATH_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted(['comments', 'length_2d', 'length_3d', 'name', 'url'])

TOUR_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted(TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE + ['count_children'])

TREK_DETAIL_JSON_STRUCTURE = sorted([
    'arrival', 'ascent', 'create_datetime', 'departure', 'descent', 'description', 'description_teaser',
    'difficulty', 'duration', 'id', 'length_2d', 'length_3d', 'max_elevation', 'min_elevation',
    'name', 'networks', 'themes', 'update_datetime', 'geometry', 'pictures', 'practice', 'external_id', 'second_external_id',
    'published', 'accessibilities'
])

TOUR_DETAIL_JSON_STRUCTURE = sorted(TREK_DETAIL_JSON_STRUCTURE + ['steps'])


TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'arrival', 'ascent', 'create_datetime', 'departure', 'descent', 'description', 'description_teaser',
    'difficulty', 'duration', 'length_2d', 'length_3d', 'max_elevation', 'min_elevation',
    'name', 'networks', 'themes', 'update_datetime', 'pictures', 'practice', 'external_id', 'second_external_id',
    'published'
])

TOUR_DETAIL_PROPERTIES_GEOJSON_STRUCTURE = sorted(TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE + ['steps'])

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

TOURISTIC_CONTENT_DETAIL_JSON_STRUCTURE = sorted([
    'approved', 'category', 'description', 'description_teaser', 'geometry', 'id', 'pictures'
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
        cls.theme = common_factory.ThemeFactory.create()
        cls.network = trek_factory.TrekNetworkFactory.create()
        cls.treks = trek_factory.TrekWithPOIsFactory.create_batch(cls.nb_treks)
        cls.treks[0].themes.add(cls.theme)
        cls.treks[0].networks.add(cls.network)
        cls.path = core_factory.PathFactory.create()
        cls.parent = trek_factory.TrekFactory.create(published=True, name='Parent')
        cls.child1 = trek_factory.TrekFactory.create(published=False, name='Child 1')
        cls.child2 = trek_factory.TrekFactory.create(published=True, name='Child 2')
        trek_models.OrderedTrekChild(parent=cls.parent, child=cls.child1, order=2).save()
        trek_models.OrderedTrekChild(parent=cls.parent, child=cls.child2, order=1).save()
        cls.content = tourism_factory.TouristicContentFactory.create(published=True)
        cls.nb_treks += 2  # add parent and 1 child published

    def login(self):
        pass

    def get_trek_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-list'), params)

    def get_trek_detail(self, id_trek, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-detail', args=(id_trek,)), params)

    def get_tour_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:tour-list'), params)

    def get_tour_detail(self, id_trek, params=None):
        self.login()
        return self.client.get(reverse('apiv2:tour-detail', args=(id_trek,)), params)

    def get_trek_all_difficulties_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-all-difficulties'), params)

    def get_trek_used_difficulties_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-used-difficulties'), params)

    def get_trek_all_practices_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-all-practices'), params)

    def get_trek_used_practices_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-used-practices'), params)

    def get_trek_all_networks_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-all-networks'), params)

    def get_trek_used_networks_list(self, params=None):
        # Not used in API but could be use in the future
        self.login()
        return self.client.get(reverse('apiv2:trek-used-networks'), params)

    def get_trek_all_themes_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:trek-all-themes'), params)

    def get_trek_used_themes_list(self, params=None):
        # Not used in API but could be use in the future
        self.login()
        return self.client.get(reverse('apiv2:trek-used-themes'), params)

    def get_poi_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:poi-list'), params)

    def get_poi_detail(self, id_poi, params=None):
        self.login()
        return self.client.get(reverse('apiv2:poi-detail', args=(id_poi,)), params)

    def get_poi_all_types_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:poi-all-types'), params)

    def get_poi_used_types_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:poi-used-types'), params)

    def get_path_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:path-list'), params)

    def get_path_detail(self, id_path, params=None):
        self.login()
        return self.client.get(reverse('apiv2:path-detail', args=(id_path,)), params)

    def get_touristiccontent_list(self, params=None):
        self.login()
        return self.client.get(reverse('apiv2:touristiccontent-list'), params)

    def get_touristiccontent_detail(self, id_content, params=None):
        self.login()
        return self.client.get(reverse('apiv2:touristiccontent-detail', args=(id_content,)), params)


class APIAnonymousTestCase(BaseApiTest):
    """
    TestCase for anonymous API profile
    """
    def test_path_list(self):
        self.client.logout()
        response = self.get_path_list()
        self.assertEqual(response.status_code, 401)

    def test_trek_list(self):
        self.client.logout()
        response = self.get_trek_list()
        self.assertEqual(response.status_code, 401)

    def test_trek_detail(self):
        self.client.logout()
        id_trek = trek_models.Trek.objects.annotate(
            count_parents=Count('trek_parents'), count_children=Count('trek_children')
        ).exclude(count_parents__gt=0).exclude(count_children__gt=0).order_by('?').first().pk
        response = self.get_trek_detail(id_trek)
        self.assertEqual(response.status_code, 401)

    def test_tour_list(self):
        self.client.logout()
        response = self.get_tour_list()
        self.assertEqual(response.status_code, 401)

    def test_tour_detail(self):
        self.client.logout()
        response = self.get_tour_detail(self.parent.pk)
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

    def test_trek_difficulty_used_list(self):
        self.client.logout()
        response = self.get_trek_used_difficulties_list()
        self.assertEqual(response.status_code, 401)

    def test_trek_practice_used_list(self):
        self.client.logout()
        response = self.get_trek_used_practices_list()
        self.assertEqual(response.status_code, 401)

    def test_trek_theme_used_list(self):
        self.client.logout()
        response = self.get_trek_used_themes_list()
        self.assertEqual(response.status_code, 401)

    def test_trek_network_used_list(self):
        self.client.logout()
        response = self.get_trek_used_networks_list()
        self.assertEqual(response.status_code, 401)

    def test_poi_list(self):
        self.client.logout()
        response = self.get_poi_list()
        self.assertEqual(response.status_code, 401)

    def test_poi_detail(self):
        self.client.logout()
        response = self.get_poi_detail(trek_models.POI.objects.order_by('?').first().pk)
        self.assertEqual(response.status_code, 401)

    def test_poi_type_all_list(self):
        self.client.logout()
        response = self.get_poi_used_types_list()
        self.assertEqual(response.status_code, 401)

    def test_poi_type_used_list(self):
        self.client.logout()
        response = self.get_poi_all_types_list()
        self.assertEqual(response.status_code, 401)

    def test_touristiccontent_detail(self):
        self.client.logout()
        response = self.get_touristiccontent_detail(self.content.pk)
        self.assertEqual(response.status_code, 401)

    def test_touristiccontent_list(self):
        self.client.logout()
        response = self.get_touristiccontent_list()
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

    def test_path_list(self):
        self.client.logout()
        response = self.get_path_list()
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_JSON_STRUCTURE)
        self.assertEqual(len(json_response.get('results')), path_models.Path.objects.all().count())
        self.assertEqual(len(json_response.get('results')[0].get('geometry').get('coordinates')[0]),
                         2)
        response = self.get_path_list({'format': 'geojson', 'dim': '3'})
        json_response = response.json()

        # test geojson format
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_GEOJSON_STRUCTURE)

        self.assertEqual(len(json_response.get('features')),
                         path_models.Path.objects.all().count(), json_response)
        # test dim 3 ok
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')[0]), 3)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         PATH_LIST_PROPERTIES_GEOJSON_STRUCTURE)

    def test_trek_list(self):
        response = self.get_trek_list()
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_JSON_STRUCTURE)

        # trek count is ok
        self.assertEqual(len(json_response.get('results')), self.nb_treks)

        # test dim 2 ok
        self.assertEqual(len(json_response.get('results')[0].get('geometry').get('coordinates')[0]),
                         2)

        # regenrate with geojson 3D
        response = self.get_trek_list({'format': 'geojson', 'dim': '3'})
        json_response = response.json()

        # test geojson format
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_GEOJSON_STRUCTURE)

        self.assertEqual(len(json_response.get('features')),
                         self.nb_treks, json_response)
        # test dim 3 ok
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')[0]), 3)

        self.assertEqual(sorted(json_response.get('features')[0].keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE)

    def test_tour_list(self):
        response = self.get_tour_list()
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_JSON_STRUCTURE)

        # trek count is ok
        self.assertEqual(len(json_response.get('results')), 1)  # Only one parent

        # test dim 2 ok
        self.assertEqual(len(json_response.get('results')[0].get('geometry').get('coordinates')[0]),
                         2)

        # regenrate with geojson 3D
        response = self.get_tour_list({'format': 'geojson', 'dim': '3'})
        json_response = response.json()

        # test geojson format
        self.assertEqual(sorted(json_response.keys()), PAGINATED_GEOJSON_STRUCTURE)

        self.assertEqual(len(json_response.get('features')), 1)
        # test dim 3 ok
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')[0]),
                         3, json_response.get('features')[0].get('geometry').get('coordinates')[0])

        self.assertEqual(sorted(json_response.get('features')[0].keys()), GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         TOUR_LIST_PROPERTIES_GEOJSON_STRUCTURE)

        self.assertEqual(json_response.get('features')[0].get('properties').get('count_children'), 2)

    def test_trek_detail(self):
        self.client.logout()
        id_trek = trek_models.Trek.objects.annotate(
            count_parents=Count('trek_parents'), count_children=Count('trek_children')
        ).exclude(count_parents__gt=0).exclude(count_children__gt=0).order_by('?').first().pk
        response = self.get_trek_detail(id_trek)
        # test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        # test default structure
        self.assertEqual(sorted(json_response.keys()),
                         TREK_DETAIL_JSON_STRUCTURE)

        response = self.get_trek_detail(id_trek, {'format': "geojson", "dim": "3"})
        json_response = response.json()

        self.assertEqual(sorted(json_response.keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('properties').keys()),
                         TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE)

    def test_tour_detail(self):
        self.client.logout()
        response = self.get_tour_detail(self.parent.pk)
        # test response code
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        # test default structure
        self.assertEqual(sorted(json_response.keys()),
                         TOUR_DETAIL_JSON_STRUCTURE)

        response = self.get_tour_detail(self.parent.pk, {'format': "geojson", "dim": "3"})
        json_response = response.json()

        self.assertEqual(sorted(json_response.keys()),
                         GEOJSON_STRUCTURE)
        self.assertEqual(sorted(json_response.get('properties').get('steps').get('features')[0].get('properties').keys()),
                         TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE)
        self.assertEqual(json_response.get('properties').get('steps').get('features')[0].get('properties').get('id'),
                         self.child2.pk)
        self.assertEqual(json_response.get('properties').get('steps').get('features')[1].get('properties').get('id'),
                         self.child1.pk)
        self.assertEqual(sorted(json_response.get('properties').keys()),
                         TOUR_DETAIL_PROPERTIES_GEOJSON_STRUCTURE)

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
        self.assertContains(response, self.theme.label)

    def test_trek_network_list(self):
        self.client.logout()
        response = self.get_trek_all_networks_list()
        self.assertContains(response, self.network.network)

    def test_trek_difficulty_used_list(self):
        self.client.logout()
        response = self.get_trek_used_difficulties_list()
        self.assertEqual(response.status_code, 200)

    def test_trek_practice_used_list(self):
        self.client.logout()
        response = self.get_trek_used_practices_list()
        self.assertEqual(response.status_code, 200)

    def test_trek_theme_used_list(self):
        self.client.logout()
        response = self.get_trek_used_themes_list()
        self.assertContains(response, self.theme.label)

    def test_trek_network_used_list(self):
        self.client.logout()
        response = self.get_trek_used_networks_list()
        self.assertContains(response, self.network.network)

    def test_poi_list(self):
        response = self.get_poi_list()
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
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
        json_response = response.json()

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

        json_response = response.json()
        # test default structure

        self.assertEqual(sorted(json_response.keys()),
                         POI_DETAIL_JSON_STRUCTURE)

        self.assertEqual(len(json_response.get('geometry').get('coordinates')), 2)

    def test_poi_detail_3d(self):
        self.client.logout()
        id_poi = trek_models.POI.objects.order_by('?').first().pk

        response = self.get_poi_detail(id_poi, {'format': "json", "dim": "3"})
        json_response = response.json()

        self.assertEqual(len(json_response.get('geometry').get('coordinates')), 3)

        self.assertEqual(sorted(json_response.keys()),
                         POI_DETAIL_JSON_STRUCTURE)

    def test_poi_detail_geojson_3d(self):
        self.client.logout()
        id_poi = trek_models.POI.objects.order_by('?').first().pk

        response = self.get_poi_detail(id_poi, {'format': "geojson", "dim": "3"})
        json_response = response.json()

        self.assertEqual(len(json_response.get('geometry').get('coordinates')), 3)

        self.assertEqual(sorted(json_response.keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('properties').keys()),
                         POI_DETAIL_PROPERTIES_GEOJSON_STRUCTURE)

    def test_poi_detail_geojson(self):
        self.client.logout()
        id_poi = trek_models.POI.objects.order_by('?').first().pk

        response = self.get_poi_detail(id_poi, {'format': "geojson"})
        json_response = response.json()

        self.assertEqual(len(json_response.get('geometry').get('coordinates')), 2)

        self.assertEqual(sorted(json_response.keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('properties').keys()),
                         POI_DETAIL_PROPERTIES_GEOJSON_STRUCTURE)

    def test_poi_detail_json_dim_3d(self):
        self.client.logout()
        id_poi = trek_models.POI.objects.order_by('?').first().pk

        response = self.get_poi_detail(id_poi, {'format': "json", "dim": "3"})
        json_response = response.json()

        self.assertEqual(sorted(json_response.keys()),
                         POI_DETAIL_JSON_STRUCTURE)

        self.assertEqual(len(json_response.get('geometry').get('coordinates')), 3)

    def test_poi_type_all_list(self):
        self.client.logout()
        response = self.get_poi_used_types_list()
        self.assertEqual(response.status_code, 200)

    def test_poi_type_used_list(self):
        self.client.logout()
        response = self.get_poi_all_types_list()
        self.assertEqual(response.status_code, 200)

    def test_poi_unpublished_detail_filter_published_false(self):
        self.client.logout()
        id_poi = trek_factory.POIFactory.create(published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'false'})
        self.assertEqual(response.status_code, 200)

    def test_poi_published_detail_filter_published_false(self):
        self.client.logout()
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'false'})
        self.assertEqual(response.status_code, 404)

    def test_poi_published_detail_filter_published_false_lang_en(self):
        self.client.logout()
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'false', 'language': 'en'})
        self.assertEqual(response.status_code, 200)

    def test_poi_published_detail_filter_published_false_lang_fr(self):
        self.client.logout()
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'false', 'language': 'fr'})
        self.assertEqual(response.status_code, 404)

    def test_poi_published_detail_filter_published_true_lang_fr(self):
        self.client.logout()
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'true', 'language': 'fr'})
        self.assertEqual(response.status_code, 200)

    def test_poi_published_detail_filter_published_ok(self):
        self.client.logout()
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'ok', 'language': 'fr'})
        self.assertEqual(response.status_code, 200)

    def test_touristiccontent_detail(self):
        self.client.logout()
        response = self.get_touristiccontent_detail(self.content.pk)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        # test default structure
        self.assertEqual(sorted(json_response.keys()),
                         TOURISTIC_CONTENT_DETAIL_JSON_STRUCTURE)

    def test_touristiccontent_list(self):
        self.client.logout()
        response = self.get_touristiccontent_list()
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_JSON_STRUCTURE)

        # touristiccontent count is ok
        self.assertEqual(len(json_response.get('results')),
                         tourism_models.TouristicContent.objects.all().count())


class APISwaggerTestCase(BaseApiTest):
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

    def test_schema_fields(self):
        self.login()
        response = self.client.get(reverse('apiv2:schema'))
        self.assertContains(response, 'Filter elements contained in bbox formatted like SW-lng,SW-lat,NE-lng,NE-lat')
        self.assertContains(response, 'Publication state. If language specified, ')
        self.assertContains(response, 'only language published are filterted. true/false/all. true by default.')
        self.assertContains(response, 'Reference point to compute distance LNG,LAT')
        self.assertContains(response, 'Practices ids separated by comas.')
