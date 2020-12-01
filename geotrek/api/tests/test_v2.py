from django.contrib.auth.models import User
from django.urls import reverse
from django.test.client import Client
from django.test.testcases import TestCase
from django.contrib.gis.geos import MultiPoint, Point
from django.conf import settings
from django.test.utils import override_settings

from geotrek.authent import factories as authent_factory, models as authent_models
from geotrek.core import factories as core_factory, models as path_models
from geotrek.common import factories as common_factory, models as common_models
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_file, get_dummy_uploaded_document
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

TREK_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'access', 'accessibilities', 'advice', 'advised_parking',
    'altimetric_profile', 'ambiance', 'arrival', 'ascent', 'attachments',
    'children', 'create_datetime', 'departure', 'descent', 'description',
    'description_teaser', 'difficulty', 'disabled_infrastructure',
    'duration', 'elevation_area_url', 'elevation_svg_url', 'external_id',
    'gpx', 'information_desks', 'kml', 'labels', 'length_2d',
    'length_3d', 'max_elevation', 'min_elevation', 'name', 'networks',
    'next', 'parents', 'parking_location', 'points_reference',
    'portal', 'practice', 'previous', 'public_transport', 'published',
    'reservation_system', 'route', 'second_external_id', 'source', 'structure',
    'themes', 'thumbnail', 'update_datetime', 'url'
])

PATH_PROPERTIES_GEOJSON_STRUCTURE = sorted(['comments', 'length_2d', 'length_3d', 'name', 'url'])

TOUR_PROPERTIES_GEOJSON_STRUCTURE = sorted(TREK_PROPERTIES_GEOJSON_STRUCTURE + ['count_children', 'steps'])

POI_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'create_datetime', 'description', 'external_id',
    'name', 'pictures', 'published', 'type', 'update_datetime', 'url'
])

TOURISTIC_CONTENT_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'approved', 'category', 'description', 'description_teaser', 'geometry', 'pictures', 'url'
])

CITY_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'geometry', 'name', 'published'
])

DISTRICT_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'geometry', 'name', 'published'
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
    'id', 'name', 'website', 'title', 'description', 'facebook_id', 'facebook_image_url', 'facebook_image_height', 'facebook_image_width'
])

STRUCTURE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name'])

TREK_LABEL_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'advice', 'filter_rando', 'name', 'pictogram'])

INFORMATION_DESK_PROPERTIES_JSON_STRUCTURE = sorted([
    'description', 'email', 'latitude', 'longitude',
    'municipality', 'name', 'phone', 'photo_url',
    'postal_code', 'street', 'type', 'website'
])

SOURCE_PROPERTIES_JSON_STRUCTURE = sorted(['name', 'pictogram', 'website'])

RESRVATION_SYSTEM_PROPERTIES_JSON_STRUCTURE = sorted(['name', 'id'])


class BaseApiTest(TestCase):
    """
    Base TestCase for all API profile
    """

    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.nb_treks = 15
        cls.theme = common_factory.ThemeFactory.create()
        cls.network = trek_factory.TrekNetworkFactory.create()
        cls.label = trek_factory.LabelTrekFactory(id=23)
        cls.treks = trek_factory.TrekWithPOIsFactory.create_batch(cls.nb_treks)
        cls.treks[0].themes.add(cls.theme)
        cls.treks[0].networks.add(cls.network)
        cls.treks[0].labels.add(cls.label)
        trek_models.TrekRelationship(trek_a=cls.treks[0], trek_b=cls.treks[1]).save()
        information_desk_type = tourism_factory.InformationDeskTypeFactory()
        cls.info_desk = tourism_factory.InformationDeskFactory(type=information_desk_type)
        cls.treks[0].information_desks.add(cls.info_desk)
        common_factory.AttachmentFactory.create(content_object=cls.treks[0], attachment_file=get_dummy_uploaded_image())
        common_factory.AttachmentFactory.create(content_object=cls.treks[0], attachment_file=get_dummy_uploaded_file())
        common_factory.AttachmentFactory.create(content_object=cls.treks[0], attachment_file=get_dummy_uploaded_document())
        common_factory.AttachmentFactory(content_object=cls.treks[0], attachment_file='', attachment_video='https://www.youtube.com/embed/Jm3anSjly0Y?wmode=opaque')
        common_factory.AttachmentFactory(content_object=cls.treks[0], attachment_file='', attachment_video='', attachment_link='https://geotrek.fr/assets/img/logo.svg')
        common_factory.AttachmentFactory(content_object=cls.treks[0], attachment_file='', attachment_video='', attachment_link='')
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
        cls.route = trek_factory.RouteFactory(id=680)
        cls.theme = common_factory.ThemeFactory(id=15)
        cls.portal = common_factory.TargetPortalFactory(id=16)
        cls.structure = authent_factory.StructureFactory(id=8)
        cls.nb_treks += 2  # add parent and 1 child published
        cls.poi_type = trek_factory.POITypeFactory()
        cls.poi = trek_factory.POIFactory()
        cls.source = common_factory.RecordSourceFactory()
        cls.reservation_system = common_factory.ReservationSystemFactory()

    def check_number_elems_response(self, response, model):
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(len(json_response['results']), model.objects.count())

    def check_structure_response(self, response, structure):
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEquals(sorted(json_response.keys()), structure)

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

    def get_practices_list(self, params=None):
        return self.client.get(reverse('apiv2:practice-list'), params)

    def get_networks_list(self, params=None):
        return self.client.get(reverse('apiv2:network-list'), params)

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

    def get_poi_type(self, params=None):
        return self.client.get(reverse('apiv2:poitype-list'), params)

    def get_path_list(self, params=None):
        return self.client.get(reverse('apiv2:path-list'), params)

    def get_path_detail(self, id_path, params=None):
        return self.client.get(reverse('apiv2:path-detail', args=(id_path,)), params)

    def get_touristiccontent_list(self, params=None):
        return self.client.get(reverse('apiv2:touristiccontent-list'), params)

    def get_touristiccontent_detail(self, id_content, params=None):
        return self.client.get(reverse('apiv2:touristiccontent-detail', args=(id_content,)), params)

    def get_treklabel_list(self, params=None):
        return self.client.get(reverse('apiv2:treklabel-list'), params)

    def get_treklabel_detail(self, id_label, params=None):
        return self.client.get(reverse('apiv2:treklabel-detail', args=(id_label,)), params)

    def get_informationdesk_list(self, params=None):
        return self.client.get(reverse('apiv2:informationdesk-list'), params)

    def get_informationdesk_detail(self, id_infodesk, params=None):
        return self.client.get(reverse('apiv2:informationdesk-detail', args=(id_infodesk,)), params)

    def get_source_list(self, params=None):
        return self.client.get(reverse('apiv2:source-list'), params)

    def get_source_detail(self, id_source, params=None):
        return self.client.get(reverse('apiv2:source-detail', args=(id_source,)), params)

    def get_reservationsystem_list(self, params=None):
        return self.client.get(reverse('apiv2:reservationsystem-list'), params)

    def get_reservationsystem_detail(self, id_reservationsystem, params=None):
        return self.client.get(reverse('apiv2:reservationsystem-detail', args=(id_reservationsystem,)), params)

    def get_config(self, params=None):
        return self.client.get(reverse('apiv2:config', params))


class APIAccessAnonymousTestCase(BaseApiTest):
    """
    TestCase for administrator API profile
    """

    @classmethod
    def setUpTestData(cls):
        BaseApiTest.setUpTestData()

    def test_path_list(self):
        response = self.get_path_list()
        self.assertEqual(response.status_code, 401)

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

        # test dim 3 by default for treks
        self.assertEqual(len(json_response.get('results')[0].get('geometry').get('coordinates')[0]),
                         3)

        # regenrate with geojson
        response = self.get_trek_list({'format': 'geojson'})
        json_response = response.json()

        # test geojson format
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_GEOJSON_STRUCTURE)

        self.assertEqual(len(json_response.get('features')),
                         self.nb_treks, json_response)

        self.assertEqual(sorted(json_response.get('features')[0].keys()),
                         GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         TREK_PROPERTIES_GEOJSON_STRUCTURE)

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
            'portal': '16',
            'label': '23',
            'route': '68',
            'q': 'test string'
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

        # regenrate with geojson
        response = self.get_tour_list({'format': 'geojson'})
        json_response = response.json()

        # test geojson format
        self.assertEqual(sorted(json_response.keys()), PAGINATED_GEOJSON_STRUCTURE)

        self.assertEqual(len(json_response.get('features')), 2)
        # test dim 3 ok
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')[0]),
                         3, json_response.get('features')[0].get('geometry').get('coordinates')[0])

        self.assertEqual(sorted(json_response.get('features')[0].keys()), GEOJSON_STRUCTURE)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         TOUR_PROPERTIES_GEOJSON_STRUCTURE)

        self.assertEqual(json_response.get('features')[0].get('properties').get('count_children'), 1)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_ITINERANCY=True)
    def test_trek_detail_categories_split_itinerancy(self):
        response = self.get_trek_detail(self.parent.id)
        self.assertEqual(response.status_code, 200)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=True)
    def test_trek_detail_categories_split_practice(self):
        response = self.get_trek_detail(self.treks[0].id)
        self.assertEqual(response.status_code, 200)

    def test_difficulty_list(self):
        response = self.get_difficulties_list()
        self.assertEqual(response.status_code, 200)

    def test_practice_list(self):
        response = self.get_practices_list()
        self.assertEqual(response.status_code, 200)

    def test_network_list(self):
        response = self.get_networks_list()
        self.assertContains(response, self.network.network)

    def test_theme_list(self):
        response = self.get_themes_list()
        self.assertContains(response, self.theme.label)

    def test_city_list(self):
        self.check_number_elems_response(
            self.get_city_list(),
            zoning_models.City
        )

    def test_city_detail(self):
        self.check_structure_response(
            self.get_city_detail(self.city.pk),
            CITY_PROPERTIES_JSON_STRUCTURE
        )

    def test_district_list(self):
        self.check_number_elems_response(
            self.get_district_list(),
            zoning_models.District
        )

    def test_district_detail(self):
        self.check_structure_response(
            self.get_district_detail(self.district.pk),
            DISTRICT_PROPERTIES_JSON_STRUCTURE
        )

    def test_route_list(self):
        self.check_number_elems_response(
            self.get_route_list(),
            trek_models.Route
        )

    def test_route_detail(self):
        self.check_structure_response(
            self.get_route_detail(self.route.pk),
            ROUTE_PROPERTIES_JSON_STRUCTURE
        )

    def test_accessibility_list(self):
        self.check_number_elems_response(
            self.get_accessibility_list(),
            trek_models.Accessibility
        )

    def test_accessibility_detail(self):
        self.check_structure_response(
            self.get_accessibility_detail(self.accessibility.pk),
            ACCESSIBILITY_PROPERTIES_JSON_STRUCTURE
        )

    def test_theme_detail(self):
        self.check_structure_response(
            self.get_themes_detail(self.theme.pk),
            THEME_PROPERTIES_JSON_STRUCTURE
        )

    def test_portal_list(self):
        self.check_number_elems_response(
            self.get_portal_list(),
            common_models.TargetPortal
        )

    def test_portal_detail(self):
        self.check_structure_response(
            self.get_portal_detail(self.portal.pk),
            TARGET_PORTAL_PROPERTIES_JSON_STRUCTURE
        )

    def test_structure_list(self):
        self.check_number_elems_response(
            self.get_structure_list(),
            authent_models.Structure
        )

    def test_structure_detail(self):
        self.check_structure_response(
            self.get_structure_detail(self.structure.pk),
            STRUCTURE_PROPERTIES_JSON_STRUCTURE
        )

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

        # regenerate with geojson 3D
        response = self.get_poi_list({'format': 'geojson'})
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
                         POI_PROPERTIES_GEOJSON_STRUCTURE)

        response = self.get_poi_list({'type': self.poi_type.pk, 'trek': self.treks[0].pk})
        self.assertEqual(response.status_code, 200)

    def test_poi_type(self):
        response = self.get_poi_type()
        self.assertEqual(response.status_code, 200)

    def test_poi_published_detail(self):
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk)
        self.assertEqual(response.status_code, 200)

    def test_poi_not_published_detail_lang_en(self):
        id_poi = trek_factory.POIFactory.create(published_fr=True, published=False)
        response = self.get_poi_detail(id_poi.pk, {'language': 'en'})
        self.assertEqual(response.status_code, 404)

    def test_poi_not_published_detail(self):
        id_poi = trek_factory.POIFactory.create(published=False)
        response = self.get_poi_detail(id_poi.pk)
        self.assertEqual(response.status_code, 404)

    def test_touristiccontent_detail(self):
        self.check_structure_response(
            self.get_touristiccontent_detail(self.content.pk),
            TOURISTIC_CONTENT_DETAIL_JSON_STRUCTURE
        )

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

        response = self.get_touristiccontent_list({
            'near_trek': self.treks[0].pk
        })
        #  test response code
        self.assertEqual(response.status_code, 200)

    def test_treklabels_list(self):
        self.check_number_elems_response(
            self.get_treklabel_list(),
            trek_models.LabelTrek
        )

    def test_treklabels_detail(self):
        self.check_structure_response(
            self.get_treklabel_detail(self.label.pk),
            TREK_LABEL_PROPERTIES_JSON_STRUCTURE
        )

    def test_informationdesk_list(self):
        self.check_number_elems_response(
            self.get_informationdesk_list(),
            tourism_models.InformationDesk
        )

    def test_informationdesk_detail(self):
        self.check_structure_response(
            self.get_informationdesk_detail(self.info_desk.pk),
            INFORMATION_DESK_PROPERTIES_JSON_STRUCTURE
        )

    def test_source_list(self):
        self.check_number_elems_response(
            self.get_source_list(),
            common_models.RecordSource
        )

    def test_source_detail(self):
        self.check_structure_response(
            self.get_source_detail(self.source.pk),
            SOURCE_PROPERTIES_JSON_STRUCTURE
        )

    def test_reservationsystem_list(self):
        self.check_number_elems_response(
            self.get_reservationsystem_list(),
            common_models.ReservationSystem
        )

    def test_reservationsystem_detail(self):
        self.check_structure_response(
            self.get_reservationsystem_detail(self.reservation_system.pk),
            RESRVATION_SYSTEM_PROPERTIES_JSON_STRUCTURE
        )

    def test_config(self):
        response = self.get_config()
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()), ['bbox'])


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
        self.login()
        response = self.get_path_list()
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_JSON_STRUCTURE)
        self.assertEqual(len(json_response.get('results')), path_models.Path.objects.all().count())
        response = self.get_path_list({'format': 'geojson'})
        json_response = response.json()

        # test geojson format
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_GEOJSON_STRUCTURE)

        self.assertEqual(len(json_response.get('features')),
                         path_models.Path.objects.all().count(), json_response)
        # test dim 3 ok
        self.assertEqual(len(json_response.get('features')[0].get('geometry').get('coordinates')[0]), 3)

        self.assertEqual(sorted(json_response.get('features')[0].get('properties').keys()),
                         PATH_PROPERTIES_GEOJSON_STRUCTURE)


class APISwaggerTestCase(BaseApiTest):
    """
    TestCase for administrator API profile
    """

    @classmethod
    def setUpTestData(cls):
        BaseApiTest.setUpTestData()

    def test_schema_fields(self):
        response = self.client.get('/api/v2.json')
        self.assertContains(response, 'Filter elements contained in bbox formatted like SW-lng,SW-lat,NE-lng,NE-lat')
        self.assertContains(response, 'Set language for translation. \'all\' by default')
        self.assertContains(response, 'Set minimum difficulty for a trek. Difficulty usually goes ')
        self.assertContains(response, 'Reference point to compute distance LNG,LAT')
        self.assertContains(response, 'Practices ids separated by comas.')

    def test_swagger_ui(self):
        response = self.client.get('/api/v2/')
        self.assertContains(response, 'swagger')
