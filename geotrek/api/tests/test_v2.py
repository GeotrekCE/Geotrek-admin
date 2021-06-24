from unittest import skipIf

from django.contrib.gis.geos import MultiLineString
from django.urls import reverse
from django.test.testcases import TestCase
from django.contrib.gis.geos import MultiPoint, Point, LineString
from django.conf import settings
from django.test.utils import override_settings

from geotrek.authent import factories as authent_factory, models as authent_models
from geotrek.feedback import factories as feedback_factory
from geotrek.core import factories as core_factory, models as path_models
from geotrek.common import factories as common_factory, models as common_models
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_file, get_dummy_uploaded_document
from geotrek.flatpages import factories as flatpages_factory
from geotrek.outdoor import factories as outdoor_factory, models as outdoor_models
from geotrek.sensitivity import factories as sensitivity_factory, models as sensitivity_models
from geotrek.trekking import factories as trek_factory, models as trek_models
from geotrek.tourism import factories as tourism_factory, models as tourism_models
from geotrek.zoning import factories as zoning_factory, models as zoning_models
from mapentity.factories import SuperUserFactory


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
    'children', 'cities', 'create_datetime', 'departure', 'departure_geom',
    'descent', 'description', 'description_teaser', 'difficulty', 'departure_city',
    'disabled_infrastructure', 'duration', 'elevation_area_url', 'elevation_svg_url',
    'external_id', 'gpx', 'information_desks', 'kml', 'labels', 'length_2d',
    'length_3d', 'max_elevation', 'min_elevation', 'name', 'networks',
    'next', 'parents', 'parking_location', 'pdf', 'points_reference',
    'portal', 'practice', 'previous', 'public_transport', 'published',
    'reservation_system', 'route', 'second_external_id', 'source', 'structure',
    'themes', 'update_datetime', 'url'
])

PATH_PROPERTIES_GEOJSON_STRUCTURE = sorted(['comments', 'length_2d', 'length_3d', 'name', 'url'])

TOUR_PROPERTIES_GEOJSON_STRUCTURE = sorted(TREK_PROPERTIES_GEOJSON_STRUCTURE + ['count_children', 'steps'])

POI_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'create_datetime', 'description', 'external_id',
    'name', 'attachments', 'published', 'type', 'update_datetime', 'url'
])

TOURISTIC_CONTENT_CATEGORY_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label', 'order', 'pictogram', 'types'
])

TOURISTIC_CONTENT_DETAIL_JSON_STRUCTURE = sorted([
    'approved', 'attachments', 'category', 'cities', 'contact', 'create_datetime', 'description',
    'description_teaser', 'departure_city', 'email', 'external_id', 'geometry', 'id', 'name', 'pdf',
    'portal', 'practical_info', 'published', 'reservation_id', 'reservation_system',
    'source', 'structure', 'themes', 'types', 'update_datetime', 'url', 'website',
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

TREK_LABEL_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'advice', 'filter', 'name', 'pictogram'])

INFORMATION_DESK_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'description', 'email', 'latitude', 'longitude',
    'municipality', 'name', 'phone', 'photo_url',
    'postal_code', 'street', 'type', 'website'
])

SOURCE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name', 'pictogram', 'website'])

RESERVATION_SYSTEM_PROPERTIES_JSON_STRUCTURE = sorted(['name', 'id'])

SITE_PROPERTIES_JSON_STRUCTURE = sorted([
    'advice', 'ambiance', 'description', 'description_teaser', 'eid', 'geometry', 'id',
    'information_desks', 'labels', 'name', 'period', 'portal', 'practice', 'source', 'managers',
    'structure', 'themes', 'url', 'web_links', 'orientation', 'wind', 'ratings_min', 'ratings_max',
])

OUTDOORPRACTICE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name'])

SITETYPE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name', 'practice'])

SENSITIVE_AREA_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'contact', 'create_datetime', 'description', 'elevation', 'geometry',
    'info_url', 'kml_url', 'name', 'period', 'practices', 'published', 'species_id',
    'structure', 'update_datetime', 'url'
])

SENSITIVE_AREA_SPECIES_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'name', 'period01', 'period02', 'period03',
    'period04', 'period05', 'period06', 'period07',
    'period08', 'period09', 'period10', 'period11',
    'period12', 'practices', 'radius', 'url'
])

COURSE_PROPERTIES_JSON_STRUCTURE = sorted([
    'advice', 'description', 'eid', 'equipment', 'geometry', 'height', 'id',
    'length', 'name', 'ratings', 'site', 'structure', 'url',
])

ORGANISM_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name'])


class BaseApiTest(TestCase):
    """
    Base TestCase for all API profile
    """

    @classmethod
    def setUpTestData(cls):
        cls.nb_treks = 15
        cls.organism = common_factory.OrganismFactory.create()
        cls.theme = common_factory.ThemeFactory.create()
        cls.network = trek_factory.TrekNetworkFactory.create()
        cls.label = common_factory.LabelFactory(id=23)
        cls.path = core_factory.PathFactory.create(geom=LineString((0, 0), (0, 10)))
        cls.treks = trek_factory.TrekWithPOIsFactory.create_batch(cls.nb_treks, paths=[(cls.path, 0, 1)], geom=cls.path.geom)
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
        cls.content = tourism_factory.TouristicContentFactory.create(published=True, geom='SRID=2154;POINT(0 0)')
        cls.content2 = tourism_factory.TouristicContentFactory.create(published=True, geom='SRID=2154;POINT(0 0)')
        cls.city = zoning_factory.CityFactory(code='01000', geom='SRID=2154;MULTIPOLYGON(((-1 -1, -1 1, 1 1, 1 -1, -1 -1)))')
        cls.district = zoning_factory.DistrictFactory(geom='SRID=2154;MULTIPOLYGON(((-1 -1, -1 1, 1 1, 1 -1, -1 -1)))')
        cls.accessibility = trek_factory.AccessibilityFactory()
        cls.route = trek_factory.RouteFactory()
        cls.theme2 = common_factory.ThemeFactory()
        cls.portal = common_factory.TargetPortalFactory()
        cls.treks[0].portal.add(cls.portal)
        cls.structure = authent_factory.StructureFactory()
        cls.treks[0].structure = cls.structure
        cls.poi_type = trek_factory.POITypeFactory()
        cls.practice = trek_factory.PracticeFactory()
        cls.difficulty = trek_factory.DifficultyLevelFactory()
        cls.network = trek_factory.TrekNetworkFactory()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.poi = trek_factory.POIFactory(paths=[(cls.treks[0].paths.all()[0], 0.5, 0.5)])
        cls.source = common_factory.RecordSourceFactory()
        cls.reservation_system = common_factory.ReservationSystemFactory()
        cls.treks[0].reservation_system = cls.reservation_system
        cls.site = outdoor_factory.SiteFactory(managers=[cls.organism])
        cls.category = tourism_factory.TouristicContentCategoryFactory()
        cls.content2.category = cls.category
        cls.content2.portal.add(cls.portal)
        common_factory.FileTypeFactory.create(type='Topoguide')
        cls.sensitivearea = sensitivity_factory.SensitiveAreaFactory()
        cls.sensitivearea_practice = sensitivity_factory.SportPracticeFactory()
        cls.sensitivearea_species = sensitivity_factory.SpeciesFactory()
        cls.parent = trek_factory.TrekFactory.create(
            published=True,
            name='Parent',
            route=cls.route,
            structure=cls.structure,
            reservation_system=cls.reservation_system,
            practice=cls.practice,
            difficulty=cls.difficulty,
        )
        cls.parent.accessibilities.add(cls.accessibility)
        cls.parent.source.add(cls.source)
        cls.parent.themes.add(cls.theme2)
        cls.parent.networks.add(cls.network)
        cls.parent.save()
        # For unpublished treks we avoid to create new reservation system and routes
        cls.parent2 = trek_factory.TrekFactory.create(published=False, name='Parent2', reservation_system=cls.reservation_system, route=cls.route)
        cls.child1 = trek_factory.TrekFactory.create(published=False, name='Child 1', reservation_system=cls.reservation_system, route=cls.route)
        cls.child2 = trek_factory.TrekFactory.create(published=True, name='Child 2')
        cls.child3 = trek_factory.TrekFactory.create(published=False, name='Child 3', reservation_system=cls.reservation_system, route=cls.route)
        trek_models.TrekRelationship(trek_a=cls.parent, trek_b=cls.treks[0]).save()
        trek_models.OrderedTrekChild(parent=cls.parent, child=cls.child1, order=2).save()
        trek_models.OrderedTrekChild(parent=cls.parent, child=cls.child2, order=1).save()
        trek_models.OrderedTrekChild(parent=cls.parent2, child=cls.child3, order=1).save()
        trek_models.OrderedTrekChild(parent=cls.treks[0], child=cls.child2, order=3).save()
        # Create a trek with a multilinestring geom
        cls.path2 = core_factory.PathFactory.create(geom=LineString((0, 10), (0, 20)))
        cls.path3 = core_factory.PathFactory.create(geom=LineString((0, 20), (0, 30)))
        cls.trek_multilinestring = trek_factory.TrekFactory.create(
            paths=[(cls.path, 0, 1), (cls.path2, 0, 1), (cls.path3, 0, 1)],
            geom=MultiLineString([cls.path.geom, cls.path3.geom])
        )
        cls.path2.delete()
        cls.trek_multilinestring.reload()
        cls.trek_multilinestring.published = True
        cls.trek_multilinestring.save()
        # Create a trek with a point geom
        cls.trek_point = trek_factory.TrekFactory.create(paths=[(cls.path, 0, 0)], geom=Point(cls.path.geom.coords[0]))
        cls.nb_treks += 4  # add parent, 1 child published and treks with a multilinestring/point geom
        cls.course = outdoor_factory.CourseFactory(site=cls.site)
        # create a reference point for distance filter (in 4326, Cahors city)
        cls.reference_point = Point(x=1.4388656616210938,
                                    y=44.448487178796235, srid=4326)

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

    def get_difficulty_detail(self, id_difficulty, params=None):
        return self.client.get(reverse('apiv2:difficulty-detail', args=(id_difficulty,)), params)

    def get_practices_list(self, params=None):
        return self.client.get(reverse('apiv2:practice-list'), params)

    def get_practices_detail(self, id_practice, params=None):
        return self.client.get(reverse('apiv2:practice-detail', args=(id_practice,)), params)

    def get_networks_list(self, params=None):
        return self.client.get(reverse('apiv2:network-list'), params)

    def get_network_detail(self, id_network, params=None):
        return self.client.get(reverse('apiv2:network-detail', args=(id_network,)), params)

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

    def get_touristiccontentcategory_list(self, params=None):
        return self.client.get(reverse('apiv2:touristiccontentcategory-list'), params)

    def get_touristiccontentcategory_detail(self, id_category, params=None):
        return self.client.get(reverse('apiv2:touristiccontentcategory-detail', args=(id_category,)), params)

    def get_touristiccontent_list(self, params=None):
        return self.client.get(reverse('apiv2:touristiccontent-list'), params)

    def get_touristiccontent_detail(self, id_content, params=None):
        return self.client.get(reverse('apiv2:touristiccontent-detail', args=(id_content,)), params)

    def get_label_list(self, params=None):
        return self.client.get(reverse('apiv2:label-list'), params)

    def get_label_detail(self, id_label, params=None):
        return self.client.get(reverse('apiv2:label-detail', args=(id_label,)), params)

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

    def get_site_list(self, params=None):
        return self.client.get(reverse('apiv2:site-list'), params)

    def get_site_detail(self, id_site, params=None):
        return self.client.get(reverse('apiv2:site-detail', args=(id_site,)), params)

    def get_course_list(self, params=None):
        return self.client.get(reverse('apiv2:course-list'), params)

    def get_course_detail(self, id_course, params=None):
        return self.client.get(reverse('apiv2:course-detail', args=(id_course,)), params)

    def get_outdoorpractice_list(self, params=None):
        return self.client.get(reverse('apiv2:outdoor-practice-list'), params)

    def get_outdoorpractice_detail(self, id_practice, params=None):
        return self.client.get(reverse('apiv2:outdoor-practice-detail', args=(id_practice,)), params)

    def get_sitetype_list(self, params=None):
        return self.client.get(reverse('apiv2:sitetype-list'), params)

    def get_sitetype_detail(self, id_type, params=None):
        return self.client.get(reverse('apiv2:sitetype-detail', args=(id_type,)), params)

    def get_sensitivearea_list(self, params=None):
        return self.client.get(reverse('apiv2:sensitivearea-list'), params)

    def get_sensitivearea_detail(self, id_sensitivearea, params=None):
        return self.client.get(reverse('apiv2:sensitivearea-detail', args=(id_sensitivearea,)), params)

    def get_sensitiveareapractice_list(self, params=None):
        return self.client.get(reverse('apiv2:sportpractice-list'), params)

    def get_sensitiveareapractice_detail(self, id_sensitivearea_practice, params=None):
        return self.client.get(reverse('apiv2:sportpractice-detail', args=(id_sensitivearea_practice,)), params)

    def get_sensitiveareaspecies_list(self, params=None):
        return self.client.get(reverse('apiv2:species-list'), params)

    def get_sensitiveareaspecies_detail(self, id_sensitivearea_species, params=None):
        return self.client.get(reverse('apiv2:species-detail', args=(id_sensitivearea_species,)), params)

    def get_config(self, params=None):
        return self.client.get(reverse('apiv2:config', params))

    def get_organism_list(self, params=None):
        return self.client.get(reverse('apiv2:organism-list'), params)

    def get_organism_detail(self, id_organism, params=None):
        return self.client.get(reverse('apiv2:organism-detail', args=(id_organism,)), params)

    def get_status_list(self, params=None):
        return self.client.get(reverse('apiv2:feedback-status'), params)

    def get_activity_list(self, params=None):
        return self.client.get(reverse('apiv2:feedback-activity'), params)

    def get_category_list(self, params=None):
        return self.client.get(reverse('apiv2:feedback-category'), params)

    def get_magnitude_list(self, params=None):
        return self.client.get(reverse('apiv2:feedback-magnitude'), params)


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

        # regenerate with geojson
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
            'cities': '31000',
            'districts': self.district.pk,
            'structures': self.structure.pk,
            'accessibilities': self.accessibility.pk,
            'themes': self.theme2.pk,
            'portals': self.portal.pk,
            'labels': '23',
            'routes': '68',
            'practices': '1',
            'q': 'test string',
        })
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_list_filter_distance(self):
        """ Test Trek list is filtered by reference point distance """
        toulouse_trek_geom = LineString([
            [
                1.4464187622070312,
                43.65147866566022
            ],
            [
                1.435432434082031,
                43.63682057801007
            ],
            [
                1.4574050903320312,
                43.62439567002734
            ],
            [
                1.4426422119140625,
                43.601775746067986
            ],
            [
                1.473541259765625,
                43.58810023846608
            ]], srid=4326)
        toulouse_trek_geom.transform(2154)
        path_trek = core_factory.PathFactory(geom=toulouse_trek_geom)
        trek_toulouse = trek_factory.TrekFactory(paths=[(path_trek, 0, 1)], geom=toulouse_trek_geom)
        # trek is in non filtered list
        response = self.get_trek_list()
        # json collection structure is ok
        json_response = response.json()
        ids_treks = [element['id'] for element in json_response['results']]
        self.assertIn(trek_toulouse.pk, ids_treks, ids_treks)

        # test trek is in distance filter (< 110 km)
        response = self.get_trek_list({
            'dist': '110000',
            'point': f"{self.reference_point.x},{self.reference_point.y}",
        })
        # json collection structure is ok
        json_response = response.json()
        ids_treks = [element['id'] for element in json_response['results']]
        self.assertIn(trek_toulouse.pk, ids_treks)

        # test trek is not in distance filter (< 50km)
        response = self.get_trek_list({
            'dist': '50000',
            'point': f"{self.reference_point.x},{self.reference_point.x}",
        })
        # json collection structure is ok
        json_response = response.json()
        ids_treks = [element['id'] for element in json_response['results']]
        self.assertNotIn(trek_toulouse.pk, ids_treks)

    def test_trek_list_filters_inexistant_zones(self):
        response = self.get_trek_list({
            'cities': '99999',
            'districts': '999',
        })
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_city(self):
        response = self.get_trek_list({'cities': self.city.pk})
        self.assertEqual(len(response.json()['results']), 17)

    def test_trek_child_not_published_detail_view_ok_if_ancestor_published(self):
        response = self.get_trek_detail(self.child1.pk)
        self.assertEqual(response.status_code, 200)

    def test_trek_child_not_published_detail_view_ko_if_ancestor_published_not_in_requested_language(self):
        response = self.get_trek_detail(self.child1.pk, {'language': 'fr'})
        self.assertEqual(response.status_code, 404)

    def test_trek_child_not_published_detail_view_ko_if_ancestor_not_published(self):
        response = self.get_trek_detail(self.child3.pk)
        self.assertEqual(response.status_code, 404)

    def test_trek_child_not_published_not_in_list_view_if_ancestor_published(self):
        response = self.get_trek_list({'fields': 'id'})
        self.assertNotContains(response, str(self.child1.pk))

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

        self.assertEqual(json_response.get('features')[1].get('properties').get('count_children'), 1)

    @override_settings(ONLY_EXTERNAL_PUBLIC_PDF=True)
    def test_trek_external_pdf(self):
        response = self.get_trek_detail(self.parent.id)
        self.assertEqual(response.status_code, 200)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_ITINERANCY=True)
    def test_trek_detail_categories_split_itinerancy(self):
        response = self.get_trek_detail(self.parent.id)
        self.assertEqual(response.status_code, 200)

    @override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=True)
    def test_trek_detail_categories_split_practice(self):
        response = self.get_trek_detail(self.treks[0].id)
        self.assertEqual(response.status_code, 200)

    def test_trek_detail_with_lang(self):
        response = self.get_trek_list({'language': 'en'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'][0]['pdf'],
                         f'http://testserver/api/en/treks/{self.child2.pk}/child-2.pdf')

    def test_difficulty_list(self):
        response = self.get_difficulties_list()
        self.assertEqual(response.status_code, 200)

    def test_difficulty_detail(self):
        response = self.get_difficulty_detail(self.difficulty.pk)
        self.assertEqual(response.status_code, 200)

    def test_practice_list(self):
        response = self.get_practices_list()
        self.assertEqual(response.status_code, 200)

    def test_practice_detail(self):
        response = self.get_practices_detail(self.practice.pk)
        self.assertEqual(response.status_code, 200)

    def test_network_list(self):
        response = self.get_networks_list({'portals': self.portal.pk})
        self.assertContains(response, self.network.network)

    def test_network_detail(self):
        response = self.get_network_detail(self.network.pk)
        self.assertEqual(response.status_code, 200)

    def test_theme_list(self):
        response = self.get_themes_list({'portals': self.portal.pk})
        self.assertContains(response, self.theme.label)

    def test_theme_list_filter_portal(self):
        portal2 = common_factory.TargetPortalFactory()
        trek = trek_factory.TrekFactory.create(published=True)
        trek.portal.add(portal2)
        trek.themes.add(self.theme)
        trek.save()
        # Ok because the trek is published
        response = self.get_themes_list({'portals': portal2.pk})
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        trek.published = False
        trek.save()
        # No theme should be returned because the trek is not published anymore
        response = self.get_themes_list({'portals': portal2.pk})
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

        trek.published = True
        trek.deleted = True
        trek.save()
        # No theme should be returned because the published trek on this portal is deleted
        response = self.get_themes_list({'portals': portal2.pk})
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

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
            self.get_themes_detail(self.theme2.pk),
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

    def test_structure_filter_list(self):
        response = self.get_structure_list({'portals': self.portal.pk, 'language': 'en'})
        self.assertEquals(len(response.json()['results']), 1)

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

        response = self.get_poi_list({'types': self.poi_type.pk, 'trek': self.treks[0].pk})
        self.assertEqual(response.status_code, 200)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_poi_list_filter_trek(self):
        response = self.get_poi_list({'trek': self.treks[0].pk})
        json_response = response.json()
        #  test response code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(json_response.get('results')),
            trek_models.POI.objects.all().count()
        )

        t = self.treks[0]
        t.pois_excluded.add(self.poi)
        t.save()

        response = self.get_poi_list({'trek': t.pk})
        json_response = response.json()
        #  test response code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_response.get('results')), trek_models.POI.objects.all().count() - 1)

    def test_poi_list_filter_distance(self):
        """ Test POI list is filtered by reference point distance """
        geom_path = LineString([(1.4464187622070312, 43.65147866566022),
                                (1.435432434082031, 43.63682057801007)], srid=4326)
        geom_path.transform(2154)
        pois_path = core_factory.PathFactory(geom=geom_path)
        geom_point_1 = Point(x=1.4464187622070312,
                             y=43.65147866566022, srid=4326)
        geom_point_1.transform(2154)
        poi_1 = trek_factory.POIFactory(paths=[(pois_path, 0, 0)],
                                        geom=geom_point_1)
        geom_point_2 = Point(x=1.435432434082031,
                             y=43.63682057801007, srid=4326)
        geom_point_2.transform(2154)
        poi_2 = trek_factory.POIFactory(paths=[(pois_path, 0, 0)],
                                        geom=geom_point_2)
        # pois are in list is in non filtered list
        response = self.get_poi_list()
        # json collection structure is ok
        json_response = response.json()
        ids_pois = [element['id'] for element in json_response['results']]
        self.assertIn(poi_1.pk, ids_pois)
        self.assertIn(poi_2.pk, ids_pois)

        # test pois is in distance filter (< 110000 km)
        response = self.get_poi_list({
            'dist': '110000',
            'point': f"{self.reference_point.x},{self.reference_point.y}",
        })
        # json collection structure is ok
        json_response = response.json()
        ids_pois = [element['id'] for element in json_response['results']]
        self.assertIn(poi_1.pk, ids_pois)
        self.assertIn(poi_2.pk, ids_pois)

        # test trek is not in distance filter (< 50km)
        response = self.get_poi_list({
            'dist': '50000',
            'point': f"{self.reference_point.x},{self.reference_point.x}",
        })
        # json collection structure is ok
        json_response = response.json()
        ids_pois = [element['id'] for element in json_response['results']]
        self.assertNotIn(poi_1.pk, ids_pois)
        self.assertNotIn(poi_2.pk, ids_pois)

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

    def test_touristiccontentcategory_detail(self):
        self.check_structure_response(
            self.get_touristiccontentcategory_detail(self.category.pk),
            TOURISTIC_CONTENT_CATEGORY_DETAIL_JSON_STRUCTURE
        )

    def test_touristiccontentcategory_list(self):
        json_response = self.get_touristiccontentcategory_list().json()
        # Get two objects for the two published touristic contents
        self.assertEquals(len(json_response['results']), 2)

    def test_touristiccontentcategory_list_filter(self):
        response = self.get_touristiccontentcategory_list({'portals': self.portal.pk})
        self.assertEquals(len(response.json()['results']), 1)

    def test_touristiccontent_detail(self):
        self.check_structure_response(
            self.get_touristiccontent_detail(self.content.pk),
            TOURISTIC_CONTENT_DETAIL_JSON_STRUCTURE
        )

    @override_settings(ONLY_EXTERNAL_PUBLIC_PDF=True)
    def test_touristiccontent_external_pdf(self):
        self.check_structure_response(
            self.get_touristiccontent_detail(self.content.pk),
            TOURISTIC_CONTENT_DETAIL_JSON_STRUCTURE
        )

    def test_touristiccontent_list(self):
        """ Test Touristic content list access and structure """
        response = self.get_touristiccontent_list()
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()),
                         PAGINATED_JSON_STRUCTURE)

        # touristiccontent count is ok
        self.assertEqual(len(json_response.get('results')),
                         tourism_models.TouristicContent.objects.all().count())

    def test_touristiccontent_list_filter_distance(self):
        """ Test Touristic content list is filtered by reference point distance """
        geom_point_1 = Point(x=1.4464187622070312,
                             y=43.65147866566022, srid=4326)
        geom_point_1.transform(2154)
        tc_1 = tourism_factory.TouristicContentFactory(geom=geom_point_1)
        geom_point_2 = Point(x=1.435432434082031,
                             y=43.63682057801007, srid=4326)
        geom_point_2.transform(2154)
        tc_2 = tourism_factory.TouristicContentFactory(geom=geom_point_2)

        # test present if no filtering
        response = self.get_touristiccontent_list()
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        ids = [element['id'] for element in json_response['results']]
        self.assertIn(tc_1.pk, ids)
        self.assertIn(tc_2.pk, ids)

        # test present filtering < 110km
        response = self.get_touristiccontent_list({
            'dist': '110000',
            'point': f"{self.reference_point.x},{self.reference_point.y}",
        })

        json_response = response.json()
        ids = [element['id'] for element in json_response['results']]
        self.assertIn(tc_1.pk, ids)
        self.assertIn(tc_2.pk, ids)

        # test present filtering < 50km
        response = self.get_touristiccontent_list({
            'dist': '50000',
            'point': f"{self.reference_point.x},{self.reference_point.y}",
        })

        json_response = response.json()
        ids = [element['id'] for element in json_response['results']]
        self.assertNotIn(tc_1.pk, ids)
        self.assertNotIn(tc_2.pk, ids)

    def test_touristiccontent_near_trek(self):
        response = self.get_touristiccontent_list({'near_trek': self.treks[0].pk})
        self.assertEqual(len(response.json()['results']), 2)

    def test_touristiccontent_categories(self):
        response = self.get_touristiccontent_list({'categories': self.content.category.pk})
        self.assertEqual(len(response.json()['results']), 1)

    def test_touristiccontent_types(self):
        tct1 = tourism_factory.TouristicContentType1Factory()
        response = self.get_touristiccontent_list({'types': self.content.type1.all()[0].pk})
        self.assertEqual(len(response.json()['results']), 1)
        response = self.get_touristiccontent_list({'types': self.content.type2.all()[0].pk})
        self.assertEqual(len(response.json()['results']), 1)
        response = self.get_touristiccontent_list({
            'types': '{},{}'.format(self.content.type1.all()[0].pk, self.content.type2.all()[0].pk)
        })
        self.assertEqual(len(response.json()['results']), 1)
        response = self.get_touristiccontent_list({'types': '{},{}'.format(self.content.type1.all()[0].pk, tct1.pk)})
        self.assertEqual(len(response.json()['results']), 1)
        response = self.get_touristiccontent_list({'types': '{},{}'.format(self.content.type2.all()[0].pk, tct1.pk)})
        self.assertEqual(len(response.json()['results']), 0)

    def test_touristiccontent_city(self):
        response = self.get_touristiccontent_list({'cities': self.city.pk})
        self.assertEqual(len(response.json()['results']), 2)

    def test_touristiccontent_inexistant_city(self):
        response = self.get_touristiccontent_list({'cities': '99999'})
        self.assertEqual(len(response.json()['results']), 0)

    def test_touristiccontent_district(self):
        response = self.get_touristiccontent_list({'districts': self.district.pk})
        self.assertEqual(len(response.json()['results']), 2)

    def test_touristiccontent_inexistant_district(self):
        response = self.get_touristiccontent_list({'districts': 99999})
        self.assertEqual(len(response.json()['results']), 0)

    def test_touristiccontent_structure(self):
        response = self.get_touristiccontent_list({'structures': self.content.structure.pk})
        self.assertEqual(len(response.json()['results']), 2)

    def test_touristiccontent_theme(self):
        response = self.get_touristiccontent_list({'themes': self.content.themes.all()[0].pk})
        self.assertEqual(len(response.json()['results']), 1)

    def test_touristiccontent_portal(self):
        response = self.get_touristiccontent_list({'portals': self.content.portal.all()[0].pk})
        self.assertEqual(len(response.json()['results']), 1)

    def test_touristiccontent_q(self):
        response = self.get_touristiccontent_list({'q': 'Blah CT'})
        self.assertEqual(len(response.json()['results']), 2)

    def test_touristiccontent_detail_with_lang(self):
        response = self.get_touristiccontent_list({'language': 'en'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'][0]['pdf'],
                         f'http://testserver/api/en/touristiccontents/{self.content.pk}/touristic-content.pdf')

    def test_labels_list(self):
        self.check_number_elems_response(
            self.get_label_list(),
            common_models.Label
        )

    def test_labels_detail(self):
        self.check_structure_response(
            self.get_label_detail(self.label.pk),
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

    def test_reservationsystem_list_filter(self):
        response = self.get_reservationsystem_list({'portals': self.portal.pk})
        # Two results : one reservationsystem associated with content2 and the other with trek[0]
        self.assertEquals(len(response.json()['results']), 2)

    def test_reservationsystem_detail(self):
        self.check_structure_response(
            self.get_reservationsystem_detail(self.reservation_system.pk),
            RESERVATION_SYSTEM_PROPERTIES_JSON_STRUCTURE
        )

    def test_site_list(self):
        self.check_number_elems_response(
            self.get_site_list(),
            outdoor_models.Site
        )

    def test_site_detail(self):
        self.check_structure_response(
            self.get_site_detail(self.site.pk),
            SITE_PROPERTIES_JSON_STRUCTURE
        )

    def test_site_list_filters(self):
        response = self.get_site_list({
            'q': 'test string'
        })
        #  test response code
        self.assertEqual(response.status_code, 200)

    def test_course_list(self):
        self.check_number_elems_response(
            self.get_course_list(),
            outdoor_models.Course
        )

    def test_course_detail(self):
        self.check_structure_response(
            self.get_course_detail(self.course.pk),
            COURSE_PROPERTIES_JSON_STRUCTURE
        )

    def test_course_list_filters(self):
        response = self.get_course_list({
            'q': 'test string'
        })
        #  test response code
        self.assertEqual(response.status_code, 200)

    def test_outdoorpractice_list(self):
        self.check_number_elems_response(
            self.get_outdoorpractice_list(),
            outdoor_models.Practice
        )

    def test_outdoorpractice_detail(self):
        self.check_structure_response(
            self.get_outdoorpractice_detail(self.site.practice.pk),
            OUTDOORPRACTICE_PROPERTIES_JSON_STRUCTURE
        )

    def test_sitetype_list(self):
        self.check_number_elems_response(
            self.get_sitetype_list(),
            outdoor_models.SiteType
        )

    def test_sitetype_detail(self):
        self.check_structure_response(
            self.get_sitetype_detail(self.site.type.pk),
            SITETYPE_PROPERTIES_JSON_STRUCTURE
        )

    def test_sensitivearea_list(self):
        self.check_number_elems_response(
            self.get_sensitivearea_list(params={'period': 'any'}),
            sensitivity_models.SensitiveArea
        )
        # Test filters coverage
        response = self.get_sensitivearea_list({
            'trek': self.parent.id,
            'period': "1,2,3,10,11,12",
            'structure': self.structure.id,
            'practice': self.sensitivearea_practice.id,
        })
        self.assertEqual(response.status_code, 200)

    def test_sensitivearea_detail(self):
        self.check_structure_response(
            self.get_sensitivearea_detail(self.sensitivearea.pk, params={'period': 'any'}),
            SENSITIVE_AREA_PROPERTIES_JSON_STRUCTURE
        )

    def test_sensitivearea_practice_list(self):
        self.check_number_elems_response(
            self.get_sensitiveareapractice_list(),
            sensitivity_models.SportPractice
        )

    def test_sensitivearea_practice_detail(self):
        self.check_structure_response(
            self.get_sensitiveareapractice_detail(self.sensitivearea_practice.pk),
            sorted(['name', 'id'])
        )

    def test_sensitivearea_species_list(self):
        self.check_number_elems_response(
            self.get_sensitiveareaspecies_list(),
            sensitivity_models.Species
        )

    def test_sensitivearea_species_detail(self):
        self.check_structure_response(
            self.get_sensitiveareaspecies_detail(self.sensitivearea_species.pk),
            SENSITIVE_AREA_SPECIES_PROPERTIES_JSON_STRUCTURE
        )

    def test_config(self):
        response = self.get_config()
        self.assertEqual(response.status_code, 200)

        json_response = response.json()
        self.assertEqual(sorted(json_response.keys()), ['bbox'])

    def test_organism_list(self):
        self.check_number_elems_response(
            self.get_organism_list(),
            common_models.Organism
        )

    def test_organism_detail(self):
        self.check_structure_response(
            self.get_organism_detail(self.organism.pk),
            ORGANISM_PROPERTIES_JSON_STRUCTURE
        )


class APIAccessAdministratorTestCase(BaseApiTest):
    """
    TestCase for administrator API profile
    """
    @classmethod
    def setUpTestData(cls):
        #  created user
        cls.administrator = SuperUserFactory()
        BaseApiTest.setUpTestData()

    def login(self):
        """
        Override base class login method, used before all function request 'get_api_element'
        """
        self.client.force_login(self.administrator)

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
        response = self.client.get('/api/v2/?format=openapi')
        self.assertContains(response, 'Filter by a bounding box formatted like W-lng,S-lat,E-lng,N-lat (WGS84).')
        self.assertContains(response, 'Set language for translation. Can be all or a two-letters language code.')
        self.assertContains(response, 'Filter by minimum difficulty level (id).')
        self.assertContains(response, 'Reference point to compute distance (WGS84). Example: lng,lat.')
        self.assertContains(response, 'Filter by one or more practice id, comma-separated.')

    def test_swagger_ui(self):
        response = self.client.get('/api/v2/')
        self.assertContains(response, 'swagger')


class RatingScaleTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.practice1 = outdoor_factory.PracticeFactory()
        cls.practice2 = outdoor_factory.PracticeFactory()
        cls.scale1 = outdoor_factory.RatingScaleFactory(name='AAA', practice=cls.practice1)
        cls.scale2 = outdoor_factory.RatingScaleFactory(name='AAA', practice=cls.practice2)
        cls.scale3 = outdoor_factory.RatingScaleFactory(name='BBB', practice=cls.practice2)

    def test_list(self):
        response = self.client.get('/api/v2/outdoor_ratingscale/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'count': 3,
            'next': None,
            'previous': None,
            'results': [{
                'id': self.scale1.pk,
                'name': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
                'practice': self.practice1.pk,
            }, {
                'id': self.scale2.pk,
                'name': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
                'practice': self.practice2.pk,
            }, {
                'id': self.scale3.pk,
                'name': {'en': 'BBB', 'es': None, 'fr': None, 'it': None},
                'practice': self.practice2.pk,
            }]
        })

    def test_detail(self):
        response = self.client.get('/api/v2/outdoor_ratingscale/{}/'.format(self.scale1.pk))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'id': self.scale1.pk,
            'name': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
            'practice': self.practice1.pk,
        })

    def test_filter_q(self):
        response = self.client.get('/api/v2/outdoor_ratingscale/?q=A')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for scale in response.json()['results']:
            self.assertEqual(scale['name']['en'], 'AAA')

    def test_filter_practice(self):
        response = self.client.get('/api/v2/outdoor_ratingscale/?practices={}'.format(self.practice2.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for scale in response.json()['results']:
            self.assertEqual(scale['practice'], self.practice2.pk)


class RatingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.scale1 = outdoor_factory.RatingScaleFactory(name='BBB')
        cls.scale2 = outdoor_factory.RatingScaleFactory(name='AAA')
        cls.rating1 = outdoor_factory.RatingFactory(name='AAA', scale=cls.scale1)
        cls.rating2 = outdoor_factory.RatingFactory(name='AAA', scale=cls.scale2)
        cls.rating3 = outdoor_factory.RatingFactory(name='BBB', scale=cls.scale2)

    def test_list(self):
        response = self.client.get('/api/v2/outdoor_rating/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'count': 3,
            'next': None,
            'previous': None,
            'results': [{
                'color': '',
                'description': {'en': None, 'es': None, 'fr': None, 'it': None},
                'id': self.rating1.pk,
                'name': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
                'order': None,
                'scale': self.scale1.pk,
            }, {
                'color': '',
                'description': {'en': None, 'es': None, 'fr': None, 'it': None},
                'id': self.rating2.pk,
                'name': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
                'order': None,
                'scale': self.scale2.pk,
            }, {
                'color': '',
                'description': {'en': None, 'es': None, 'fr': None, 'it': None},
                'id': self.rating3.pk,
                'name': {'en': 'BBB', 'es': None, 'fr': None, 'it': None},
                'order': None,
                'scale': self.scale2.pk,
            }]
        })

    def test_detail(self):
        response = self.client.get('/api/v2/outdoor_rating/{}/'.format(self.rating1.pk))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'id': self.rating1.pk,
            'color': '',
            'description': {'en': None, 'es': None, 'fr': None, 'it': None},
            'name': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
            'order': None,
            'scale': self.scale1.pk,
        })

    def test_filter_q(self):
        response = self.client.get('/api/v2/outdoor_rating/?q=BBB')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for rating in response.json()['results']:
            self.assertNotEqual(rating['name']['en'] == 'BBB', rating['scale'] == self.scale1.pk)

    def test_filter_scale(self):
        response = self.client.get('/api/v2/outdoor_rating/?scale={}'.format(self.scale2.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for rating in response.json()['results']:
            self.assertEqual(rating['scale'], self.scale2.pk)


class FlatPageTestCase(TestCase):
    maxDiff = None

    @classmethod
    def setUpTestData(cls):
        cls.source = common_factory.RecordSourceFactory()
        cls.portal = common_factory.TargetPortalFactory()
        cls.page1 = flatpages_factory.FlatPageFactory(
            title='AAA', published=True, order=2, target='web', content='Blah',
            sources=[cls.source], portals=[cls.portal]
        )
        cls.page2 = flatpages_factory.FlatPageFactory(
            title='BBB', published=True, order=1, target='mobile', content='Blbh'
        )

    def test_list(self):
        response = self.client.get('/api/v2/flatpage/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'count': 2,
            'next': None,
            'previous': None,
            'results': [{
                'id': self.page2.pk,
                'title': {'en': 'BBB', 'es': None, 'fr': None, 'it': None},
                'content': {'en': 'Blbh', 'es': None, 'fr': None, 'it': None},
                'external_url': '',
                'order': 1,
                'portal': [],
                'published': {'en': True, 'es': False, 'fr': False, 'it': False},
                'source': [],
                'target': 'mobile',
                'attachments': [],
            }, {
                'id': self.page1.pk,
                'title': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
                'content': {'en': 'Blah', 'es': None, 'fr': None, 'it': None},
                'external_url': '',
                'order': 2,
                'portal': [self.portal.pk],
                'published': {'en': True, 'es': False, 'fr': False, 'it': False},
                'source': [self.source.pk],
                'target': 'web',
                'attachments': [],
            }]
        })

    def test_detail(self):
        response = self.client.get('/api/v2/flatpage/{}/'.format(self.page1.pk))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'id': self.page1.pk,
            'title': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
            'content': {'en': 'Blah', 'es': None, 'fr': None, 'it': None},
            'external_url': '',
            'order': 2,
            'portal': [self.portal.pk],
            'published': {'en': True, 'es': False, 'fr': False, 'it': False},
            'source': [self.source.pk],
            'target': 'web',
            'attachments': [],
        })

    def test_filter_q(self):
        response = self.client.get('/api/v2/flatpage/?q=BB')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['title']['en'], 'BBB')

    def test_filter_targets(self):
        response = self.client.get('/api/v2/flatpage/?targets=web')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['title']['en'], 'AAA')

    def test_filter_sources(self):
        response = self.client.get('/api/v2/flatpage/?sources={}'.format(self.source.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['title']['en'], 'AAA')

    def test_filter_portals(self):
        response = self.client.get('/api/v2/flatpage/?portals={}'.format(self.portal.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['title']['en'], 'AAA')


class ReportStatusTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.status1 = feedback_factory.ReportStatusFactory(label="A transmettre")
        cls.status2 = feedback_factory.ReportStatusFactory(label="En cours de traitement")
        cls.activity1 = feedback_factory.ReportActivityFactory(label="Horse-riding")
        cls.activity2 = feedback_factory.ReportActivityFactory(label="Climbing")
        cls.magnitude1 = feedback_factory.ReportProblemMagnitudeFactory(label="Easy")
        cls.magnitude2 = feedback_factory.ReportProblemMagnitudeFactory(label="Hardcore")
        cls.category1 = feedback_factory.ReportCategoryFactory(label="Conflict")
        cls.category2 = feedback_factory.ReportCategoryFactory(label="Literring")

    def test_status_list(self):
        response = self.client.get('/api/v2/feedback_status/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.status1.pk,
                    "label": {'en': "A transmettre", 'es': None, 'fr': None, 'it': None},
                },
                {
                    "id": self.status2.pk,
                    "label": {'en': "En cours de traitement", 'es': None, 'fr': None, 'it': None},
                }]
        })

    def test_activity_list(self):
        response = self.client.get('/api/v2/feedback_activity/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.activity1.pk,
                    "label": {'en': "Horse-riding", 'es': None, 'fr': None, 'it': None},
                },
                {
                    "id": self.activity2.pk,
                    "label": {'en': "Climbing", 'es': None, 'fr': None, 'it': None},
                }]
        })

    def test_magnitude_list(self):
        response = self.client.get('/api/v2/feedback_magnitude/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.magnitude1.pk,
                    "label": {'en': "Easy", 'es': None, 'fr': None, 'it': None},
                },
                {
                    "id": self.magnitude2.pk,
                    "label": {'en': "Hardcore", 'es': None, 'fr': None, 'it': None},
                }]
        })

    def test_category_list(self):
        response = self.client.get('/api/v2/feedback_category/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "count": 2,
            "next": None,
            "previous": None,
            "results": [
                {
                    "id": self.category1.pk,
                    "label": {'en': "Conflict", 'es': None, 'fr': None, 'it': None},
                },
                {
                    "id": self.category2.pk,
                    "label": {'en': "Literring", 'es': None, 'fr': None, 'it': None},
                }]
        })


class TrekOrderingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trek1 = trek_factory.TrekFactory(name_fr="AAA", name_en='ABA', published_fr=True, published_en=True)
        cls.trek2 = trek_factory.TrekFactory(name_fr="ABA", name_en='BAA', published_fr=True, published_en=True)
        cls.trek3 = trek_factory.TrekFactory(name_fr="BAA", name_en="AAA", published_fr=True, published_en=True)
        cls.trek4 = trek_factory.TrekFactory(name_fr="CCC", name_en="CCC", published_fr=True, published_en=True)

    def test_order_fr(self):
        params = {'language': 'fr'}
        response = self.client.get(reverse('apiv2:trek-list'), params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'][0]['id'], self.trek1.pk)
        self.assertEqual(response.json()['results'][1]['id'], self.trek2.pk)
        self.assertEqual(response.json()['results'][2]['id'], self.trek3.pk)
        self.assertEqual(response.json()['results'][3]['id'], self.trek4.pk)

    def test_order_en(self):
        params = {'language': 'en'}
        response = self.client.get(reverse('apiv2:trek-list'), params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'][0]['id'], self.trek3.pk)
        self.assertEqual(response.json()['results'][1]['id'], self.trek1.pk)
        self.assertEqual(response.json()['results'][2]['id'], self.trek2.pk)
        self.assertEqual(response.json()['results'][3]['id'], self.trek4.pk)


class TouristicContentOrderingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tc1 = tourism_factory.TouristicContentFactory(name_fr="AAA", name_en='ABA', published_fr=True, published_en=True)
        cls.tc2 = tourism_factory.TouristicContentFactory(name_fr="ABA", name_en='BAA', published_fr=True, published_en=True)
        cls.tc3 = tourism_factory.TouristicContentFactory(name_fr="BAA", name_en="AAA", published_fr=True, published_en=True)
        cls.tc4 = tourism_factory.TouristicContentFactory(name_fr="CCC", name_en="CCC", published_fr=True, published_en=True)

    def test_order_fr(self):
        params = {'language': 'fr'}
        response = self.client.get(reverse('apiv2:touristiccontent-list'), params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'][0]['id'], self.tc1.pk)
        self.assertEqual(response.json()['results'][1]['id'], self.tc2.pk)
        self.assertEqual(response.json()['results'][2]['id'], self.tc3.pk)
        self.assertEqual(response.json()['results'][3]['id'], self.tc4.pk)

    def test_order_en(self):
        params = {'language': 'en'}
        response = self.client.get(reverse('apiv2:touristiccontent-list'), params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'][0]['id'], self.tc3.pk)
        self.assertEqual(response.json()['results'][1]['id'], self.tc1.pk)
        self.assertEqual(response.json()['results'][2]['id'], self.tc2.pk)
        self.assertEqual(response.json()['results'][3]['id'], self.tc4.pk)
