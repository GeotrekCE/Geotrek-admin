from django.urls import reverse
from django.db.models import Count
from django.test.client import Client
from django.test.testcases import TestCase
from django.contrib.gis.geos import MultiPoint, Point
from django.conf import settings
from django.test.utils import override_settings

from geotrek.authent import factories as authent_factory, models as authent_models
from geotrek.core import factories as core_factory, models as path_models
from geotrek.common import factories as common_factory, models as common_models
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.trekking import factories as trek_factory, models as trek_models
from geotrek.tourism import factories as tourism_factory, models as tourism_models
from geotrek.zoning import factories as zoning_factory, models as zoning_models

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
    'name', 'networks', 'themes', 'update_datetime', 'url', 'practice', 'external_id', 'second_external_id', 'published', 'thumbnail'
])

PATH_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted(['comments', 'length_2d', 'length_3d', 'name', 'url'])

TOUR_LIST_PROPERTIES_GEOJSON_STRUCTURE = sorted(TREK_LIST_PROPERTIES_GEOJSON_STRUCTURE + ['count_children'])

TREK_DETAIL_JSON_STRUCTURE = sorted([
    'arrival', 'ascent', 'create_datetime', 'departure', 'descent', 'description', 'description_teaser',
    'difficulty', 'duration', 'id', 'length_2d', 'length_3d', 'max_elevation', 'min_elevation',
    'name', 'networks', 'themes', 'update_datetime', 'geometry', 'pictures', 'practice', 'external_id', 'second_external_id',
    'published', 'accessibilities', 'labels', 'advice', 'advised_parking',
    'parking_location', 'gpx', 'kml', 'children', 'parents', 'public_transport',
    'elevation_area_url', 'elevation_svg_url', 'altimetric_profile', 'reservation_system',
    'duration_pretty', 'ambiance', 'access', 'route', 'disabled_infrastructure', 'points_reference', 'category', 'structure', 'treks', 'previous', 'next', 'portal', 'source', 'information_desks', 'relationships', 'files', 'videos', 'thumbnail'
])

TOUR_DETAIL_JSON_STRUCTURE = sorted(TREK_DETAIL_JSON_STRUCTURE + ['steps'])


TREK_DETAIL_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'arrival', 'ascent', 'create_datetime', 'departure', 'descent', 'description', 'description_teaser',
    'difficulty', 'duration', 'length_2d', 'length_3d', 'max_elevation', 'min_elevation',
    'name', 'networks', 'themes', 'update_datetime', 'pictures', 'practice', 'external_id', 'second_external_id',
    'published', 'elevation_area_url', 'elevation_svg_url', 'altimetric_profile', 'reservation_system',
    'accessibilities', 'labels', 'advice', 'advised_parking',
    'parking_location', 'gpx', 'kml', 'children', 'parents', 'public_transport',
    'duration_pretty', 'ambiance', 'access', 'route', 'disabled_infrastructure', 'points_reference', 'category', 'structure', 'treks', 'previous', 'next', 'portal', 'source', 'information_desks', 'relationships', 'files', 'videos', 'thumbnail'
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

CITY_PROPERTIES_JSON_STRUCTURE = sorted([
    'code', 'name', 'published'
])

DISTRICT_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'name', 'published'
])

ROUTE_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'route', 'pictogram'
])

THEME_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'label', 'pictogram'
])

ACCESSIBILITY_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'name', 'pictogram'
])

TARGET_PORTAL_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'name', 'website', 'title', 'description', 'facebook_id', 'facebook_image_url'
])

STRUCTURE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name'])


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
        cls.label = trek_factory.LabelTrekFactory()
        cls.treks = trek_factory.TrekWithPOIsFactory.create_batch(cls.nb_treks)
        cls.treks[0].themes.add(cls.theme)
        cls.treks[0].networks.add(cls.network)
        cls.treks[0].labels.add(cls.label)
        trek_models.TrekRelationship(trek_a=cls.treks[0], trek_b=cls.treks[1]).save()
        information_desk_type = tourism_factory.InformationDeskTypeFactory()
        info_desk = tourism_factory.InformationDeskFactory(type=information_desk_type)
        cls.treks[0].information_desks.add(info_desk)
        cls.attachment_1 = common_factory.AttachmentFactory.create(content_object=cls.treks[0], attachment_file=get_dummy_uploaded_image())
        cls.treks[3].parking_location = None
        cls.treks[3].points_reference = MultiPoint([Point(0, 0), Point(1, 1)], srid=settings.SRID)
        cls.treks[3].save()
        cls.path = core_factory.PathFactory.create()
        cls.parent = trek_factory.TrekFactory.create(published=True, name='Parent')
        cls.child1 = trek_factory.TrekFactory.create(published=False, name='Child 1')
        cls.child2 = trek_factory.TrekFactory.create(published=True, name='Child 2')
        trek_models.TrekRelationship(trek_a=cls.parent, trek_b=cls.treks[0]).save()
        trek_models.OrderedTrekChild(parent=cls.parent, child=cls.child1, order=2).save()
        trek_models.OrderedTrekChild(parent=cls.parent, child=cls.child2, order=1).save()
        trek_models.OrderedTrekChild(parent=cls.treks[0], child=cls.child2, order=3).save()
        cls.content = tourism_factory.TouristicContentFactory.create(published=True)
        cls.city = zoning_factory.CityFactory(code=31000)
        cls.district = zoning_factory.DistrictFactory(id=420)
        cls.accessibility = trek_factory.AccessibilityFactory(id=4)
        cls.route = trek_factory.RouteFactory()
        cls.theme = common_factory.ThemeFactory(id=15)
        cls.portal = common_factory.TargetPortalFactory(id=16)
        cls.structure = authent_factory.StructureFactory(id=8)
        cls.nb_treks += 2  # add parent and 1 child published

    def get_trek_list(self, params=None):
        return self.client.get(reverse('apiv2:trek-list'), params)

    def get_trek_detail(self, id_trek, params=None):
        return self.client.get(reverse('apiv2:trek-detail', args=(id_trek,)), params)

    def get_tour_list(self, params=None):
        return self.client.get(reverse('apiv2:tour-list'), params)

    def get_tour_detail(self, id_trek, params=None):
        return self.client.get(reverse('apiv2:tour-detail', args=(id_trek,)), params)

    def get_difficulties_list(self, params=None):
        return self.client.get(reverse('apiv2:difficulty-list'), params)

    def get_trek_difficulties_list(self, params=None):
        return self.client.get(reverse('apiv2:trek-difficulties'), params)

    def get_practices_list(self, params=None):
        return self.client.get(reverse('apiv2:practice-list'), params)

    def get_trek_practices_list(self, params=None):
        return self.client.get(reverse('apiv2:trek-practices'), params)

    def get_networks_list(self, params=None):
        return self.client.get(reverse('apiv2:network-list'), params)

    def get_trek_networks_list(self, params=None):
        return self.client.get(reverse('apiv2:trek-networks'), params)

    def get_themes_list(self, params=None):
        return self.client.get(reverse('apiv2:theme-list'), params)

    def get_themes_detail(self, id_theme, params=None):
        return self.client.get(reverse('apiv2:theme-detail', args=(id_theme,)), params)

    def get_city_list(self, params=None):
        return self.client.get(reverse('apiv2:city-list'), params)

    def get_city_detail(self, id_city, params=None):
        return self.client.get(reverse('apiv2:city-detail', args=(id_city,)), params)

    def get_district_list(self, params=None):
        return self.client.get(reverse('apiv2:district-list'), params)

    def get_district_detail(self, id_district, params=None):
        return self.client.get(reverse('apiv2:district-detail', args=(id_district,)), params)

    def get_route_list(self, params=None):
        return self.client.get(reverse('apiv2:route-list'), params)

    def get_route_detail(self, id_route, params=None):
        return self.client.get(reverse('apiv2:route-detail', args=(id_route,)), params)

    def get_accessibility_list(self, params=None):
        return self.client.get(reverse('apiv2:accessibility-list'), params)

    def get_accessibility_detail(self, id_accessibility, params=None):
        return self.client.get(reverse('apiv2:accessibility-detail', args=(id_accessibility,)), params)

    def get_portal_list(self, params=None):
        return self.client.get(reverse('apiv2:portal-list'), params)

    def get_portal_detail(self, id_portal, params=None):
        return self.client.get(reverse('apiv2:portal-detail', args=(id_portal,)), params)

    def get_structure_list(self, params=None):
        return self.client.get(reverse('apiv2:structure-list'), params)

    def get_structure_detail(self, id_structure, params=None):
        return self.client.get(reverse('apiv2:structure-detail', args=(id_structure,)), params)

    def get_poi_list(self, params=None):
        return self.client.get(reverse('apiv2:poi-list'), params)

    def get_poi_detail(self, id_poi, params=None):
        return self.client.get(reverse('apiv2:poi-detail', args=(id_poi,)), params)

    def get_poi_all_types_list(self, params=None):
        return self.client.get(reverse('apiv2:poi-all-types'), params)

    def get_poi_used_types_list(self, params=None):
        return self.client.get(reverse('apiv2:poi-used-types'), params)

    def get_path_list(self, params=None):
        return self.client.get(reverse('apiv2:path-list'), params)

    def get_path_detail(self, id_path, params=None):
        return self.client.get(reverse('apiv2:path-detail', args=(id_path,)), params)

    def get_touristiccontent_list(self, params=None):
        return self.client.get(reverse('apiv2:touristiccontent-list'), params)

    def get_touristiccontent_detail(self, id_content, params=None):
        return self.client.get(reverse('apiv2:touristiccontent-detail', args=(id_content,)), params)


class APIAccessAnonymousTestCase(BaseApiTest):
    """
    TestCase for administrator API profile
    """

    @classmethod
    def setUpTestData(cls):
        BaseApiTest.setUpTestData()

    def test_path_list(self):
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

    def test_trek_list_filters(self):
        response = self.get_trek_list({
            'duration_min': '2',
            'duration_max': '5',
            'length_min': '4',
            'length_max': '20',
            'difficulty_min': '1',
            'difficulty_max': '3',
            'ascent_min': '150',
            'ascent_max': '1000',
            'city': '31000',
            'district': '420',
            'structure': '8',
            'accessibility': '4',
            'theme': '15',
            'portal': '16'
        })
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_tour_list(self):
        response = self.get_tour_list()
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_JSON_STRUCTURE)

        # trek count is ok
        self.assertEqual(len(json_response.get('results')), 2)  # Two parents

        # test dim 2 ok
        self.assertEqual(len(json_response.get('results')[0].get('geometry').get('coordinates')[0]),
                         2)

        # regenrate with geojson 3D
        response = self.get_tour_list({'format': 'geojson', 'dim': '3'})
        json_response = response.json()

        # test geojson format
        self.assertEqual(sorted(json_response.keys()), PAGINATED_GEOJSON_STRUCTURE)

        self.assertEqual(len(json_response.get('features')), 2)
        # test dim 3 ok
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')[0]),
                         3, json_response.get('features')[0].get('geometry').get('coordinates')[0])

        self.assertEqual(sorted(json_response.get('features')[0].keys()), GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         TOUR_LIST_PROPERTIES_GEOJSON_STRUCTURE)

        self.assertEqual(json_response.get('features')[0].get('properties').get('count_children'), 1)

    def test_trek_detail(self):
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

        # calls to cover all cases of fields to display
        response = self.get_trek_detail(self.treks[0].id)
        self.assertEqual(response.status_code, 200)

        response = self.get_trek_detail(self.treks[3].id)
        self.assertEqual(response.status_code, 200)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_ITINERANCY=True)
    def test_trek_detail_categories_split_itinerancy(self):
        response = self.get_trek_detail(self.parent.id)
        self.assertEqual(response.status_code, 200)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=True)
    def test_trek_detail_categories_split_practice(self):
        response = self.get_trek_detail(self.treks[0].id)
        self.assertEqual(response.status_code, 200)

    def test_tour_detail(self):
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

    def test_trek_difficulties_list(self):
        response = self.get_trek_difficulties_list()
        self.assertEquals(response.status_code, 302)

    def test_difficulty_list(self):
        response = self.get_difficulties_list()
        self.assertEqual(response.status_code, 200)

    def test_trek_practices_list(self):
        response = self.get_trek_practices_list()
        self.assertEquals(response.status_code, 302)

    def test_practice_list(self):
        response = self.get_practices_list()
        self.assertEqual(response.status_code, 200)

    def test_trek_network_list(self):
        response = self.get_trek_networks_list()
        self.assertEquals(response.status_code, 302)

    def test_network_list(self):
        response = self.get_networks_list()
        self.assertContains(response, self.network.network)

    def test_theme_list(self):
        response = self.get_themes_list()
        self.assertContains(response, self.theme.label)

    def test_city_list(self):
        response = self.get_city_list()
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(json_response['results']), zoning_models.City.objects.count())

    def test_city_detail(self):
        response = self.get_city_detail(self.city.pk)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(sorted(json_response.keys()), CITY_PROPERTIES_JSON_STRUCTURE)

    def test_district_list(self):
        response = self.get_district_list()
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(json_response['results']), zoning_models.District.objects.count())

    def test_district_detail(self):
        response = self.get_district_detail(self.district.pk)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(sorted(json_response.keys()), DISTRICT_PROPERTIES_JSON_STRUCTURE)

    def test_route_list(self):
        response = self.get_route_list()
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(json_response['results']), trek_models.Route.objects.count())

    def test_route_detail(self):
        response = self.get_route_detail(self.route.pk)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(sorted(json_response.keys()), ROUTE_PROPERTIES_JSON_STRUCTURE)

    def test_accessibility_list(self):
        response = self.get_accessibility_list()
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(json_response['results']), trek_models.Accessibility.objects.count())

    def test_accessibility_detail(self):
        response = self.get_accessibility_detail(self.accessibility.pk)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(sorted(json_response.keys()), ACCESSIBILITY_PROPERTIES_JSON_STRUCTURE)

    def test_theme_detail(self):
        response = self.get_themes_detail(self.theme.pk)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(sorted(json_response.keys()), THEME_PROPERTIES_JSON_STRUCTURE)

    def test_portal_list(self):
        response = self.get_portal_list()
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(json_response['results']), common_models.TargetPortal.objects.count())

    def test_portal_detail(self):
        response = self.get_portal_detail(self.portal.pk)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(sorted(json_response.keys()), TARGET_PORTAL_PROPERTIES_JSON_STRUCTURE)

    def test_structure_list(self):
        response = self.get_structure_list()
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(json_response), authent_models.Structure.objects.count())

    def test_structure_detail(self):
        response = self.get_structure_detail(self.structure.pk)
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(sorted(json_response.keys()), STRUCTURE_PROPERTIES_JSON_STRUCTURE)

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
        id_poi = trek_models.POI.objects.order_by('?').first().pk

        response = self.get_poi_detail(id_poi, {'format': "json", "dim": "3"})
        json_response = response.json()

        self.assertEqual(len(json_response.get('geometry').get('coordinates')), 3)

        self.assertEqual(sorted(json_response.keys()),
                         POI_DETAIL_JSON_STRUCTURE)

    def test_poi_detail_geojson_3d(self):
        id_poi = trek_models.POI.objects.order_by('?').first().pk

        response = self.get_poi_detail(id_poi, {'format': "geojson", "dim": "3"})
        json_response = response.json()

        self.assertEqual(len(json_response.get('geometry').get('coordinates')), 3)

        self.assertEqual(sorted(json_response.keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('properties').keys()),
                         POI_DETAIL_PROPERTIES_GEOJSON_STRUCTURE)

    def test_poi_detail_geojson(self):
        id_poi = trek_models.POI.objects.order_by('?').first().pk

        response = self.get_poi_detail(id_poi, {'format': "geojson"})
        json_response = response.json()

        self.assertEqual(len(json_response.get('geometry').get('coordinates')), 2)

        self.assertEqual(sorted(json_response.keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('properties').keys()),
                         POI_DETAIL_PROPERTIES_GEOJSON_STRUCTURE)

    def test_poi_detail_json_dim_3d(self):
        id_poi = trek_models.POI.objects.order_by('?').first().pk

        response = self.get_poi_detail(id_poi, {'format': "json", "dim": "3"})
        json_response = response.json()

        self.assertEqual(sorted(json_response.keys()),
                         POI_DETAIL_JSON_STRUCTURE)

        self.assertEqual(len(json_response.get('geometry').get('coordinates')), 3)

    def test_poi_type_all_list(self):
        response = self.get_poi_used_types_list()
        self.assertEqual(response.status_code, 200)

    def test_poi_type_used_list(self):
        response = self.get_poi_all_types_list()
        self.assertEqual(response.status_code, 200)

    def test_poi_unpublished_detail_filter_published_false(self):
        id_poi = trek_factory.POIFactory.create(published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'false'})
        self.assertEqual(response.status_code, 200)

    def test_poi_published_detail_filter_published_false(self):
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'false'})
        self.assertEqual(response.status_code, 404)

    def test_poi_published_detail_filter_published_false_lang_en(self):
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'false', 'language': 'en'})
        self.assertEqual(response.status_code, 200)

    def test_poi_published_detail_filter_published_false_lang_fr(self):
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'false', 'language': 'fr'})
        self.assertEqual(response.status_code, 404)

    def test_poi_published_detail_filter_published_true_lang_fr(self):
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'true', 'language': 'fr'})
        self.assertEqual(response.status_code, 200)

    def test_poi_published_detail_filter_published_ok(self):
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'published': 'ok', 'language': 'fr'})
        self.assertEqual(response.status_code, 200)

    def test_touristiccontent_detail(self):
        response = self.get_touristiccontent_detail(self.content.pk)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        # test default structure
        self.assertEqual(sorted(json_response.keys()),
                         TOURISTIC_CONTENT_DETAIL_JSON_STRUCTURE)

    def test_touristiccontent_list(self):
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
        BaseApiTest.setUpTestData()

    def test_schema_fields(self):
        response = self.client.get(reverse('apiv2:schema'))
        self.assertContains(response, 'Filter elements contained in bbox formatted like SW-lng,SW-lat,NE-lng,NE-lat')
        self.assertContains(response, 'Publication state. If language specified, ')
        self.assertContains(response, 'only language published are filterted. true/false/all. true by default.')
        self.assertContains(response, 'Reference point to compute distance LNG,LAT')
        self.assertContains(response, 'Practices ids separated by comas.')
