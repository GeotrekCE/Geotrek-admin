import datetime
from functools import partial
import json
import re
from unittest import skipIf, mock

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import (LineString, MultiLineString, MultiPoint,
                                     Point, Polygon)
from django.contrib.gis.geos.collections import GeometryCollection
from django.db import connection
from django.test import TestCase, RequestFactory, override_settings
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from mapentity.tests.factories import SuperUserFactory
from paperclip.models import random_suffix_regexp
from rest_framework.test import APITestCase, APIClient

from geotrek import __version__
from geotrek.api.v2.views.trekking import TrekViewSet
from geotrek.authent import models as authent_models
from geotrek.authent.tests import factories as authent_factory
from geotrek.authent.tests.factories import StructureFactory
from geotrek.common import models as common_models
from geotrek.common.models import Attachment, FileType
from geotrek.common.tests import factories as common_factory, TranslationResetMixin
from geotrek.common.utils.testdata import (get_dummy_uploaded_document,
                                           get_dummy_uploaded_file,
                                           get_dummy_uploaded_image, get_dummy_uploaded_image_svg)
from geotrek.core import models as path_models
from geotrek.core.tests import factories as core_factory
from geotrek.feedback import models as feedback_models
from geotrek.feedback.tests import factories as feedback_factory, factories as feedback_factories
from geotrek.flatpages.models import MenuItem, FlatPage
from geotrek.flatpages.tests import factories as flatpages_factory
from geotrek.flatpages.tests.factories import MenuItemFactory
from geotrek.infrastructure import models as infrastructure_models
from geotrek.infrastructure.tests import factories as infrastructure_factory
from geotrek.outdoor import models as outdoor_models
from geotrek.outdoor.tests import factories as outdoor_factory
from geotrek.sensitivity import models as sensitivity_models
from geotrek.sensitivity.models import SportPractice
from geotrek.sensitivity.tests import factories as sensitivity_factory
from geotrek.sensitivity.tests.factories import SensitiveAreaFactory, MultiPolygonSensitiveAreaFactory, \
    RegulatorySensitiveAreaFactory
from geotrek.signage import models as signage_models
from geotrek.signage.tests import factories as signage_factory
from geotrek.tourism import models as tourism_models
from geotrek.tourism.tests import factories as tourism_factory
from geotrek.trekking import models as trek_models
from geotrek.trekking.tests import factories as trek_factory
from geotrek.trekking.tests.base import TrekkingManagerTest
from geotrek.trekking.tests.factories import PracticeFactory
from geotrek.zoning import models as zoning_models
from geotrek.zoning.tests import factories as zoning_factory


PAGINATED_JSON_STRUCTURE = sorted([
    'count', 'next', 'previous', 'results',
])

PAGINATED_GEOJSON_STRUCTURE = sorted([
    'count', 'next', 'previous', 'features', 'type'
])

GEOJSON_COLLECTION_STRUCTURE = sorted([
    'features', 'type',
])

GEOJSON_STRUCTURE = sorted([
    'geometry',
    'type',
    'bbox',
    'properties'
])

TREK_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'access', 'accessibilities', 'accessibility_advice', 'accessibility_covering',
    'accessibility_exposure', 'accessibility_level', 'accessibility_signage', 'accessibility_slope',
    'accessibility_width', 'advice', 'advised_parking', 'altimetric_profile', 'ambiance', 'arrival', 'ascent',
    'attachments', 'attachments_accessibility', 'children', 'cities', 'create_datetime', 'departure', 'departure_geom',
    'descent', 'description', 'description_teaser', 'difficulty', 'departure_city',
    'disabled_infrastructure', 'districts', 'duration', 'elevation_area_url', 'elevation_svg_url', 'gear',
    'external_id', 'gpx', 'information_desks', 'kml', 'labels', 'length_2d',
    'length_3d', 'max_elevation', 'min_elevation', 'name', 'networks',
    'next', 'parents', 'parking_location', 'pdf', 'points_reference',
    'portal', 'practice', 'previous', 'public_transport', 'provider', 'published', 'ratings', 'ratings_description',
    'reservation_system', 'reservation_id', 'route', 'second_external_id', 'source', 'structure',
    'themes', 'update_datetime', 'url', 'uuid', 'view_points', 'web_links'
])

PATH_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'arrival', 'comfort', 'comments', 'departure', 'length_2d', 'length_3d', 'name',
    'networks', 'provider', 'source', 'stake', 'url', 'usages', 'uuid'])

TOUR_PROPERTIES_GEOJSON_STRUCTURE = sorted(TREK_PROPERTIES_GEOJSON_STRUCTURE + ['count_children', 'steps'])

POI_PROPERTIES_GEOJSON_STRUCTURE = sorted([
    'id', 'create_datetime', 'description', 'external_id',
    'name', 'attachments', 'published', 'provider', 'structure', 'type', 'type_label', 'type_pictogram',
    'update_datetime', 'url', 'uuid', 'view_points'
])

LABEL_ACCESSIBILITY_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label', 'pictogram'
])

TOURISTIC_CONTENT_CATEGORY_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label', 'order', 'pictogram', 'types'
])

TOURISTIC_CONTENT_DETAIL_JSON_STRUCTURE = sorted([
    'accessibility', 'approved', 'attachments', 'category', 'cities', 'contact', 'create_datetime', 'description',
    'description_teaser', 'departure_city', 'districts', 'email', 'external_id', 'geometry', 'id', 'label_accessibility', 'name', 'pdf',
    'portal', 'practical_info', 'provider', 'published', 'reservation_id', 'reservation_system',
    'source', 'structure', 'themes', 'types', 'update_datetime', 'url', 'uuid', 'website',
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

ACCESSIBILITY_LEVEL_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'name'
])

TARGET_PORTAL_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'name', 'website', 'title', 'description', 'facebook_id', 'facebook_image_url', 'facebook_image_height', 'facebook_image_width'
])

STRUCTURE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name'])

TREK_LABEL_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'advice', 'filter', 'name', 'pictogram'])

FILETYPE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'structure', 'type'])

INFORMATION_DESK_TYPE_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'label', 'pictogram'
])

INFORMATION_DESK_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'accessibility', 'description', 'email', 'label_accessibility', 'latitude', 'longitude',
    'municipality', 'name', 'phone', 'photo_url', 'provider', 'uuid',
    'postal_code', 'street', 'type', 'website'
])

SOURCE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name', 'pictogram', 'website'])

RESERVATION_SYSTEM_PROPERTIES_JSON_STRUCTURE = sorted(['name', 'id'])

SITE_PROPERTIES_JSON_STRUCTURE = sorted([
    'accessibility', 'advice', 'ambiance', 'attachments', 'children', 'children_uuids', 'cities', 'courses', 'courses_uuids', 'description',
    'description_teaser', 'districts', 'eid', 'geometry', 'id', 'information_desks', 'labels', 'managers', 'name', 'orientation', 'parent',
    'parent_uuid', 'period', 'portal', 'practice', 'provider', 'pdf', 'ratings', 'sector', 'source', 'structure', 'themes', 'type', 'url', 'uuid',
    'view_points', 'published', 'wind', 'web_links'
])

OUTDOORPRACTICE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name', 'sector', 'pictogram'])

OUTDOOR_SECTOR_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name'])

SITETYPE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name', 'practice'])

SENSITIVE_AREA_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'contact', 'create_datetime', 'description', 'elevation', 'geometry',
    'info_url', 'kml_url', 'openair_url', 'name', 'period', 'practices', 'provider',
    'published', 'species_id', 'structure', 'update_datetime', 'url', 'attachments',
    'rules'
])

SENSITIVE_AREA_SPECIES_PROPERTIES_JSON_STRUCTURE = sorted([
    'id', 'name', 'period01', 'period02', 'period03',
    'period04', 'period05', 'period06', 'period07',
    'period08', 'period09', 'period10', 'period11',
    'period12', 'practices', 'radius', 'url'
])

COURSE_PROPERTIES_JSON_STRUCTURE = sorted([
    'accessibility', 'advice', 'cities', 'description', 'districts', 'eid', 'equipment', 'geometry', 'height', 'id',
    'length', 'name', 'ratings', 'ratings_description', 'sites', 'sites_uuids', 'structure',
    'type', 'url', 'attachments', 'max_elevation', 'min_elevation', 'parents', 'parents_uuids', 'provider',
    'pdf', 'points_reference', 'published', 'children', 'children_uuids', 'duration', 'gear', 'uuid'
])

COURSETYPE_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name', 'practice'])

ORGANISM_PROPERTIES_JSON_STRUCTURE = sorted(['id', 'name'])

SERVICE_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'eid', 'geometry', 'provider', 'structure', 'type', 'uuid'
])

SERVICE_TYPE_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'name', 'practices', 'pictogram'
])

INFRASTRUCTURE_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'accessibility', 'attachments', 'condition', 'description', 'eid', 'geometry',
    'implantation_year', 'maintenance_difficulty', 'name', 'provider', 'structure',
    'type', 'usage_difficulty', 'uuid'
])

INFRASTRUCTURE_TYPE_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label', 'pictogram', 'structure', 'type'
])

INFRASTRUCTURE_CONDITION_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label', 'structure'
])

INFRASTRUCTURE_USAGE_DIFFICULTY_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label', 'structure'
])

INFRASTRUCTURE_MAINTENANCE_DIFFICULTY_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label', 'structure'
])

TOURISTIC_EVENT_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'accessibility', 'approved', 'attachments', 'begin_date', 'bookable', 'booking', 'cities', 'contact', 'create_datetime',
    'description', 'description_teaser', 'districts', 'duration', 'email', 'end_date', 'external_id', 'geometry',
    'meeting_point', 'start_time', 'meeting_time', 'end_time', 'name', 'organizer', 'organizers', 'organizers_id', 'capacity', 'pdf', 'place', 'portal',
    'practical_info', 'provider', 'published', 'source', 'speaker', 'structure', 'target_audience', 'themes',
    'type', 'update_datetime', 'url', 'uuid', 'website', 'cancelled', 'cancellation_reason', 'participant_number', 'price'
])

TOURISTIC_EVENT_PLACE_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'name', 'geometry'
])

TOURISTIC_EVENT_ORGANIZER_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label'
])

TOURISTIC_EVENT_TYPE_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'pictogram', 'type'
])

SIGNAGE_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'attachments', 'blades', 'code', 'condition', 'conditions', 'description', 'eid',
    'geometry', 'implantation_year', 'name', 'printed_elevation', 'sealing',
    'provider', 'structure', 'type', 'uuid'
])

SIGNAGE_TYPE_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label', 'pictogram', 'structure'
])

SIGNAGE_BLADE_COLOR_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label'
])

SIGNAGE_DIRECTION_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label'
])

SIGNAGE_SEALING_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label', 'structure'
])

SIGNAGE_BLADE_TYPE_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'label', 'structure'
])

HDVIEWPOINT_DETAIL_JSON_STRUCTURE = sorted([
    'id', 'annotations', 'author', 'create_datetime', 'geometry', 'legend', 'license',
    'metadata_url', 'picture_tiles_url', 'poi', 'site', 'title', 'trek', 'thumbnail_url', 'update_datetime', 'uuid'
])


class BaseApiTest(TestCase):
    """ Base TestCase for all API profiles """

    @classmethod
    def setUpTestData(cls):
        # This prevents the test APIAccessAnonymousTestCase.test_hdviewpoint_detail_content_poi not passing on some environments.
        # The root cause has not been investigated.
        ContentType.objects.clear_cache()

        cls.nb_treks = 15
        cls.organism = common_factory.OrganismFactory.create()
        cls.theme = common_factory.ThemeFactory.create()
        cls.network = trek_factory.TrekNetworkFactory.create()
        cls.rating = trek_factory.RatingFactory()
        cls.rating2 = trek_factory.RatingFactory()
        cls.label = common_factory.LabelFactory(id=23)
        cls.path = core_factory.PathFactory.create(geom=LineString((0, 0), (0, 10)))
        if settings.TREKKING_TOPOLOGY_ENABLED:
            cls.treks = trek_factory.TrekWithPOIsFactory.create_batch(cls.nb_treks, paths=[(cls.path, 0, 1)],
                                                                      geom=cls.path.geom)
        else:
            cls.treks = trek_factory.TrekFactory.create_batch(cls.nb_treks, geom=cls.path.geom)
            trek_factory.POIFactory.create_batch(cls.nb_treks, geom=Point(0, 4))
            trek_factory.POIFactory.create_batch(cls.nb_treks, geom=Point(0, 5))
        html_content_with_imgs = '<p>Some HTML content with images</p>' \
                                 '<img src="/media/upload/steep_descent.svg" alt="Descent">' \
                                 '<img src="https://testserver/media/upload/pedestre.svg" alt="" width="1848" height="1848">'
        cls.treks[0].description = html_content_with_imgs
        cls.treks[0].description_teaser = html_content_with_imgs
        cls.treks[0].ambiance = html_content_with_imgs
        cls.treks[0].save()
        cls.treks[0].themes.add(cls.theme)
        cls.treks[0].networks.add(cls.network)
        cls.treks[0].labels.add(cls.label)
        cls.treks[0].ratings.add(cls.rating)
        cls.treks[1].ratings.add(cls.rating2)
        cls.information_desk_type = tourism_factory.InformationDeskTypeFactory()
        cls.info_desk = tourism_factory.InformationDeskFactory(type=cls.information_desk_type)
        cls.treks[0].information_desks.add(cls.info_desk)
        common_factory.AttachmentFactory.create(content_object=cls.treks[0], attachment_file=get_dummy_uploaded_image())
        common_factory.AttachmentFactory.create(content_object=cls.treks[0], attachment_file=get_dummy_uploaded_file())
        common_factory.AttachmentFactory.create(content_object=cls.treks[0], attachment_file=get_dummy_uploaded_document())
        common_factory.AttachmentFactory(content_object=cls.treks[0], attachment_file='', attachment_video='https://www.youtube.com/embed/Jm3anSjly0Y?wmode=opaque')
        common_factory.AttachmentFactory(content_object=cls.treks[0], attachment_file='', attachment_video='', attachment_link='https://geotrek.fr/assets/img/logo.svg')
        common_factory.AttachmentFactory(content_object=cls.treks[0], attachment_file='', attachment_video='', attachment_link='')
        common_factory.AttachmentAccessibilityFactory(content_object=cls.treks[0])
        cls.treks[3].parking_location = None
        cls.treks[3].points_reference = MultiPoint([Point(0, 0), Point(1, 1)], srid=settings.SRID)
        cls.treks[3].save()
        cls.content = tourism_factory.TouristicContentFactory.create(published=True, geom='SRID=2154;POINT(0 0)')
        cls.content2 = tourism_factory.TouristicContentFactory.create(published=True, geom='SRID=2154;POINT(0 0)')
        cls.event = tourism_factory.TouristicEventFactory.create(published=True, geom='SRID=2154;POINT(0 0)')
        cls.city = zoning_factory.CityFactory(code='01000', geom='SRID=2154;MULTIPOLYGON(((-1 -1, -1 1, 1 1, 1 -1, -1 -1)))')
        cls.city2 = zoning_factory.CityFactory(code='02000', geom='SRID=2154;MULTIPOLYGON(((-1 -1, -1 1, 1 1, 1 -1, -1 -1)))')
        cls.district = zoning_factory.DistrictFactory(geom='SRID=2154;MULTIPOLYGON(((-1 -1, -1 1, 1 1, 1 -1, -1 -1)))')
        cls.district2 = zoning_factory.DistrictFactory(geom='SRID=2154;MULTIPOLYGON(((-1 -1, -1 1, 1 1, 1 -1, -1 -1)))')
        cls.accessibility = trek_factory.AccessibilityFactory()
        cls.accessibility_level = trek_factory.AccessibilityLevelFactory()
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
            cls.poi = trek_factory.POIFactory(paths=[(cls.treks[0].paths.first(), 0.5, 0.5)])
            poi_excluded = trek_factory.POIFactory(paths=[(cls.treks[0].paths.first(), 0.5, 0.5)])
        else:
            cls.poi = trek_factory.POIFactory(geom='SRID=2154;POINT(0 5)')
            poi_excluded = trek_factory.POIFactory(geom='SRID=2154;POINT(0 5)')
        cls.treks[0].pois_excluded.add(poi_excluded)
        cls.source = common_factory.RecordSourceFactory()
        cls.reservation_system = common_factory.ReservationSystemFactory()
        cls.treks[0].reservation_system = cls.reservation_system
        cls.site = outdoor_factory.SiteFactory(managers=[cls.organism])
        cls.site.pois_excluded.add(poi_excluded)
        cls.label_accessibility = tourism_factory.LabelAccessibilityFactory()
        cls.category = tourism_factory.TouristicContentCategoryFactory()
        cls.content2.category = cls.category
        cls.content2.label_accessibility = cls.label_accessibility
        cls.content2.save()
        cls.info_desk.label_accessibility = cls.label_accessibility
        cls.info_desk.save()
        cls.content2.portal.add(cls.portal)
        common_factory.FileTypeFactory.create(type='Topoguide')
        cls.filetype = common_factory.FileTypeFactory.create(type='Foo')
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
            accessibility_level=cls.accessibility_level
        )
        cls.parent.accessibilities.add(cls.accessibility)
        cls.parent.source.add(cls.source)
        cls.parent.themes.add(cls.theme2)
        cls.parent.networks.add(cls.network)
        cls.parent.save()
        # For unpublished treks we avoid to create new reservation system and routes
        cls.parent2 = trek_factory.TrekFactory.create(published=False, name='Parent2',
                                                      reservation_system=cls.reservation_system, route=cls.route,
                                                      accessibility_level=None)
        cls.child1 = trek_factory.TrekFactory.create(published=False, name='Child 1',
                                                     reservation_system=cls.reservation_system, route=cls.route,
                                                     accessibility_level=None)
        cls.child2 = trek_factory.TrekFactory.create(published=True, name='Child 2', accessibility_level=None)
        cls.child3 = trek_factory.TrekFactory.create(published=False, name='Child 3',
                                                     reservation_system=cls.reservation_system, route=cls.route,
                                                     accessibility_level=None)
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
        cls.coursetype = outdoor_factory.CourseTypeFactory()
        cls.course = outdoor_factory.CourseFactory(
            type=cls.coursetype,
            points_reference=MultiPoint(Point(12, 12))
        )
        cls.course.pois_excluded.add(poi_excluded)
        cls.course.parent_sites.set([cls.site])
        # create a reference point for distance filter (in 4326, Cahors city)
        cls.reference_point = Point(x=1.4388656616210938,
                                    y=44.448487178796235, srid=4326)
        cls.service_type = trek_factory.ServiceTypeFactory()
        cls.service_type_2 = trek_factory.ServiceTypeFactory(published=False)
        cls.service1 = trek_factory.ServiceFactory()
        cls.service = trek_factory.ServiceFactory(
            type=cls.service_type
        )
        cls.service_2 = trek_factory.ServiceFactory(
            type=cls.service_type_2
        )
        cls.infrastructure_type = infrastructure_factory.InfrastructureTypeFactory()
        cls.infrastructure_condition = infrastructure_factory.InfrastructureConditionFactory()
        cls.infrastructure_usagedifficulty = infrastructure_factory.InfrastructureUsageDifficultyLevelFactory()
        cls.infrastructure_maintenancedifficulty = infrastructure_factory.InfrastructureMaintenanceDifficultyLevelFactory()
        cls.infrastructure = infrastructure_factory.InfrastructureFactory(
            type=cls.infrastructure_type,
            usage_difficulty=cls.infrastructure_usagedifficulty,
            maintenance_difficulty=cls.infrastructure_maintenancedifficulty,
            condition=cls.infrastructure_condition,
            published=True
        )
        cls.bladetype = signage_factory.BladeTypeFactory(
        )
        cls.color = signage_factory.BladeColorFactory()
        cls.sealing = signage_factory.SealingFactory()
        cls.direction = signage_factory.BladeDirectionFactory()
        cls.bladetype = signage_factory.BladeFactory(
            color=cls.color,
            type=cls.bladetype,
            direction=cls.direction
        )
        cls.signagetype = signage_factory.SignageTypeFactory()
        cls.signage = signage_factory.SignageFactory(
            type=cls.signagetype,
            published=True
        )
        cls.sector = outdoor_factory.SectorFactory()
        cls.outdoor_practice = outdoor_factory.PracticeFactory(sector=cls.sector)
        cls.site2 = outdoor_factory.SiteFactory(practice=None)
        cls.site2.portal.set([cls.portal])
        cls.theme3 = common_factory.ThemeFactory()
        cls.site2.themes.add(cls.theme3)
        cls.label_3 = common_factory.LabelFactory()
        cls.site2.labels.add(cls.label_3)
        cls.hdviewpoint_trek = common_factory.HDViewPointFactory(
            content_object=cls.treks[0]
        )
        cls.hdviewpoint_poi = common_factory.HDViewPointFactory(
            content_object=cls.poi
        )
        cls.hdviewpoint_site = common_factory.HDViewPointFactory(
            content_object=cls.site
        )

    def check_number_elems_response(self, response, model):
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_response['results']), model.objects.count())

    def check_structure_response(self, response, structure):
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted(json_response.keys()), structure)

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

    def get_accessibility_level_list(self, params=None):
        return self.client.get(reverse('apiv2:accessibility-level-list'), params)

    def get_accessibility_detail(self, id_accessibility, params=None):
        return self.client.get(reverse('apiv2:accessibility-detail', args=(id_accessibility,)), params)

    def get_accessibility_level_detail(self, id_accessibility_level, params=None):
        return self.client.get(reverse('apiv2:accessibility-level-detail', args=(id_accessibility_level,)), params)

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

    def get_labelaccessibility_list(self, params=None):
        return self.client.get(reverse('apiv2:labelaccessibility-list', params))

    def get_labelaccessibility_detail(self, id_label_accessibility, params=None):
        return self.client.get(reverse('apiv2:labelaccessibility-detail', args=(id_label_accessibility,)), params)

    def get_label_list(self, params=None):
        return self.client.get(reverse('apiv2:label-list'), params)

    def get_label_detail(self, id_label, params=None):
        return self.client.get(reverse('apiv2:label-detail', args=(id_label,)), params)

    def get_filetype_list(self, params=None):
        return self.client.get(reverse('apiv2:filetype-list'), params)

    def get_filetype_detail(self, id_label, params=None):
        return self.client.get(reverse('apiv2:filetype-detail', args=(id_label,)), params)

    def get_informationdesk_list(self, params=None):
        return self.client.get(reverse('apiv2:informationdesk-list'), params)

    def get_informationdesk_detail(self, id_infodesk, params=None):
        return self.client.get(reverse('apiv2:informationdesk-detail', args=(id_infodesk,)), params)

    def get_informationdesk_type_list(self, params=None):
        return self.client.get(reverse('apiv2:informationdesktype-list'), params)

    def get_informationdesk_type_detail(self, id_infodesk_type, params=None):
        return self.client.get(reverse('apiv2:informationdesktype-detail', args=(id_infodesk_type,)), params)

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

    def get_touristicevent_list(self, params=None):
        return self.client.get(reverse('apiv2:touristicevent-list'), params)

    def get_touristicevent_detail(self, id_touristicevent, params=None):
        return self.client.get(reverse('apiv2:touristicevent-detail', args=(id_touristicevent,)), params)

    def get_touristiceventtype_list(self, params=None):
        return self.client.get(reverse('apiv2:touristiceventtype-list'), params)

    def get_touristiceventtype_detail(self, id_touristiceventtype, params=None):
        return self.client.get(reverse('apiv2:touristiceventtype-detail', args=(id_touristiceventtype,)), params)

    def get_touristiceventplace_list(self, params=None):
        return self.client.get(reverse('apiv2:touristiceventplace-list'), params)

    def get_touristiceventplace_detail(self, id_touristiceventplace, params=None):
        return self.client.get(reverse('apiv2:touristiceventplace-detail', args=(id_touristiceventplace,)), params)

    def get_touristiceventorganizer_list(self, params=None):
        return self.client.get(reverse('apiv2:touristiceventorganizer-list'), params)

    def get_touristiceventorganizer_detail(self, id_touristiceventorganizer, params=None):
        return self.client.get(reverse('apiv2:touristiceventorganizer-detail', args=(id_touristiceventorganizer,)), params)

    def get_servicetype_list(self, params=None):
        return self.client.get(reverse('apiv2:servicetype-list'), params)

    def get_service_list(self, params=None):
        return self.client.get(reverse('apiv2:service-list'), params)

    def get_servicetype_detail(self, id_servicetype, params=None):
        return self.client.get(reverse('apiv2:servicetype-detail', args=(id_servicetype,)), params)

    def get_service_detail(self, id_service, params=None):
        return self.client.get(reverse('apiv2:service-detail', args=(id_service,)), params)

    def get_coursetype_list(self, params=None):
        return self.client.get(reverse('apiv2:coursetype-list'), params)

    def get_coursetype_detail(self, id_coursetype, params=None):
        return self.client.get(reverse('apiv2:coursetype-detail', args=(id_coursetype,)), params)

    def get_infrastructuretype_detail(self, id_infrastructuretype, params=None):
        return self.client.get(reverse('apiv2:infrastructure-type-detail', args=(id_infrastructuretype,)), params)

    def get_infrastructuretype_list(self, params=None):
        return self.client.get(reverse('apiv2:infrastructure-type-list'), params)

    def get_infrastructure_list(self, params=None):
        return self.client.get(reverse('apiv2:infrastructure-list'), params)

    def get_infrastructure_detail(self, id_infrastructure, params=None):
        return self.client.get(reverse('apiv2:infrastructure-detail', args=(id_infrastructure,)), params)

    def get_infrastructurecondition_list(self, params=None):
        return self.client.get(reverse('apiv2:infrastructure-condition-list'), params)

    def get_infrastructurecondition_detail(self, id_infrastructurecondition, params=None):
        return self.client.get(reverse('apiv2:infrastructure-condition-detail', args=(id_infrastructurecondition,)), params)

    def get_infrastructuremaintenancedifficulty_list(self, params=None):
        return self.client.get(reverse('apiv2:infrastructure-maintenance-difficulty-list'), params)

    def get_infrastructuremaintenancedifficulty_detail(self, id_infrastructuremaintenancedifficulty, params=None):
        return self.client.get(reverse('apiv2:infrastructure-maintenance-difficulty-detail', args=(id_infrastructuremaintenancedifficulty,)), params)

    def get_infrastructureusagedifficulty_list(self, params=None):
        return self.client.get(reverse('apiv2:infrastructure-usage-difficulty-list'), params)

    def get_infrastructureusagedifficulty_detail(self, id_infrastructureusagedifficulty, params=None):
        return self.client.get(reverse('apiv2:infrastructure-usage-difficulty-detail', args=(id_infrastructureusagedifficulty,)), params)

    def get_signage_detail(self, id_signage, params=None):
        return self.client.get(reverse('apiv2:signage-detail', args=(id_signage,)), params)

    def get_signage_list(self, params=None):
        return self.client.get(reverse('apiv2:signage-list'), params)

    def get_signagetype_list(self, params=None):
        return self.client.get(reverse('apiv2:signage-type-list'), params)

    def get_signagetype_detail(self, id_signagetype, params=None):
        return self.client.get(reverse('apiv2:signage-type-detail', args=(id_signagetype,)), params)

    def get_signagebladetype_list(self, params=None):
        return self.client.get(reverse('apiv2:signage-blade-type-list'), params)

    def get_signagebladetype_detail(self, id_signagebladetype, params=None):
        return self.client.get(reverse('apiv2:signage-blade-type-detail', args=(id_signagebladetype,)), params)

    def get_signagesealing_list(self, params=None):
        return self.client.get(reverse('apiv2:signage-sealing-list'), params)

    def get_signagesealing_detail(self, id_signagesealing, params=None):
        return self.client.get(reverse('apiv2:signage-sealing-detail', args=(id_signagesealing,)), params)

    def get_signagecolor_list(self, params=None):
        return self.client.get(reverse('apiv2:signage-color-list'), params)

    def get_signagecolor_detail(self, id_signagecolor, params=None):
        return self.client.get(reverse('apiv2:signage-color-detail', args=(id_signagecolor,)), params)

    def get_signagedirection_list(self, params=None):
        return self.client.get(reverse('apiv2:signage-direction-list'), params)

    def get_signagedirection_detail(self, id_signagedirection, params=None):
        return self.client.get(reverse('apiv2:signage-direction-detail', args=(id_signagedirection,)), params)

    def get_sector_list(self, params=None):
        return self.client.get(reverse('apiv2:outdoor-sector-list'), params)

    def get_sector_detail(self, id_sector, params=None):
        return self.client.get(reverse('apiv2:outdoor-sector-detail', args=(id_sector,)), params)

    def get_hdviewpoint_list(self, params=None):
        return self.client.get(reverse('apiv2:hdviewpoint-list'), params)

    def get_hdviewpoint_detail(self, id_hdviewpoint, params=None):
        return self.client.get(reverse('apiv2:hdviewpoint-detail', args=(id_hdviewpoint,)), params)


class NoPaginationTestCase(BaseApiTest):
    """
    Integration tests for disabled pagination.
    """

    def setUp(self):
        self.factory = RequestFactory()

    def test_json_no_page(self):
        request = self.factory.get(
            reverse("apiv2:trek-list"),
            {
                "no_page": "true",
            }
        )
        response = TrekViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)
        self.assertIsInstance(response.data[0], dict)
        self.assertEqual(
            len(response.data[0].get("geometry").get("coordinates")[0]),
            3,
        )

    def test_geojson_no_page(self):
        request = self.factory.get(
            reverse("apiv2:trek-list"),
            {
                "no_page": "true",
                "format": "geojson",
            }
        )
        response = TrekViewSet.as_view({"get": "list"})(request)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, dict)
        self.assertEqual(sorted(response.data.keys()), GEOJSON_COLLECTION_STRUCTURE)
        self.assertEqual(
            len(response.data.get("features")), self.nb_treks, response.data
        )
        self.assertEqual(
            sorted(response.data.get("features")[0].get("properties").keys()),
            TREK_PROPERTIES_GEOJSON_STRUCTURE,
        )


class APIAccessAnonymousTestCase(BaseApiTest):
    """ TestCase for anonymous API profile """

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
            'accessibility_level': self.accessibility_level.pk,
            'themes': self.theme2.pk,
            'portals': self.portal.pk,
            'labels': '23',
            'routes': '68',
            'practices': '1',
            'ratings': self.rating.pk,
            'q': 'test string',
        })
        #  test response code
        self.assertEqual(response.status_code, 200)

        # json collection structure is ok
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_theme_filter(self):
        response = self.get_trek_list({'themes': self.theme2.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        response = self.get_trek_list({'themes': 0})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_portal_filter(self):
        response = self.get_trek_list({'portals': self.portal.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        response = self.get_trek_list({'portals': 0})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_ids_filter(self):
        response = self.get_trek_list({'ids': f"{self.treks[0].pk},{self.treks[1].pk}"})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 2)

        response = self.get_trek_list({'ids': 99999})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_label_filter(self):
        response = self.get_trek_list({'labels': self.label.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        response = self.get_trek_list({'labels': 0})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_labels_exclude_filter(self):
        response = self.get_trek_list({'labels_exclude': self.label.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 18)

        trek = trek_factory.TrekFactory.create()
        label = common_factory.LabelFactory.create()
        trek.labels.add(label, self.label)

        response = self.get_trek_list({'labels_exclude': self.label.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 18)

        trek = trek_factory.TrekFactory.create()
        label_2 = common_factory.LabelFactory.create()
        trek.labels.add(label, label_2)

        response = self.get_trek_list({'labels_exclude': f'{self.label.pk},{label.pk}'})
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 18)

        response = self.get_trek_list({'labels_exclude': label_2.pk})
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 20)

    def test_trek_city_filter(self):
        path = core_factory.PathFactory.create(geom=LineString((-10, -9), (-9, -9)))
        city3 = zoning_factory.CityFactory(code='03000',
                                           geom='SRID=2154;MULTIPOLYGON(((-10 -10, -10 -9, -9 -9, -9 -10, -10 -10)))')
        if settings.TREKKING_TOPOLOGY_ENABLED:
            trek_factory.TrekFactory.create(paths=[(path, 0, 1)])
        else:
            trek_factory.TrekFactory.create(geom='SRID=2154;LINESTRING(-10 -9, -9 -9)')
        response = self.get_trek_list({'cities': city3.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        response = self.get_trek_list({'cities': 0})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_district_filter(self):
        path = core_factory.PathFactory.create(geom=LineString((-10, -9), (-9, -9)))
        dist3 = zoning_factory.DistrictFactory(geom='SRID=2154;MULTIPOLYGON(((-10 -10, -10 -9, -9 -9, '
                                                    '-9 -10, -10 -10)))')
        if settings.TREKKING_TOPOLOGY_ENABLED:
            trek_factory.TrekFactory.create(paths=[(path, 0, 1)])
        else:
            trek_factory.TrekFactory.create(geom='SRID=2154;LINESTRING(-10 -9, -9 -9)')
        response = self.get_trek_list({'districts': dist3.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        response = self.get_trek_list({'districts': 0})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_structure_filter(self):
        response = self.get_trek_list({'structures': self.structure.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        response = self.get_trek_list({'cities': 0})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_practice_filter(self):
        response = self.get_trek_list({'practices': self.practice.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        response = self.get_trek_list({'practices': 0})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_accessibility_level_filter(self):
        response = self.get_trek_list({'accessibility_level': self.accessibility_level.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        response = self.get_trek_list({'accessibility_level': 0})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_routes_filter(self):
        response = self.get_trek_list({'routes': self.route.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        response = self.get_trek_list({'routes': 0})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_trek_ratings_filter(self):
        response = self.get_trek_list({'ratings': self.rating.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 1)

        response = self.get_trek_list({'ratings': 0})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 0)

    def test_version_route(self):
        response = self.client.get("/api/v2/version")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'version': __version__})

    @override_settings(DEBUG=False)
    def test_handle_404_route(self):
        response = self.client.get("/api/v2/x")
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'page': 'does not exist'})

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

    def test_trek_list_filter_in_bbox(self):
        """ Test Trek list is filtered by bbox param """
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
        trek_toulouse.geom.buffer(10)
        trek_toulouse.geom.transform(4326)
        xmin, ymin, xmax, ymax = trek_toulouse.geom.extent

        # test pois is in bbox filter
        response = self.get_trek_list({
            'in_bbox': f'{xmin},{ymin},{xmax},{ymax}',
        })

        # json collection structure is ok
        json_response = response.json()
        ids_treks = [element['id'] for element in json_response['results']]
        self.assertIn(trek_toulouse.pk, ids_treks)

        # test trek is not in distance filter (< 50km)
        response = self.get_trek_list({
            'in_bbox': f'{0.0},{0.0},{1.0},{1.0}',
        })
        # json collection structure is ok
        json_response = response.json()
        ids_treks = [element['id'] for element in json_response['results']]
        self.assertNotIn(trek_toulouse.pk, ids_treks)

    def test_trek_list_filtered_by_near_trek(self):
        trek = self.treks[0]

        response = self.get_trek_list({"near_trek": trek.pk})

        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response["count"], 16)

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

    def test_trek_district(self):
        response = self.get_trek_list({'districts': self.district.pk})
        self.assertEqual(len(response.json()['results']), 17)

    def test_trek_cities(self):
        response = self.get_trek_list({'cities': f"{self.city.pk},{self.city2.pk}"})
        self.assertEqual(len(response.json()['results']), 17)

    def test_trek_districts(self):
        response = self.get_trek_list({'districts': f"{self.district.pk},{self.district2.pk}"})
        self.assertEqual(len(response.json()['results']), 17)

    def test_trek_ratings(self):
        response = self.get_trek_list({'ratings': f"{self.rating.pk},{self.rating2.pk}"})
        self.assertEqual(len(response.json()['results']), 2)

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

    def test_trek_detail_img_src_are_completed_in_descriptions(self):
        response = self.get_trek_detail(self.treks[0].pk)
        self.assertEqual(response.status_code, 200)
        # Note that tags are sorted and the HTML format slightly changed during the "src" processing.
        expected_description = '<p>Some HTML content with images</p>'\
                               '<img alt="Descent" src="http://testserver/media/upload/steep_descent.svg"/>'\
                               '<img alt="" height="1848" src="https://testserver/media/upload/pedestre.svg" width="1848"/>'
        self.assertEqual(response.json()['description']['en'], expected_description)
        self.assertEqual(response.json()['description_teaser']['en'], expected_description)
        self.assertEqual(response.json()['ambiance']['en'], expected_description)

        # Same test requesting a specific language
        response = self.get_trek_detail(self.treks[0].pk, params={'language': 'en'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['description'], expected_description)
        self.assertEqual(response.json()['description_teaser'], expected_description)
        self.assertEqual(response.json()['ambiance'], expected_description)
        self.assertEqual(response.json()['view_points'][0]['geometry'], {'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]})

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
        self.assertContains(response, self.theme3.label)

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

    def test_sector_detail(self):
        self.check_structure_response(
            self.get_sector_detail(self.sector.pk),
            OUTDOOR_SECTOR_PROPERTIES_JSON_STRUCTURE
        )

    def test_sector_list(self):
        self.check_number_elems_response(
            self.get_sector_list(),
            outdoor_models.Sector
        )

    def test_hdviewpoint_detail(self):
        self.check_structure_response(
            self.get_hdviewpoint_detail(self.hdviewpoint_trek.pk),
            HDVIEWPOINT_DETAIL_JSON_STRUCTURE
        )

    def test_hdviewpoint_list(self):
        self.check_number_elems_response(
            self.get_hdviewpoint_list(),
            common_models.HDViewPoint
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

    def test_accessibility_level_list(self):
        self.check_number_elems_response(
            self.get_accessibility_level_list(),
            trek_models.AccessibilityLevel
        )

    def test_accessibility_detail(self):
        self.check_structure_response(
            self.get_accessibility_detail(self.accessibility.pk),
            ACCESSIBILITY_PROPERTIES_JSON_STRUCTURE
        )

    def test_accessibility_level_detail(self):
        self.check_structure_response(
            self.get_accessibility_level_detail(self.accessibility_level.pk),
            ACCESSIBILITY_LEVEL_PROPERTIES_JSON_STRUCTURE
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
        self.assertEqual(len(response.json()['results']), 1)

    def test_structure_detail(self):
        self.check_structure_response(
            self.get_structure_detail(self.structure.pk),
            STRUCTURE_PROPERTIES_JSON_STRUCTURE
        )

    def test_service_list(self):
        response = self.get_service_list()
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        services = trek_models.Service.objects.all()
        self.assertEqual(len(json_response['results']), services.count() - 1, services.filter(type__published=True).count())

    def test_service_detail(self):
        self.check_structure_response(
            self.get_service_detail(self.service.pk),
            SERVICE_DETAIL_JSON_STRUCTURE
        )

    def test_infrastructure_list(self):
        self.check_number_elems_response(
            self.get_infrastructure_list(),
            infrastructure_models.Infrastructure
        )

    def test_infrastructure_detail(self):
        self.check_structure_response(
            self.get_infrastructure_detail(self.infrastructure.pk),
            INFRASTRUCTURE_DETAIL_JSON_STRUCTURE
        )

    def test_infrastructuretype_list(self):
        self.check_number_elems_response(
            self.get_infrastructuretype_list(),
            infrastructure_models.InfrastructureType
        )

    def test_infrastructuretype_detail(self):
        self.check_structure_response(
            self.get_infrastructuretype_detail(self.infrastructure_type.pk),
            INFRASTRUCTURE_TYPE_DETAIL_JSON_STRUCTURE
        )

    def test_infrastructurecondition_list(self):
        self.check_number_elems_response(
            self.get_infrastructurecondition_list(),
            infrastructure_models.InfrastructureCondition
        )

    def test_infrastructurecondition_detail(self):
        self.check_structure_response(
            self.get_infrastructurecondition_detail(self.infrastructure_condition.pk),
            INFRASTRUCTURE_CONDITION_DETAIL_JSON_STRUCTURE
        )

    def test_infrastructuremaintenancedifficulty_list(self):
        self.check_number_elems_response(
            self.get_infrastructuremaintenancedifficulty_list(),
            infrastructure_models.InfrastructureMaintenanceDifficultyLevel
        )

    def test_infrastructuremaintenancedifficulty_detail(self):
        self.check_structure_response(
            self.get_infrastructuremaintenancedifficulty_detail(self.infrastructure_maintenancedifficulty.pk),
            INFRASTRUCTURE_MAINTENANCE_DIFFICULTY_DETAIL_JSON_STRUCTURE
        )

    def test_infrastructureusagedifficulty_list(self):
        self.check_number_elems_response(
            self.get_infrastructureusagedifficulty_list(),
            infrastructure_models.InfrastructureUsageDifficultyLevel
        )

    def test_infrastructureusagedifficulty_detail(self):
        self.check_structure_response(
            self.get_infrastructureusagedifficulty_detail(self.infrastructure_usagedifficulty.pk),
            INFRASTRUCTURE_USAGE_DIFFICULTY_DETAIL_JSON_STRUCTURE
        )

    def test_servicetype_list(self):
        response = self.get_servicetype_list()
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        services = trek_models.ServiceType.objects.all()
        self.assertEqual(len(json_response['results']), services.count() - 1, services.filter(published=True).count())

    def test_servicetype_detail(self):
        self.check_structure_response(
            self.get_servicetype_detail(self.service_type.pk),
            SERVICE_TYPE_DETAIL_JSON_STRUCTURE
        )

    def test_signage_detail(self):
        self.check_structure_response(
            self.get_signage_detail(self.signage.pk),
            SIGNAGE_DETAIL_JSON_STRUCTURE
        )

    def test_signage_list(self):
        self.check_number_elems_response(
            self.get_signage_list(),
            signage_models.Signage
        )

    def test_signagetype_list(self):
        self.check_number_elems_response(
            self.get_signagetype_list(),
            signage_models.SignageType
        )

    def test_signagetype_detail(self):
        self.check_structure_response(
            self.get_signagetype_detail(self.signagetype.pk),
            SIGNAGE_TYPE_DETAIL_JSON_STRUCTURE
        )

    def test_signagebladetype_list(self):
        self.check_number_elems_response(
            self.get_signagebladetype_list(),
            signage_models.BladeType
        )

    def test_signagebladetype_detail(self):
        self.check_structure_response(
            self.get_signagebladetype_detail(self.bladetype.pk),
            SIGNAGE_BLADE_TYPE_DETAIL_JSON_STRUCTURE
        )

    def test_signagesealing_list(self):
        self.check_number_elems_response(
            self.get_signagesealing_list(),
            signage_models.Sealing
        )

    def test_signagesealing_detail(self):
        self.check_structure_response(
            self.get_signagesealing_detail(self.sealing.pk),
            SIGNAGE_SEALING_DETAIL_JSON_STRUCTURE
        )

    def test_signagecolor_list(self):
        self.check_number_elems_response(
            self.get_signagecolor_list(),
            signage_models.Color
        )

    def test_signagecolor_detail(self):
        self.check_structure_response(
            self.get_signagecolor_detail(self.color.pk),
            SIGNAGE_BLADE_COLOR_DETAIL_JSON_STRUCTURE
        )

    def test_signagedirection_list(self):
        self.check_number_elems_response(
            self.get_signagedirection_list(),
            signage_models.Direction
        )

    def test_signagedirection_detail(self):
        self.check_structure_response(
            self.get_signagedirection_detail(self.direction.pk),
            SIGNAGE_DIRECTION_DETAIL_JSON_STRUCTURE
        )

    def test_service_types_filter(self):
        response = self.get_service_list({'types': self.service_type.pk})
        self.assertEqual(response.json().get("count"), 1)

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

        response = self.get_poi_list({'types': self.poi_type.pk, 'trek': self.treks[0].pk, 'sites': self.site.pk, 'courses': self.course.pk})
        self.assertEqual(response.status_code, 200)

    def launch_tests_excluded_pois(self, obj, filter_name):
        response = self.get_poi_list({filter_name: obj.pk})
        json_response = response.json()
        #  test response code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(json_response.get('results')),
            trek_models.POI.objects.all().count() - 1  # 1 excluded POI
        )
        obj.pois_excluded.add(self.poi)
        obj.save()

        response = self.get_poi_list({filter_name: obj.pk})
        json_response = response.json()
        #  test response code
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(json_response.get('results')),
            trek_models.POI.objects.all().count() - 2  # 1 excluded POI
        )

    def test_poi_list_filter_trek(self):
        self.launch_tests_excluded_pois(self.treks[0], 'trek')

    def test_poi_list_filter_courses(self):
        self.launch_tests_excluded_pois(self.course, 'courses')

    def test_poi_list_filter_sites(self):
        self.launch_tests_excluded_pois(self.site, 'sites')

    def test_poi_list_filtered_by_near_trek(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            trek = trek_factory.TrekFactory()
            trek_factory.POIFactory(paths=[(trek.paths.first(), 0.5, 0.5)], name="a POI near trek")
            far_away_coords = [[n + 2000 for n in c] for c in trek.geom.coords]
            far_away_path = core_factory.PathFactory(geom=LineString(far_away_coords, srid=settings.SRID))
            trek_factory.POIFactory(paths=[far_away_path, 0.5, 0.5], name="a POI far from trek")
            near_excluded_poi = trek_factory.POIFactory(paths=[(trek.paths.first(), 0.2, 0.2)])
        else:
            trek = trek_factory.TrekFactory(geom=LineString(Point(500, 600), Point(550, 800), srid=settings.SRID))
            trek_factory.POIFactory(geom=Point(525, 700, srid=settings.SRID), name="a POI near trek")
            trek_factory.POIFactory(geom=Point(2500, 3000, srid=settings.SRID), name="a POI far from trek")
            near_excluded_poi = trek_factory.POIFactory(geom=Point(510, 620, srid=settings.SRID))
        trek.pois_excluded.add(near_excluded_poi)

        for filtername in ["near_trek", "trek"]:
            response = self.get_poi_list({filtername: trek.pk})

            self.assertEqual(response.status_code, 200)
            # Expects a single POI without far away or excluded POIs
            json_response = response.json()
            self.assertEqual(json_response["count"], 1)
            response_poi = json_response["results"][0]
            self.assertEqual(response_poi["name"][settings.MODELTRANSLATION_DEFAULT_LANGUAGE], "a POI near trek")

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

    def test_poi_list_filter_in_bbox(self):
        """ Test POI list is filtered by bbox param """
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

        test_bbox = LineString(geom_point_1, geom_point_2, srid=2154)
        test_bbox.buffer(10)
        test_bbox.transform(4326)
        xmin, ymin, xmax, ymax = test_bbox.extent

        # test pois is in bbox filter
        response = self.get_poi_list({
            'in_bbox': f'{xmin},{ymin},{xmax},{ymax}',
        })
        # json collection structure is ok
        json_response = response.json()
        ids_pois = [element['id'] for element in json_response['results']]
        self.assertIn(poi_1.pk, ids_pois)
        self.assertIn(poi_2.pk, ids_pois)

        # test trek is not in distance filter (< 50km)
        response = self.get_poi_list({
            'in_bbox': f'{0.0},{0.0},{1.0},{1.0}',
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
        poi_not_published = trek_factory.POIFactory.create(published=False)
        response = self.get_poi_detail(poi_not_published.pk)
        self.assertEqual(response.status_code, 404)

    def test_touristiccontentcategory_detail(self):
        self.check_structure_response(
            self.get_touristiccontentcategory_detail(self.category.pk),
            TOURISTIC_CONTENT_CATEGORY_DETAIL_JSON_STRUCTURE
        )

    def test_touristiccontentcategory_list(self):
        json_response = self.get_touristiccontentcategory_list().json()
        # Get two objects for the two published touristic contents
        self.assertEqual(len(json_response['results']), 2)

    def test_touristiccontentcategory_list_filter(self):
        response = self.get_touristiccontentcategory_list({'portals': self.portal.pk})
        self.assertEqual(len(response.json()['results']), 1)

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

    def test_touristiccontent_list_filter_in_bbox(self):
        """ Test Touristic content list is filtered by bbox """
        geom_point_1 = Point(x=1.4464187622070312,
                             y=43.65147866566022, srid=4326)
        geom_point_1.transform(2154)
        tc_1 = tourism_factory.TouristicContentFactory(geom=geom_point_1)
        geom_point_2 = Point(x=1.435432434082031,
                             y=43.63682057801007, srid=4326)
        geom_point_2.transform(2154)
        tc_2 = tourism_factory.TouristicContentFactory(geom=geom_point_2)

        bbox = LineString(geom_point_1, geom_point_2, srid=2154)
        bbox.buffer(10)
        bbox.transform(4326)
        xmin, ymin, xmax, ymax = bbox.extent

        # test present filtering < 110km
        response = self.get_touristiccontent_list({
            'in_bbox': f"{xmin},{ymin},{xmax},{ymax}",
        })

        json_response = response.json()
        ids = [element['id'] for element in json_response['results']]
        self.assertIn(tc_1.pk, ids)
        self.assertIn(tc_2.pk, ids)

        # test present filtering < 50km
        response = self.get_touristiccontent_list({
            'in_bbox': f"{0.0},{0.0},{1.0},{1.0}",
        })

        json_response = response.json()
        ids = [element['id'] for element in json_response['results']]
        self.assertNotIn(tc_1.pk, ids)
        self.assertNotIn(tc_2.pk, ids)

    def test_touristiccontent_near_trek(self):
        response = self.get_touristiccontent_list({'near_trek': self.treks[0].pk})
        self.assertEqual(len(response.json()['results']), 2)

    def test_touristiccontent_near_missing_trek(self):
        response = self.get_touristiccontent_list({'near_trek': 42666})
        self.assertEqual(len(response.json()['results']), 0)

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

    def test_touristiccontent_label_accessibility(self):
        response = self.get_touristiccontent_list({'labels_accessibility': self.label_accessibility.pk})
        self.assertEqual(len(response.json()['results']), 1)

    def test_touristiccontent_q(self):
        response = self.get_touristiccontent_list({'q': 'Blah CT'})
        self.assertEqual(len(response.json()['results']), 2)

    def test_touristiccontent_detail_with_lang(self):
        response = self.get_touristiccontent_list({'language': 'en'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'][0]['pdf'],
                         f'http://testserver/api/en/touristiccontents/{self.content.pk}/touristic-content.pdf')

    def test_labels_accessibility_detail(self):
        self.check_structure_response(
            self.get_labelaccessibility_detail(self.label_accessibility.pk),
            LABEL_ACCESSIBILITY_DETAIL_JSON_STRUCTURE
        )

    def test_labels_accessibility_list(self):
        self.check_number_elems_response(
            self.get_labelaccessibility_list(),
            tourism_models.LabelAccessibility
        )

    def test_labels_list(self):
        self.check_number_elems_response(
            self.get_label_list(),
            common_models.Label
        )

    def test_labels_filter_filter(self):
        label_1 = common_factory.LabelFactory.create(filter=False)
        label_2 = common_factory.LabelFactory.create(filter=True)
        self.treks[0].labels.add(label_1, label_2)
        response = self.get_label_list({'only_filters': True})
        self.assertEqual(response.json()["count"], 3)
        self.assertSetEqual({result["id"] for result in response.json()["results"]}, {self.label.pk, label_2.pk, self.label_3.pk})
        response = self.get_label_list({'only_filters': False})
        self.assertEqual(response.json()["results"][0]["id"], label_1.pk)
        self.assertEqual(response.json()["count"], 1)
        response = self.get_label_list()
        self.assertEqual(response.json()["count"], 4)

        response = self.get_label_list({'only_filters': 'None'})
        self.assertEqual(response.json()["count"], 0)

    def test_labels_detail(self):
        self.check_structure_response(
            self.get_label_detail(self.label.pk),
            TREK_LABEL_PROPERTIES_JSON_STRUCTURE
        )

    def test_filetype_detail(self):
        self.check_structure_response(
            self.get_filetype_detail(self.filetype.pk),
            FILETYPE_PROPERTIES_JSON_STRUCTURE
        )

    def test_filetype_list(self):
        self.check_number_elems_response(
            self.get_filetype_list(),
            common_models.FileType
        )

    def test_informationdesk_list(self):
        self.check_number_elems_response(
            self.get_informationdesk_list(),
            tourism_models.InformationDesk
        )

    def test_informationdesk_list_with_svg(self):
        info_desk = tourism_factory.InformationDeskFactory(
            photo=get_dummy_uploaded_image_svg(), name='test!')
        info_desk.save()
        self.treks[0].information_desks.add(info_desk)
        self.check_number_elems_response(
            self.get_informationdesk_list(),
            tourism_models.InformationDesk
        )

    def test_informationdesk_detail(self):
        self.check_structure_response(
            self.get_informationdesk_detail(self.info_desk.pk),
            INFORMATION_DESK_PROPERTIES_JSON_STRUCTURE
        )

    def test_informationdesk_detail_with_svg(self):
        info_desk = tourism_factory.InformationDeskFactory(
            photo=get_dummy_uploaded_image_svg())
        info_desk.save()
        self.treks[0].information_desks.add(info_desk)
        self.check_structure_response(
            self.get_informationdesk_detail(info_desk.pk),
            INFORMATION_DESK_PROPERTIES_JSON_STRUCTURE
        )

    def test_informationdesk_filter_trek(self):
        response = self.get_informationdesk_list({'trek': self.treks[0].pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.info_desk.pk)
        response = self.get_informationdesk_list({'trek': self.parent.pk})
        self.assertEqual(response.json()["count"], 0)

    def test_infodesk_filter_type(self):
        response = self.get_informationdesk_list({'types': self.information_desk_type.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.info_desk.pk)

    def test_infodesk_filter_label_accessibility(self):
        response = self.get_informationdesk_list({'labels_accessibility': self.label_accessibility.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.info_desk.pk)

    def test_informationdesk_type_list(self):
        self.check_number_elems_response(
            self.get_informationdesk_type_list(),
            tourism_models.InformationDeskType
        )

    def test_informationdesk_type_detail(self):
        self.check_structure_response(
            self.get_informationdesk_type_detail(self.information_desk_type.pk),
            INFORMATION_DESK_TYPE_PROPERTIES_JSON_STRUCTURE
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
        self.assertEqual(len(response.json()['results']), 2)

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

    def test_coursetype_list(self):
        self.check_number_elems_response(
            self.get_coursetype_list(),
            outdoor_models.CourseType
        )

    def test_coursetype_detail(self):
        self.check_structure_response(
            self.get_coursetype_detail(self.coursetype.pk),
            COURSETYPE_PROPERTIES_JSON_STRUCTURE
        )

    def test_course_list_filters(self):
        response = self.get_course_list({
            'q': 'test string'
        })
        #  test response code
        self.assertEqual(response.status_code, 200)

    def test_outdoorpractice_list(self):
        response = self.get_outdoorpractice_list()
        json_response = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(json_response['results']),
            outdoor_models.Practice.objects.filter(sites__published=True).distinct().count()
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

    def test_sensitivearea_list_filtered_by_near_trek(self):
        nearby_dist = settings.SENSITIVE_AREA_INTERSECTION_MARGIN // 2
        far_away_dist = settings.SENSITIVE_AREA_INTERSECTION_MARGIN * 2
        trek_x = 24800
        if settings.TREKKING_TOPOLOGY_ENABLED:
            trek_path = core_factory.PathFactory(geom=LineString(Point(trek_x, 7800), Point(trek_x, 7900), srid=settings.SRID))
            trek = trek_factory.TrekFactory(paths=[(trek_path, 0, 1)])
        else:
            trek = trek_factory.TrekFactory(geom=LineString(Point(trek_x, 7800), Point(trek_x, 7900), srid=settings.SRID))
        # a sensitive area near it
        near_area_x1 = trek_x + nearby_dist
        near_area_x2 = trek_x + nearby_dist + 1000
        sensitivity_factory.SensitiveAreaFactory(
            geom=f'POLYGON(({near_area_x1} 7800, {near_area_x2} 7800, {near_area_x2} 7900, {near_area_x1} 7900, {near_area_x1} 7800))'
        )
        # a sensitive area far from it
        far_area_x1 = trek_x + far_away_dist
        far_area_x2 = trek_x + far_away_dist + 1000
        sensitivity_factory.SensitiveAreaFactory(
            geom=f'POLYGON(({far_area_x1} 7800, {far_area_x2} 7800, {far_area_x2} 7900, {far_area_x1} 7900, {far_area_x1} 7800))'
        )

        response = self.get_sensitivearea_list({"near_trek": trek.pk, "period": "ignore"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

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

    def test_sensitivearea_distance_list(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p1 = core_factory.PathFactory.create(geom=LineString((605600, 6650000), (605604, 6650004), srid=2154))
            trek = trek_factory.TrekFactory.create(
                published=True,
                name='Parent',
                paths=[p1]
            )
        else:
            trek = trek_factory.TrekFactory.create(geom=LineString((605600, 6650000), (605604, 6650004), srid=2154))
        specy = sensitivity_factory.SpeciesFactory.create(period01=True)
        sensitivity_factory.SensitiveAreaFactory.create(
            geom='SRID=2154;POLYGON((605600 6650000, 605600 6650004, 605604 6650004, 605604 6650000, 605600 6650000))',
            species=specy,
            description="Test"
        )
        sensitivity_factory.SensitiveAreaFactory.create(
            geom='SRID=2154;POLYGON((606001 6650501, 606001 6650505, 606005 6650505, 606005 6650501, 606001 6650501))',
            species=specy,
            description="Test 2"
        )
        response = self.get_sensitivearea_list({
            'trek': trek.id,
            'period': '1'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        # validate wrong trek id returns empty list
        response = self.get_sensitivearea_list({
            'trek': 9999
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    def test_hdviewpoint_detail_content(self):
        response = self.get_hdviewpoint_detail(self.hdviewpoint_trek.pk)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(
            json_response.get('picture_tiles_url'),
            f"http://testserver/api/hdviewpoint/drf/hdviewpoints/{self.hdviewpoint_trek.pk}/tiles/%7Bz%7D/%7Bx%7D/%7By%7D.png?source=vips"
        )
        json.dumps(json_response.get('annotations'))
        self.assertIsNone(json_response.get('site'))
        self.assertIsNone(json_response.get('poi'))
        self.assertEqual(json_response.get('trek').get('uuid'), str(self.treks[0].uuid))
        self.assertEqual(json_response.get('trek').get('id'), self.treks[0].id)

    def test_hdviewpoint_detail_content_poi(self):
        response = self.get_hdviewpoint_detail(self.hdviewpoint_poi.pk)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        json.dumps(json_response.get('annotations'))
        self.assertIsNone(json_response.get('site'))
        self.assertIsNone(json_response.get('trek'))
        self.assertEqual(json_response.get('poi').get('uuid'), str(self.poi.uuid))
        self.assertEqual(json_response.get('poi').get('id'), self.poi.id)

    def test_hdviewpoint_detail_content_site(self):
        response = self.get_hdviewpoint_detail(self.hdviewpoint_site.pk)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        json.dumps(json_response.get('annotations'))
        self.assertIsNone(json_response.get('poi'))
        self.assertIsNone(json_response.get('trek'))
        self.assertEqual(json_response.get('site').get('uuid'), str(self.site.uuid))
        self.assertEqual(json_response.get('site').get('id'), self.site.id)

    def test_hdviewpoint_geom_on_related_lists(self):
        response = self.get_poi_detail(self.poi.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['view_points'][0]['geometry'], {'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]})
        response = self.get_site_detail(self.site.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['view_points'][0]['geometry'], {'type': 'Point', 'coordinates': [-1.3630812, -5.9838563]})


class APIAccessAdministratorTestCase(BaseApiTest):
    """ TestCase for administrator API profile """

    @classmethod
    def setUpTestData(cls):
        #  created user
        cls.administrator = SuperUserFactory()
        super().setUpTestData()

    def test_path_list(self):
        self.client.force_login(self.administrator)
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
    """ TestCase API documentation """

    def test_schema_fields(self):
        response = self.client.get('/api/v2/', {'format': 'openapi'})
        self.assertContains(response, 'Filter by a bounding box formatted like W-lng,S-lat,E-lng,N-lat (WGS84).')
        self.assertContains(response, 'Set language for translation. Can be all or a two-letters language code.')
        self.assertContains(response, 'Filter by minimum difficulty level (id).')
        self.assertContains(response, 'Reference point to compute distance (WGS84). Example: lng,lat.')
        self.assertContains(response, 'Filter by one or more practice id, comma-separated.')
        self.assertContains(response, 'Filter by one or more types id, comma-separated. Logical OR for types in the same list, AND for types in different lists.')

    def test_swagger_ui(self):
        response = self.client.get('/api/v2/')
        self.assertContains(response, 'swagger')


class TrekRatingScaleTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.practice1 = trek_factory.PracticeFactory()
        cls.practice2 = trek_factory.PracticeFactory()
        cls.practice1.treks.set([trek_factory.TrekFactory()])
        cls.practice2.treks.set([trek_factory.TrekFactory()])
        cls.scale1 = trek_factory.RatingScaleFactory(name='AAA', practice=cls.practice1)
        cls.scale2 = trek_factory.RatingScaleFactory(name='AAA', practice=cls.practice2)
        cls.scale3 = trek_factory.RatingScaleFactory(name='BBB', practice=cls.practice2)

    def test_list(self):
        response = self.client.get('/api/v2/trek_ratingscale/')
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
        response = self.client.get('/api/v2/trek_ratingscale/{}/'.format(self.scale1.pk))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'id': self.scale1.pk,
            'name': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
            'practice': self.practice1.pk,
        })

    def test_filter_q(self):
        response = self.client.get('/api/v2/trek_ratingscale/', {'q': 'A'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for scale in response.json()['results']:
            self.assertEqual(scale['name']['en'], 'AAA')

    def test_filter_practice(self):
        response = self.client.get('/api/v2/trek_ratingscale/', {'practices': self.practice2.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for scale in response.json()['results']:
            self.assertEqual(scale['practice'], self.practice2.pk)


class OutdoorRatingScaleTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.practice1 = outdoor_factory.PracticeFactory()
        cls.practice2 = outdoor_factory.PracticeFactory()
        cls.practice1.sites.set([outdoor_factory.SiteFactory()])
        cls.practice2.sites.set([outdoor_factory.SiteFactory()])
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
        response = self.client.get('/api/v2/outdoor_ratingscale/', {'q': 'A'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for scale in response.json()['results']:
            self.assertEqual(scale['name']['en'], 'AAA')

    def test_filter_practice(self):
        response = self.client.get('/api/v2/outdoor_ratingscale/', {'practices': self.practice2.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for scale in response.json()['results']:
            self.assertEqual(scale['practice'], self.practice2.pk)


class TrekRatingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.scale1 = trek_factory.RatingScaleFactory(name='BBB')
        cls.scale2 = trek_factory.RatingScaleFactory(name='AAA')
        cls.rating1 = trek_factory.RatingFactory(name='AAA', scale=cls.scale1)
        cls.rating2 = trek_factory.RatingFactory(name='AAA', scale=cls.scale2)
        cls.rating3 = trek_factory.RatingFactory(name='BBB', scale=cls.scale2)
        cls.rating1.treks.set([trek_factory.TrekFactory()])
        cls.rating2.treks.set([trek_factory.TrekFactory()])
        cls.rating3.treks.set([trek_factory.TrekFactory()])

    def test_list(self):
        response = self.client.get('/api/v2/trek_rating/')
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
        response = self.client.get('/api/v2/trek_rating/{}/'.format(self.rating2.pk))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'id': self.rating2.pk,
            'color': '',
            'description': {'en': None, 'es': None, 'fr': None, 'it': None},
            'name': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
            'order': None,
            'scale': self.scale2.pk,
        })

    def test_filter_q(self):
        response = self.client.get('/api/v2/trek_rating/', {'q': 'BBB'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for rating in response.json()['results']:
            self.assertNotEqual(rating['name']['en'] == 'BBB', rating['scale'] == self.scale1.pk)

    def test_filter_scale(self):
        response = self.client.get('/api/v2/trek_rating/', {'scale': self.scale2.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for rating in response.json()['results']:
            self.assertEqual(rating['scale'], self.scale2.pk)


class OutdoorRatingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.scale1 = outdoor_factory.RatingScaleFactory(name='BBB')
        cls.scale2 = outdoor_factory.RatingScaleFactory(name='AAA')
        cls.rating1 = outdoor_factory.RatingFactory(name='AAA', scale=cls.scale1)
        cls.rating2 = outdoor_factory.RatingFactory(name='AAA', scale=cls.scale2)
        cls.rating3 = outdoor_factory.RatingFactory(name='BBB', scale=cls.scale2)
        cls.rating1.sites.set([outdoor_factory.SiteFactory()])
        cls.rating2.sites.set([outdoor_factory.SiteFactory()])
        cls.rating3.sites.set([outdoor_factory.SiteFactory()])

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
        response = self.client.get('/api/v2/outdoor_rating/', {'q': 'BBB'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for rating in response.json()['results']:
            self.assertNotEqual(rating['name']['en'] == 'BBB', rating['scale'] == self.scale1.pk)

    def test_filter_scale(self):
        response = self.client.get('/api/v2/outdoor_rating/', {'scale': self.scale2.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        for rating in response.json()['results']:
            self.assertEqual(rating['scale'], self.scale2.pk)


class FlatPageTestCase(TestCase):

    published_page_factory = partial(flatpages_factory.FlatPageFactory, published=True)

    @staticmethod
    def add_child(parent, child, pos="last-child"):
        # treebeard doc advises to get fresh object from the DB for tree operations.
        # See "Note" at https://django-treebeard.readthedocs.io/en/latest/tutorial.html

        def get(pk):
            return FlatPage.objects.get(pk=pk)

        get(child.pk).move(get(parent.pk), pos=pos)

    @classmethod
    def setUpTestData(cls):
        cls.source = common_factory.RecordSourceFactory()
        cls.portal = common_factory.TargetPortalFactory()
        cls.page1 = flatpages_factory.FlatPageFactory(
            title='AAA', published=True, content='Blah',
            sources=[cls.source], portals=[cls.portal]
        )
        cls.page2 = flatpages_factory.FlatPageFactory(
            title='BBB', published=True, content='Blbh'
        )

    def test_list(self):
        response = self.client.get('/api/v2/flatpage/')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data["count"], 2)
        resp_by_ids = {page["id"]: page for page in resp_data["results"]}
        self.assertIn(self.page1.id, resp_by_ids.keys())
        self.assertIn(self.page2.id, resp_by_ids.keys())
        self.assertEqual(
            resp_by_ids[self.page1.id],
            {
                'id': self.page1.pk,
                'title': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
                'content': {'en': 'Blah', 'es': None, 'fr': None, 'it': None},
                'portals': [self.portal.pk],
                'published': {'en': True, 'es': False, 'fr': False, 'it': False},
                'source': [self.source.pk],
                'attachments': [],
                'parent': None,
                'children': [],
            }
        )
        self.assertEqual(
            resp_by_ids[self.page2.id],
            {
                'id': self.page2.pk,
                'title': {'en': 'BBB', 'es': None, 'fr': None, 'it': None},
                'content': {'en': 'Blbh', 'es': None, 'fr': None, 'it': None},
                'portals': [],
                'published': {'en': True, 'es': False, 'fr': False, 'it': False},
                'source': [],
                'attachments': [],
                'parent': None,
                'children': [],
            }
        )

    def test_list_returns_published_page_only(self):
        flatpages_factory.FlatPageFactory(
            title='Not published page', published=False, content='Not published content'
        )

        response = self.client.get('/api/v2/flatpage/')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data["count"], 2)
        resp_ids = [page["id"] for page in resp_data["results"]]
        self.assertIn(self.page1.id, resp_ids)
        self.assertIn(self.page2.id, resp_ids)

    def test_list_returns_published_in_specified_language_only(self):
        self.page2.published_fr = True
        self.page2.save()
        flatpages_factory.FlatPageFactory(
            title='Not published page', published=False, content='Not published content'
        )

        response = self.client.get('/api/v2/flatpage/?language=fr')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data["count"], 1)
        self.assertEqual(resp_data["results"][0]["id"], self.page2.id)

    def test_list_returns_pages_associated_to_portals(self):
        portal1 = common_factory.TargetPortalFactory()
        portal2 = common_factory.TargetPortalFactory()
        published_page_factory = partial(flatpages_factory.FlatPageFactory, published=True)
        page1 = published_page_factory(portals=[portal1])
        page2 = published_page_factory(portals=[portal1, portal2])
        published_page_factory(portals=None)

        response = self.client.get(f'/api/v2/flatpage/?portals={portal1.id},{portal2.id}')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data["count"], 2)
        resp_ids = [page["id"] for page in resp_data["results"]]
        self.assertIn(page1.id, resp_ids)
        self.assertIn(page2.id, resp_ids)

    def test_list_returns_page_checking_both_publication_and_portal(self):
        portal1 = common_factory.TargetPortalFactory()
        portal2 = common_factory.TargetPortalFactory()
        page_factory = flatpages_factory.FlatPageFactory
        page_factory(published_en=True, published_fr=False, portals=[portal2])
        page_factory(published_fr=True, portals=[portal1])
        page_factory(published_fr=True, portals=None)
        visible_page = page_factory(published_fr=True, portals=[portal2])

        response = self.client.get(f'/api/v2/flatpage/?language=fr&portals={portal2.id}')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data["count"], 1)
        self.assertEqual(resp_data["results"][0]["id"], visible_page.id)

    def test_list_returns_page_targeted_by_visible_menu_item(self):
        portal = common_factory.TargetPortalFactory()
        page_factory = partial(flatpages_factory.FlatPageFactory, published_fr=True, portals=None)
        not_visible_page = page_factory()
        visible_page = page_factory()
        menu_factory = partial(flatpages_factory.MenuItemFactory, target_type=MenuItem.TARGET_TYPE_CHOICES.PAGE)
        # Those 3 menu items are not visible given the following API query
        menu_factory(published=False, portals=[portal], page=not_visible_page)
        menu_factory(published_en=True, published_fr=False, portals=[portal], page=not_visible_page)
        menu_factory(published_fr=True, portals=None, page=not_visible_page)
        # Visible menu item
        menu_factory(published_fr=True, portals=[portal], page=visible_page)

        response = self.client.get(f'/api/v2/flatpage/?language=fr&portals={portal.id}')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data["count"], 1)
        self.assertEqual(resp_data["results"][0]["id"], visible_page.id)

    def test_list_filters_children_prop(self):
        portal1 = common_factory.TargetPortalFactory()
        portal2 = common_factory.TargetPortalFactory()
        page_factory = flatpages_factory.FlatPageFactory
        parent_page = page_factory(published_fr=True, portals=[portal1])
        # Those 3 children pages should not be visible
        page_factory(published_en=True, published_fr=False, portals=[portal1]).move(parent_page, pos="last-child")
        page_factory(published_en=True, published_fr=True, portals=[portal2]).move(parent_page, pos="last-child")
        page_factory(published_en=True, published_fr=True, portals=None).move(parent_page, pos="last-child")
        # Visible child page
        visible_child_page = page_factory(published_en=True, published_fr=True, portals=[portal1])
        visible_child_page.move(parent_page, pos="last-child")

        response = self.client.get(f'/api/v2/flatpage/?language=fr&portals={portal1.id}')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        parent_page_repr = {p["id"]: p for p in resp_data["results"]}[parent_page.id]
        self.assertEqual(len(parent_page_repr["children"]), 1)
        self.assertEqual(parent_page_repr["children"][0], visible_child_page.id)

    def test_list_includes_children_pages_in_order(self):
        parent = self.published_page_factory()
        children = [self.published_page_factory() for _ in range(3)]
        children_ids = [c.id for c in children]
        self.add_child(parent=parent, child=children[0], pos="last-child")
        self.add_child(parent=parent, child=children[1], pos="first-child")
        self.add_child(parent=children[0], child=children[2], pos="left")

        response = self.client.get('/api/v2/flatpage/')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        parent_page_repr = {p["id"]: p for p in resp_data["results"]}[parent.id]
        self.assertEqual(parent_page_repr["children"], [children_ids[1], children_ids[2], children_ids[0]])

    def test_list_returns_null_parent_prop_when_parent_has_no_portal(self):
        portal = common_factory.TargetPortalFactory()
        page_factory = flatpages_factory.FlatPageFactory
        parent_page = page_factory(published_fr=True, portals=None)
        child_page = page_factory(published_en=True, published_fr=True, portals=[portal])
        child_page.move(parent_page, pos="last-child")

        response = self.client.get(f'/api/v2/flatpage/?language=fr&portals={portal.id}')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        child_page_repr = {p["id"]: p for p in resp_data["results"]}[child_page.id]
        self.assertEqual(child_page_repr["parent"], None)

    def test_list_returns_null_parent_prop_when_parent_has_another_portal(self):
        portal1 = common_factory.TargetPortalFactory()
        portal2 = common_factory.TargetPortalFactory()
        page_factory = flatpages_factory.FlatPageFactory
        parent_page = page_factory(published_fr=True, portals=[portal2])
        child_page = page_factory(published_fr=True, portals=[portal1])
        child_page.move(parent_page, pos="last-child")

        response = self.client.get(f'/api/v2/flatpage/?language=fr&portals={portal1.id}')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        child_page_repr = {p["id"]: p for p in resp_data["results"]}[child_page.id]
        self.assertEqual(child_page_repr["parent"], None)

    def test_list_returns_null_parent_prop_when_parent_is_not_lang_published(self):
        portal = common_factory.TargetPortalFactory()
        page_factory = flatpages_factory.FlatPageFactory
        parent_page = page_factory(published_fr=False, portals=[portal])
        child_page = page_factory(published_fr=True, portals=[portal])
        child_page.move(parent_page, pos="last-child")

        response = self.client.get(f'/api/v2/flatpage/?language=fr&portals={portal.id}')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        child_page_repr = {p["id"]: p for p in resp_data["results"]}[child_page.id]
        self.assertEqual(child_page_repr["parent"], None)

    def test_list_returns_null_parent_prop_when_parent_is_not_published(self):
        portal = common_factory.TargetPortalFactory()
        page_factory = flatpages_factory.FlatPageFactory
        parent_page = page_factory(published=False, portals=[portal])
        child_page = page_factory(published=True, portals=[portal])
        child_page.move(parent_page, pos="last-child")

        response = self.client.get(f'/api/v2/flatpage/?portals={portal.id}')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        child_page_repr = {p["id"]: p for p in resp_data["results"]}[child_page.id]
        self.assertEqual(child_page_repr["parent"], None)

    def test_list_filter_by_parent(self):
        parent = self.published_page_factory()
        children = [self.published_page_factory() for _ in range(3)]
        children_ids = [c.id for c in children]
        self.add_child(parent, children[0])
        self.add_child(parent, children[1])
        self.add_child(parent, children[2])

        response = self.client.get(f'/api/v2/flatpage/?parent={parent.id}')

        self.assertEqual(response.status_code, 200)
        child_pages_ids = [p["id"] for p in response.json()["results"]]
        self.assertEqual(child_pages_ids, [children_ids[0], children_ids[1], children_ids[2]])

    def test_list_filter_by_parent_child_pages_are_ordered(self):
        parent = self.published_page_factory()
        children = [self.published_page_factory() for _ in range(3)]
        children_ids = [c.id for c in children]
        self.add_child(parent=parent, child=children[0], pos="last-child")
        self.add_child(parent=parent, child=children[1], pos="first-child")
        self.add_child(parent=children[0], child=children[2], pos="left")

        response = self.client.get(f'/api/v2/flatpage/?parent={parent.id}')

        self.assertEqual(response.status_code, 200)
        child_pages_ids = [p["id"] for p in response.json()["results"]]
        self.assertEqual(child_pages_ids, [children_ids[1], children_ids[2], children_ids[0]])

    def test_list_filter_by_parent_not_exists(self):
        not_exists_parent_id = 123

        response = self.client.get(f'/api/v2/flatpage/?parent={not_exists_parent_id}')

        self.assertEqual(response.status_code, 200)
        resp_data = response.json()
        self.assertEqual(resp_data["count"], 0)
        self.assertEqual(resp_data["results"], [])

    def test_list_filter_by_parent_child_pages_visibility(self):
        portal1 = common_factory.TargetPortalFactory()
        portal2 = common_factory.TargetPortalFactory()
        page_factory = flatpages_factory.FlatPageFactory
        parent_page = page_factory(published_fr=True, portals=[portal1])
        # Those 3 children pages should not be visible
        page_factory(published_en=True, published_fr=False, portals=[portal1]).move(parent_page, pos="last-child")
        page_factory(published_en=True, published_fr=True, portals=[portal2]).move(parent_page, pos="last-child")
        page_factory(published_en=True, published_fr=True, portals=None).move(parent_page, pos="last-child")
        # Visible child page
        visible_child_page = page_factory(published_en=True, published_fr=True, portals=[portal1])
        visible_child_page.move(parent_page, pos="last-child")

        response = self.client.get(f'/api/v2/flatpage/{parent_page.id}/?language=fr&portals={portal1.id}')

        self.assertEqual(response.status_code, 200)
        parent_page_repr = response.json()
        self.assertEqual(parent_page_repr["children"], [visible_child_page.id])

    def test_detail(self):
        response = self.client.get('/api/v2/flatpage/{}/'.format(self.page1.pk))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'id': self.page1.pk,
            'title': {'en': 'AAA', 'es': None, 'fr': None, 'it': None},
            'content': {'en': 'Blah', 'es': None, 'fr': None, 'it': None},
            'portals': [self.portal.pk],
            'published': {'en': True, 'es': False, 'fr': False, 'it': False},
            'source': [self.source.pk],
            'attachments': [],
            'parent': None,
            'children': [],
        })

    def test_detail_includes_filtered_children_pages(self):
        portal1 = common_factory.TargetPortalFactory()
        portal2 = common_factory.TargetPortalFactory()
        page_factory = flatpages_factory.FlatPageFactory
        parent_page = page_factory(published_fr=True, portals=[portal1])
        # Those 3 children pages should not be visible
        page_factory(published_en=True, published_fr=False, portals=[portal1]).move(parent_page, pos="last-child")
        page_factory(published_en=True, published_fr=True, portals=[portal2]).move(parent_page, pos="last-child")
        page_factory(published_en=True, published_fr=True, portals=None).move(parent_page, pos="last-child")
        # Visible child page
        visible_child_page = page_factory(published_en=True, published_fr=True, portals=[portal1])
        visible_child_page.move(parent_page, pos="last-child")

        response = self.client.get(f'/api/v2/flatpage/{parent_page.id}/?language=fr&portals={portal1.id}')

        self.assertEqual(response.status_code, 200)
        parent_page_repr = response.json()
        self.assertEqual(len(parent_page_repr["children"]), 1)
        self.assertEqual(parent_page_repr["children"][0], visible_child_page.id)

    def test_detail_includes_children_pages_in_order(self):
        parent = self.published_page_factory()
        children = [self.published_page_factory() for _ in range(3)]
        children_ids = [c.id for c in children]
        self.add_child(parent=parent, child=children[0], pos="last-child")
        self.add_child(parent=parent, child=children[1], pos="first-child")
        self.add_child(parent=children[0], child=children[2], pos="left")

        response = self.client.get(f'/api/v2/flatpage/{parent.id}/')

        self.assertEqual(response.status_code, 200)
        parent_page_repr = response.json()
        self.assertEqual(parent_page_repr["children"], [children_ids[1], children_ids[2], children_ids[0]])

    def test_filter_q(self):
        response = self.client.get('/api/v2/flatpage/', {'q': 'BB'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['title']['en'], 'BBB')

    def test_filter_sources(self):
        response = self.client.get('/api/v2/flatpage/', {'sources': self.source.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['title']['en'], 'AAA')

    def test_filter_portals(self):
        response = self.client.get('/api/v2/flatpage/', {'portals': self.portal.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['title']['en'], 'AAA')

    def test_filter_sources_by_portal(self):
        response = self.client.get('/api/v2/source/', {'portals': self.portal.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], self.source.name)


class MenuItemTestCase(TestCase):

    published_menu_item_factory = partial(MenuItemFactory, published=True)

    @staticmethod
    def add_child(parent, child):
        # treebeard doc advises to get fresh object from the DB for tree operations.
        # See "Note" at https://django-treebeard.readthedocs.io/en/latest/tutorial.html

        def get(pk):
            return MenuItem.objects.get(pk=pk)

        get(child.pk).move(get(parent.pk), pos="last-child")

    def test_tree(self):
        parent = self.published_menu_item_factory(title="parent")
        child1 = self.published_menu_item_factory(title="child1")
        self.add_child(parent, child1)
        child2 = self.published_menu_item_factory(title="child2")
        self.add_child(parent, child2)

        response = self.client.get('/api/v2/menu_item/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        parent_repr = data[0]
        self.assertEqual(parent_repr["title"]["en"], "parent")
        self.assertEqual(len(parent_repr["children"]), 2)
        child1_repr = parent_repr["children"][0]
        self.assertEqual(child1_repr["title"]["en"], "child1")
        child2_repr = parent_repr["children"][1]
        self.assertEqual(child2_repr["title"]["en"], "child2")

    def test_tree_full_data_with_no_target(self):
        portal1 = common_factory.TargetPortalFactory()
        portal2 = common_factory.TargetPortalFactory()
        menu_item = MenuItem.add_root(
            title_en="Hello World!",
            title_fr="Bonjour le monde !",
            published_en=True,
            published_fr=True,
            pictogram=get_dummy_uploaded_image("menu_item_picto.png"),
            target_type=None,
        )
        menu_item.portals.add(portal1, portal2)
        user = authent_models.User.objects.create(username="test_user")
        file_type = FileType.objects.create(type="Photographie")
        Attachment.objects.create(
            content_type=ContentType.objects.get_for_model(MenuItem),
            object_id=menu_item.id,
            attachment_file=get_dummy_uploaded_image("menu_item_thumbnail.png"),
            filetype=file_type,
            creator=user,
        )
        child1 = self.published_menu_item_factory()
        child2 = self.published_menu_item_factory()
        self.add_child(menu_item, child1)
        self.add_child(menu_item, child2)

        response = self.client.get('/api/v2/menu_item/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        menu_item_repr = data[0]
        expected_menu_item_repr = {
            "id": menu_item.id,
            "title": {
                "en": "Hello World!",
                "fr": "Bonjour le monde !",
                "es": None,
                "it": None,
            },
            "published": {
                "en": True,
                "fr": True,
                "es": False,
                "it": False,
            },
        }
        for key, value in expected_menu_item_repr.items():
            self.assertEqual(menu_item_repr[key], value)

        self.assertIn(portal1.id, menu_item_repr["portals"])
        self.assertIn(portal2.id, menu_item_repr["portals"])

        self.assertTrue(menu_item_repr["pictogram"].find("menu_item_picto") != -1)

        self.assertEqual(len(menu_item_repr["attachments"]), 1)
        attachment_repr = menu_item_repr["attachments"][0]
        self.assertTrue(attachment_repr["url"].find("menu_item_thumbnail") != -1)
        self.assertTrue(attachment_repr["thumbnail"].find("menu_item_thumbnail") != -1)

    def test_tree_with_page_target(self):
        page = flatpages_factory.FlatPageFactory(
            published=True,
            title_en="Targeted page",
            title_fr="Page ciblée",
        )
        MenuItem.add_root(
            published=True,
            target_type=MenuItem.TARGET_TYPE_CHOICES.PAGE,
            page=page,
        )

        response = self.client.get('/api/v2/menu_item/')

        self.assertEqual(response.status_code, 200)
        menu_item_repr = response.json()[0]
        self.assertEqual(menu_item_repr["target_type"], "page")
        self.assertEqual(menu_item_repr["page"], page.id)
        self.assertEqual(menu_item_repr["page_title"]["en"], page.title_en)
        self.assertEqual(menu_item_repr["page_title"]["fr"], page.title_fr)

    def test_tree_with_link_target(self):
        menu_item = MenuItem.add_root(
            published=True,
            target_type=MenuItem.TARGET_TYPE_CHOICES.LINK,
            link_url_en="https://en.example.com/",
            link_url_fr="https://fr.example.com/",
            open_in_new_tab=False,
        )

        response = self.client.get('/api/v2/menu_item/')

        self.assertEqual(response.status_code, 200)
        menu_item_repr = response.json()[0]
        self.assertEqual(menu_item_repr["target_type"], "link")
        self.assertEqual(menu_item_repr["link_url"]["en"], menu_item.link_url_en)
        self.assertEqual(menu_item_repr["link_url"]["fr"], menu_item.link_url_fr)
        self.assertEqual(menu_item_repr["open_in_new_tab"], False)

    def test_tree_target_type_is_lowercase_for_child(self):
        parent = self.published_menu_item_factory()
        child = self.published_menu_item_factory(target_type=MenuItem.TARGET_TYPE_CHOICES.LINK)
        self.add_child(parent, child)

        response = self.client.get('/api/v2/menu_item/')

        self.assertEqual(response.status_code, 200)
        parent_repr = response.json()[0]
        child_repr = parent_repr["children"][0]
        self.assertEqual(child_repr["target_type"], "link")

    def test_tree_with_portals_filter_on_root_menu_items(self):
        portal1 = common_factory.TargetPortalFactory()
        portal2 = common_factory.TargetPortalFactory()
        portal3 = common_factory.TargetPortalFactory()
        self.published_menu_item_factory(portals=[portal1])
        menu1 = self.published_menu_item_factory(portals=[portal1, portal2])
        menu2 = self.published_menu_item_factory(portals=[portal2])
        self.published_menu_item_factory(portals=None)
        menu3 = self.published_menu_item_factory(portals=[portal3])

        response = self.client.get(f'/api/v2/menu_item/?portals={portal2.pk},{portal3.pk}')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 3)
        menu_item_ids = [item["id"] for item in data]
        self.assertIn(menu1.pk, menu_item_ids)
        self.assertIn(menu2.pk, menu_item_ids)
        self.assertIn(menu3.pk, menu_item_ids)

    def test_tree_with_portals_filter_on_children(self):
        portal1 = common_factory.TargetPortalFactory()
        portal2 = common_factory.TargetPortalFactory()
        portal3 = common_factory.TargetPortalFactory()
        parent = self.published_menu_item_factory(portals=[portal2])
        menu1 = self.published_menu_item_factory(portals=[portal1])
        self.add_child(parent, menu1)
        menu2 = self.published_menu_item_factory(portals=[portal1, portal2])
        self.add_child(parent, menu2)
        menu3 = self.published_menu_item_factory(portals=[portal2])
        self.add_child(parent, menu3)
        menu4 = self.published_menu_item_factory(portals=None)
        self.add_child(parent, menu4)
        menu5 = self.published_menu_item_factory(portals=[portal3])
        self.add_child(parent, menu5)

        response = self.client.get(f'/api/v2/menu_item/?portals={portal2.pk},{portal3.pk}')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        parent_repr = data[0]
        children_ids = [item["id"] for item in parent_repr["children"]]
        self.assertIn(menu2.pk, children_ids)
        self.assertIn(menu3.pk, children_ids)
        self.assertIn(menu5.pk, children_ids)

    def test_tree_with_language_filter_on_root_items(self):
        MenuItemFactory(published_fr=False, published_en=False)
        menu1 = MenuItemFactory(published_fr=True, published_en=False)
        MenuItemFactory(published_fr=False, published_en=True)
        menu2 = MenuItemFactory(published_fr=True, published_en=True)

        response = self.client.get('/api/v2/menu_item/?language=fr')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        menu_item_ids = [item["id"] for item in data]
        self.assertIn(menu1.pk, menu_item_ids)
        self.assertIn(menu2.pk, menu_item_ids)

    def test_tree_with_language_filter_on_children(self):
        parent = MenuItemFactory(published_fr=True, published_en=True)
        child1 = MenuItemFactory(published_fr=False, published_en=False)
        child2 = MenuItemFactory(published_fr=True, published_en=False)
        child3 = MenuItemFactory(published_fr=False, published_en=True)
        child4 = MenuItemFactory(published_fr=True, published_en=True)
        self.add_child(parent, child1)
        self.add_child(parent, child2)
        self.add_child(parent, child3)
        self.add_child(parent, child4)

        response = self.client.get('/api/v2/menu_item/?language=fr')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        parent_repr = data[0]
        self.assertEqual(len(parent_repr["children"]), 2)
        children_ids = [item["id"] for item in parent_repr["children"]]
        self.assertIn(child2.pk, children_ids)
        self.assertIn(child4.pk, children_ids)

    def test_tree_with_language_filter_all_value(self):
        MenuItemFactory(published_fr=False, published_en=False)
        menu1 = MenuItemFactory(published_fr=True, published_en=False)
        menu2 = MenuItemFactory(published_fr=False, published_en=True)
        menu3 = MenuItemFactory(published_fr=True, published_en=True)

        response = self.client.get('/api/v2/menu_item/?language=all')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 3)
        menu_item_ids = [item["id"] for item in data]
        self.assertIn(menu1.pk, menu_item_ids)
        self.assertIn(menu2.pk, menu_item_ids)
        self.assertIn(menu3.pk, menu_item_ids)

    def test_tree_menu_item_not_exposed_if_target_page_not_published(self):
        page = flatpages_factory.FlatPageFactory(published=False)
        MenuItemFactory(published=True, page=page, target_type=MenuItem.TARGET_TYPE_CHOICES.PAGE)

        response = self.client.get('/api/v2/menu_item/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 0)

    def test_tree_child_menu_item_not_exposed_if_target_page_not_published(self):
        page = flatpages_factory.FlatPageFactory(published=False)
        parent = MenuItemFactory(published=True)
        child = MenuItemFactory(published=True, page=page, target_type=MenuItem.TARGET_TYPE_CHOICES.PAGE)
        self.add_child(parent, child)

        response = self.client.get('/api/v2/menu_item/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        parent_repr = data[0]
        self.assertEqual(len(parent_repr["children"]), 0)

    def test_detail(self):
        menu_item = self.published_menu_item_factory(title_en="Hello!", title_fr="Bonjour !")

        response = self.client.get(f'/api/v2/menu_item/{menu_item.pk}/')

        self.assertEqual(response.status_code, 200)
        menu_item_repr = response.json()
        self.assertEqual(
            menu_item_repr,
            {
                "id": menu_item.pk,
                "title": {
                    "en": "Hello!",
                    "fr": "Bonjour !",
                    "es": None,
                    "it": None,
                },
                "target_type": None,
                "published": {
                    "en": True,
                    "fr": False,
                    "es": False,
                    "it": False,
                },
                "page": None,
                "page_title": None,
                "link_url": {
                    "en": "",
                    "fr": "",
                    "es": "",
                    "it": "",
                },
                "open_in_new_tab": True,
                "children": [],
                "parent": None,
                "attachments": [],
                "pictogram": None,
                "portals": [],
            }
        )

    def test_detail_pictogram_is_absolute_URL(self):
        menu_item = self.published_menu_item_factory(title="Test picto", pictogram=get_dummy_uploaded_image("menu_picto.png"))

        response = self.client.get(f'/api/v2/menu_item/{menu_item.pk}/')

        self.assertEqual(response.status_code, 200)
        data = response.json()
        picto_url = data["pictogram"]
        self.assertTrue(re.match("^(http://|https://)", picto_url) is not None)

    def test_detail_includes_parent_and_children(self):
        parent = self.published_menu_item_factory()
        menu_item = self.published_menu_item_factory()
        child1 = self.published_menu_item_factory()
        child2 = self.published_menu_item_factory()
        self.add_child(parent, menu_item)
        self.add_child(menu_item, child1)
        self.add_child(menu_item, child2)

        response = self.client.get(f'/api/v2/menu_item/{menu_item.pk}/')

        self.assertEqual(response.status_code, 200)
        menu_item_repr = response.json()
        self.assertEqual(menu_item_repr["parent"], parent.id)
        self.assertEqual(len(menu_item_repr["children"]), 2)
        self.assertEqual(menu_item_repr["children"][0], child1.id)
        self.assertEqual(menu_item_repr["children"][1], child2.id)

    def test_detail_does_not_show_not_published_parent(self):
        parent = MenuItemFactory(published=False)
        menu_item = self.published_menu_item_factory()
        self.add_child(parent, menu_item)

        response = self.client.get(f'/api/v2/menu_item/{menu_item.pk}/')

        self.assertEqual(response.status_code, 200)
        menu_item_repr = response.json()
        self.assertEqual(menu_item_repr["parent"], None)

    def test_detail_does_not_show_not_published_child(self):
        menu_item = self.published_menu_item_factory()
        child1 = self.published_menu_item_factory()
        self.add_child(menu_item, child1)
        child2 = MenuItemFactory(published=False)
        self.add_child(menu_item, child2)

        response = self.client.get(f'/api/v2/menu_item/{menu_item.pk}/')

        self.assertEqual(response.status_code, 200)
        menu_item_repr = response.json()
        self.assertEqual(len(menu_item_repr["children"]), 1)
        child_id = menu_item_repr["children"][0]
        self.assertEqual(child_id, child1.id)

    def test_detail_with_language_not_found_error(self):
        menu_item = MenuItemFactory(published_en=True, published_fr=False)
        response = self.client.get(f'/api/v2/menu_item/{menu_item.pk}/?language=fr')
        self.assertEqual(response.status_code, 404)

    def test_detail_with_language_filter_on_children(self):
        menu_item = MenuItemFactory(published_en=True, published_fr=True)
        child1 = MenuItemFactory(published_en=False, published_fr=False)
        child2 = MenuItemFactory(published_en=True, published_fr=False)
        child3 = MenuItemFactory(published_en=False, published_fr=True)
        child4 = MenuItemFactory(published_en=True, published_fr=True)
        self.add_child(menu_item, child1)
        self.add_child(menu_item, child2)
        self.add_child(menu_item, child3)
        self.add_child(menu_item, child4)

        response = self.client.get(f'/api/v2/menu_item/{menu_item.pk}/?language=fr')

        self.assertEqual(response.status_code, 200)
        menu_item_repr = response.json()
        children_ids = menu_item_repr["children"]
        self.assertEqual(len(children_ids), 2)
        self.assertIn(child3.id, children_ids)
        self.assertIn(child4.id, children_ids)

    def test_detail_with_language_filter_on_parent(self):
        parent = MenuItemFactory(published_en=True, published_fr=False)
        menu_item = MenuItemFactory(published_en=True, published_fr=True)
        self.add_child(parent, menu_item)

        response = self.client.get(f'/api/v2/menu_item/{menu_item.pk}/?language=fr')

        self.assertEqual(response.status_code, 200)
        menu_item_repr = response.json()
        self.assertEqual(menu_item_repr["parent"], None)


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
                    'identifier': self.status1.identifier,
                    'color': self.status1.color,
                    "id": self.status1.pk,
                    "label": {'en': "A transmettre", 'es': None, 'fr': None, 'it': None},
                },
                {
                    'identifier': self.status2.identifier,
                    'color': self.status2.color,
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


class LanguageOrderingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trek1 = trek_factory.TrekFactory(name_fr="AAA", name_en='ABA', published_fr=True, published_en=True)
        cls.trek2 = trek_factory.TrekFactory(name_fr="ABA", name_en='BAA', published_fr=True, published_en=True)
        cls.trek3 = trek_factory.TrekFactory(name_fr="BAA", name_en="AAA", published_fr=True, published_en=True)
        cls.trek4 = trek_factory.TrekFactory(name_fr="CCC", name_en="CCC", published_fr=True, published_en=True)
        cls.course1 = outdoor_factory.CourseFactory(name_fr="AAA", name_en='ABA', published_fr=True, published_en=True)
        cls.course2 = outdoor_factory.CourseFactory(name_fr="ABA", name_en='BAA', published_fr=True, published_en=True)
        cls.course3 = outdoor_factory.CourseFactory(name_fr="BAA", name_en="AAA", published_fr=True, published_en=True)
        cls.course4 = outdoor_factory.CourseFactory(name_fr="CCC", name_en="CCC", published_fr=True, published_en=True)
        cls.site1 = outdoor_factory.SiteFactory(name_fr="AAA", name_en='ABA', published_fr=True, published_en=True)
        cls.site2 = outdoor_factory.SiteFactory(name_fr="ABA", name_en='BAA', published_fr=True, published_en=True)
        cls.site3 = outdoor_factory.SiteFactory(name_fr="BAA", name_en="AAA", published_fr=True, published_en=True)
        cls.site4 = outdoor_factory.SiteFactory(name_fr="CCC", name_en="CCC", published_fr=True, published_en=True)
        cls.tc1 = tourism_factory.TouristicContentFactory(name_fr="AAA", name_en='ABA', published_fr=True, published_en=True)
        cls.tc2 = tourism_factory.TouristicContentFactory(name_fr="ABA", name_en='BAA', published_fr=True, published_en=True)
        cls.tc3 = tourism_factory.TouristicContentFactory(name_fr="BAA", name_en="AAA", published_fr=True, published_en=True)
        cls.tc4 = tourism_factory.TouristicContentFactory(name_fr="CCC", name_en="CCC", published_fr=True, published_en=True)

    def assert_ordered_by_language(self, endpoint, ordered_ids, language):
        # GET request on list with language param
        response = self.client.get(reverse(endpoint), {'language': language})
        self.assertEqual(response.status_code, 200)
        # Assert response list is ordered as expected
        for index, expected_id in enumerate(ordered_ids):
            self.assertEqual(response.json()['results'][index]['id'], expected_id)

    def test_ordered_trek_lists(self):
        order_fr = [self.trek1.id, self.trek2.id, self.trek3.id, self.trek4.id]
        self.assert_ordered_by_language('apiv2:trek-list', order_fr, 'fr')
        order_en = [self.trek3.id, self.trek1.id, self.trek2.id, self.trek4.id]
        self.assert_ordered_by_language('apiv2:trek-list', order_en, 'en')

    def test_ordered_touristic_content_lists(self):
        order_fr = [self.tc1.id, self.tc2.id, self.tc3.id, self.tc4.id]
        self.assert_ordered_by_language('apiv2:touristiccontent-list', order_fr, 'fr')
        order_en = [self.tc3.id, self.tc1.id, self.tc2.id, self.tc4.id]
        self.assert_ordered_by_language('apiv2:touristiccontent-list', order_en, 'en')

    def test_ordered_outdoor_site_lists(self):
        order_fr = [self.site1.id, self.site2.id, self.site3.id, self.site4.id]
        self.assert_ordered_by_language('apiv2:site-list', order_fr, 'fr')
        order_en = [self.site3.id, self.site1.id, self.site2.id, self.site4.id]
        self.assert_ordered_by_language('apiv2:site-list', order_en, 'en')

    def test_order_outdoor_course_lists(self):
        order_fr = [self.course1.id, self.course2.id, self.course3.id, self.course4.id]
        self.assert_ordered_by_language('apiv2:course-list', order_fr, 'fr')
        order_en = [self.course3.id, self.course1.id, self.course2.id, self.course4.id]
        self.assert_ordered_by_language('apiv2:course-list', order_en, 'en')


class WebLinksCategoryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.web_link_cat1 = trek_factory.WebLinkCategoryFactory(pictogram='dummy_picto1.png', label="To do")
        cls.web_link_cat2 = trek_factory.WebLinkCategoryFactory(pictogram='dummy_picto2.png', label="To see")
        cls.web_link_cat3 = trek_factory.WebLinkCategoryFactory(pictogram='dummy_picto3.png', label="To eat")

    def test_web_links_category_list(self):
        response = self.client.get(reverse('apiv2:weblink-category-list'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "count": 3,
            "next": None,
            "previous": None,
            "results": [
                {
                    "label": {'en': "To do", 'es': None, 'fr': None, 'it': None},
                    "id": self.web_link_cat1.pk,
                    "pictogram": "http://testserver/media/dummy_picto1.png",
                },
                {
                    "label": {'en': "To eat", 'es': None, 'fr': None, 'it': None},
                    "id": self.web_link_cat3.pk,
                    "pictogram": "http://testserver/media/dummy_picto3.png",
                },
                {
                    "label": {'en': "To see", 'es': None, 'fr': None, 'it': None},
                    "id": self.web_link_cat2.pk,
                    "pictogram": "http://testserver/media/dummy_picto2.png",
                }]
        })

    def test_web_links_category_detail(self):
        response = self.client.get(f"/api/v2/weblink_category/{self.web_link_cat1.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            "label": {'en': "To do", 'es': None, 'fr': None, 'it': None},
            "id": self.web_link_cat1.pk,
            "pictogram": "http://testserver/media/dummy_picto1.png",
        })


class TrekWebLinksTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.web_link_cat = trek_factory.WebLinkCategoryFactory(pictogram='dummy_picto.png', label_en='Category')
        cls.web_link1 = trek_factory.WebLinkFactory(category=cls.web_link_cat, name="Web link", name_en="Web link", url="http://dummy.url")
        cls.web_link2 = trek_factory.WebLinkFactory(category=cls.web_link_cat, name="Web link", name_en="Web link", url="http://dummy.url")
        cls.trek1 = trek_factory.TrekFactory(web_links=[cls.web_link1, cls.web_link2])

    def test_web_links_in_trek_list(self):
        response = self.client.get(reverse('apiv2:trek-list'))
        self.assertEqual(response.status_code, 200)
        json_result = response.json()['results'][0]
        web_links = json_result['web_links']
        self.assertEqual(json_result['id'], self.trek1.pk)
        self.assertEqual(web_links[0]['name']['en'], "Web link")
        self.assertEqual(web_links[0]['url'], "http://dummy.url")
        self.assertEqual(web_links[0]['category']['label']['en'], "Category")
        self.assertEqual(web_links[0]['category']['id'], self.web_link_cat.pk)
        self.assertEqual(web_links[0]['category']['pictogram'], 'http://testserver/media/dummy_picto.png')
        self.assertEqual(web_links[1]['name']['en'], "Web link")
        self.assertEqual(web_links[1]['url'], "http://dummy.url")
        self.assertEqual(web_links[1]['category']['label']['en'], "Category")
        self.assertEqual(web_links[1]['category']['id'], self.web_link_cat.pk)
        self.assertEqual(web_links[1]['category']['pictogram'], 'http://testserver/media/dummy_picto.png')

    def test_web_links_in_trek_detail(self):
        response = self.client.get(f"/api/v2/trek/{self.trek1.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], self.trek1.pk)
        self.assertEqual(response.json()['web_links'][0]['name']['en'], "Web link")
        self.assertEqual(response.json()['web_links'][0]['url'], "http://dummy.url")
        self.assertEqual(response.json()['web_links'][0]['category']['label']['en'], "Category")
        self.assertEqual(response.json()['web_links'][0]['category']['id'], self.web_link_cat.pk)
        self.assertEqual(response.json()['web_links'][0]['category']['pictogram'], 'http://testserver/media/dummy_picto.png')


class TrekDifficultyFilterCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.v_easy = trek_factory.DifficultyLevelFactory(difficulty="Very easy")
        cls.easy = trek_factory.DifficultyLevelFactory(difficulty="Easy")
        cls.medium = trek_factory.DifficultyLevelFactory(difficulty="Medium")
        cls.hard = trek_factory.DifficultyLevelFactory(difficulty="Very hard")
        cls.v_hard = trek_factory.DifficultyLevelFactory(difficulty="Hard")
        cls.trek_v_easy = trek_factory.TrekFactory(difficulty=cls.v_easy)
        cls.trek_easy = trek_factory.TrekFactory(difficulty=cls.easy)
        cls.trek_medium = trek_factory.TrekFactory(difficulty=cls.medium)
        cls.trek_hard = trek_factory.TrekFactory(difficulty=cls.hard)
        cls.trek_v_hard = trek_factory.TrekFactory(difficulty=cls.v_hard)

    def assert_trek_is_in_reponse(self, response, expected_trek):
        found = list(filter(lambda trek: trek['id'] == expected_trek.pk, response.json()['results']))
        self.assertTrue(found)

    def assert_trek_is_not_in_reponse(self, response, expected_trek):
        found = list(filter(lambda trek: trek['id'] == expected_trek.pk, response.json()['results']))
        self.assertFalse(found)

    def test_difficulty_ids(self):
        self.assertEqual(self.v_easy.id, 1)
        self.assertEqual(self.easy.id, 2)
        self.assertEqual(self.medium.id, 3)
        self.assertEqual(self.hard.id, 4)
        self.assertEqual(self.v_hard.id, 5)

    def test_filter_difficulty_min(self):
        response = self.client.get("/api/v2/trek/", {'difficulty_min': self.medium.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
        self.assert_trek_is_not_in_reponse(response, self.trek_v_easy)
        self.assert_trek_is_not_in_reponse(response, self.trek_easy)
        self.assert_trek_is_in_reponse(response, self.trek_medium)
        self.assert_trek_is_in_reponse(response, self.trek_hard)
        self.assert_trek_is_in_reponse(response, self.trek_v_hard)

    def test_filter_difficulty_max(self):
        response = self.client.get("/api/v2/trek/", {'difficulty_max': self.medium.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
        self.assert_trek_is_in_reponse(response, self.trek_v_easy)
        self.assert_trek_is_in_reponse(response, self.trek_easy)
        self.assert_trek_is_in_reponse(response, self.trek_medium)
        self.assert_trek_is_not_in_reponse(response, self.trek_hard)
        self.assert_trek_is_not_in_reponse(response, self.trek_v_hard)

    def test_filter_difficulty_min_max_1(self):
        response = self.client.get("/api/v2/trek/", {'difficulty_min': self.easy.id, 'difficulty_max': self.hard.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
        self.assert_trek_is_not_in_reponse(response, self.trek_v_easy)
        self.assert_trek_is_in_reponse(response, self.trek_easy)
        self.assert_trek_is_in_reponse(response, self.trek_medium)
        self.assert_trek_is_in_reponse(response, self.trek_hard)
        self.assert_trek_is_not_in_reponse(response, self.trek_v_hard)

    def test_filter_difficulty_min_max_2(self):
        response = self.client.get("/api/v2/trek/", {'difficulty_min': self.hard.id, 'difficulty_max': self.hard.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        self.assert_trek_is_not_in_reponse(response, self.trek_v_easy)
        self.assert_trek_is_not_in_reponse(response, self.trek_easy)
        self.assert_trek_is_not_in_reponse(response, self.trek_medium)
        self.assert_trek_is_in_reponse(response, self.trek_hard)
        self.assert_trek_is_not_in_reponse(response, self.trek_v_hard)


@override_settings(SRID=4326)
@override_settings(API_SRID=4326)
@override_settings(TOURISM_INTERSECTION_MARGIN=500)
@freeze_time("2000-07-04")
class TouristicEventTestCase(BaseApiTest):

    @classmethod
    def setUpTestData(cls):
        cls.touristic_event_type = tourism_factory.TouristicEventTypeFactory()
        cls.place = tourism_factory.TouristicEventPlaceFactory(name="Here")
        cls.other_place = tourism_factory.TouristicEventPlaceFactory(name="Over here")
        cls.touristic_event1 = tourism_factory.TouristicEventFactory(
            name_fr="Exposition - Du vent, du sable et des étoiles",
            name_en="Wind and sand",
            description_fr="Cette exposition",
            description_en="An expo",
            description_teaser_fr="Un parcours dans la vie",
            geom=Point(0.77802, 43.047482, srid=4326),
            meeting_point="Bibliothèque municipale de Soueich, Mairie, 31550 Soueich",
            begin_date=datetime.date(2021, 7, 2),
            end_date=datetime.date(2021, 7, 3),
            accessibility="HA",
            target_audience="De 4 à 121 ans",
            published=True,
            bookable=True,
            type=cls.touristic_event_type,
            start_time=datetime.time(11, 20),
            end_time=datetime.time(12, 20),
            cancelled=True,
            place=cls.other_place,
            cancellation_reason=tourism_factory.CancellationReasonFactory(label_en="Fire", label_fr="Incendie")
        )
        cls.touristic_event1.portal.set([common_factory.TargetPortalFactory()])
        cls.touristic_event2 = tourism_factory.TouristicEventFactory(
            name_fr="expo",
            geom=Point(5.77802, 2.047482, srid=4326),
            published=True,
            bookable=False
        )
        cls.touristic_event2.portal.set([common_factory.TargetPortalFactory()])
        cls.path = core_factory.PathFactory.create(geom=LineString((0.77802, 43.047482), (0.77803, 43.047483), srid=4326))
        cls.trek = trek_factory.TrekFactory.create(
            paths=[(cls.path, 0, 1)],
            geom=cls.path.geom,
            published=True
        )
        cls.touristic_event3 = tourism_factory.TouristicEventFactory(
            name_fr="expooo",
            geom=Point(5.77802, 2.047482, srid=4326),
            published=False,
        )
        # Should not appear at any point
        cls.touristic_event4 = tourism_factory.TouristicEventFactory(
            deleted=True
        )
        cls.organizer = tourism_factory.TouristicEventOrganizerFactory(label='OrganizerA')
        cls.place_unpublished = tourism_factory.TouristicEventPlaceFactory(name="There")
        cls.touristic_event5 = tourism_factory.TouristicEventFactory(
            end_date=None,
            published=True,
            name="No end date",
            begin_date='2022-02-20',
            start_time="12:34",
            capacity=12,
            bookable=False,
            place=cls.place,
        )
        cls.touristic_event5.organizers.set([cls.organizer])
        cls.touristic_content = tourism_factory.TouristicContentFactory(geom=Point(0.77802, 43.047482, srid=4326))

    def test_touristic_event_list(self):
        response = self.get_touristicevent_list()
        self.assertEqual(response.json().get("count"), 3)

    @freeze_time("2022-02-02")
    def test_touristic_event_list_2(self):
        response = self.get_touristicevent_list()
        # Only two because past events are filter by default
        self.assertEqual(response.json().get("count"), 2)
        # Event with no end date is returned with begin date as end date
        self.assertEqual(response.json().get("results")[1]['end_date'], "2022-02-20")
        # start_time replaces meeting_time
        self.assertEqual(response.json().get("results")[1]['meeting_time'], "12:34:00")
        # capacity replaces participant_number
        self.assertEqual(response.json().get("results")[1]['participant_number'], '12')
        # Event with end date returns right end date
        self.assertEqual(response.json().get("results")[0]['end_date'], "2202-02-22")
        # Sorted by end date
        self.assertLessEqual(response.json().get("results")[0]['begin_date'], response.json().get("results")[1]['begin_date'])

    def test_touristic_event_dates_filters_1(self):
        response = self.get_touristicevent_list({'dates_before': '2200-01-01', 'dates_after': '1970-01-01'})
        self.assertEqual(response.json().get("count"), 3)

    def test_touristic_event_dates_filters_2(self):
        response = self.get_touristicevent_list({'dates_before': '2021-09-01', 'dates_after': '1970-01-01'})
        self.assertEqual(response.json().get("count"), 2)

    def test_touristic_event_dates_filters_3(self):
        response = self.get_touristicevent_list({'dates_after': '2021-07-03'})
        self.assertEqual(response.json().get("count"), 3)

    def test_touristic_event_dates_filters_4(self):
        response = self.get_touristicevent_list({'dates_after': '2021-07-04'})
        # Event 1 finishes on 3rd of july
        self.assertEqual(response.json().get("count"), 2)

    def test_touristic_event_organizer_filters_1(self):
        response = self.get_touristicevent_list({'organizer': 'tt'})
        self.assertEqual(response.json()['organizer'][0],
                         '“tt” is not a valid value.')

    def test_touristic_event_organizer_filters_2(self):
        response = self.get_touristicevent_list({'organizer': f'{self.organizer.pk}'})
        self.assertEqual(response.json().get("count"), 1)

    def test_touristic_event_cancelled_filter(self):
        response = self.get_touristicevent_list({'cancelled': 'True'})
        self.assertEqual(response.json().get("count"), 1)
        self.assertTrue(response.json().get("results")[0].get("cancelled"))
        self.assertEqual(response.json().get("results")[0].get("cancellation_reason").get('en'), "Fire")
        self.assertEqual(response.json().get("results")[0].get("cancellation_reason").get('fr'), "Incendie")
        response = self.get_touristicevent_list({'cancelled': 'False'})
        self.assertEqual(response.json().get("count"), 2)

    def test_touristic_event_detail(self):
        response = self.get_touristicevent_detail(self.touristic_event1.pk)
        self.check_structure_response(response, TOURISTIC_EVENT_DETAIL_JSON_STRUCTURE)

    def test_touristic_event_place_detail(self):
        response = self.get_touristiceventplace_detail(self.place.pk)
        self.check_structure_response(response, TOURISTIC_EVENT_PLACE_DETAIL_JSON_STRUCTURE)

    def test_touristic_event_organizer_detail(self):
        response = self.get_touristiceventorganizer_detail(self.organizer.pk)
        self.check_structure_response(response, TOURISTIC_EVENT_ORGANIZER_DETAIL_JSON_STRUCTURE)

    def test_touristicevent_near_trek(self):
        response = self.get_touristicevent_list({'near_trek': self.trek.pk})
        # Event 1 appears but not Event 2
        self.assertEqual(response.json().get("count"), 1)

    def test_touristicevent_near_touristicevent(self):
        response = self.get_touristicevent_list({'near_touristicevent': self.touristic_event3.pk})
        # Event 2 appears but not Event 1 (too far) or Event 3 (not published)
        self.assertEqual(response.json().get("count"), 1)

    def test_touristicevent_near_touristiccontent(self):
        response = self.get_touristicevent_list({'near_touristiccontent': self.touristic_content.pk})
        # Event 1 appears but not Event 2 (too far) or Event 3 (too far + not published)
        self.assertEqual(response.json().get("count"), 1)

    def test_touristic_event_portal_filters(self):
        response = self.get_touristicevent_list({'portals': self.touristic_event1.portal.first().pk})
        self.assertEqual(response.json().get("count"), 1)

    def test_touristic_event_type_filters(self):
        response = self.get_touristicevent_list({'types': self.touristic_event_type.pk})
        self.assertEqual(response.json().get("count"), 1)

    def test_touristic_event_bookable(self):
        response = self.get_touristicevent_list({'bookable': 'True'})
        self.assertEqual(response.json().get("count"), 1)
        response = self.get_touristicevent_list({'bookable': 'False'})
        self.assertEqual(response.json().get("count"), 2)

    def test_touristic_event_place_filter(self):
        response = self.get_touristicevent_list({'place': f"{self.place.pk},{self.other_place.pk}"})
        self.assertEqual(response.json().get("count"), 2)

    def test_touristic_event_place_not_valid_filter(self):
        response = self.get_touristicevent_list({'place': "100000"})
        self.assertEqual(response.json()['place'][0], "Select a valid choice. 100000 is not one of the available choices.")

    def test_touristic_event_place_list(self):
        response = self.get_touristiceventplace_list()
        self.assertEqual(response.json().get("count"), 2)


class TouristicEventTypeTestCase(BaseApiTest):
    @classmethod
    def setUpTestData(cls):
        cls.touristic_event_type = tourism_factory.TouristicEventTypeFactory(type_fr="Cool", type_en="af")
        cls.touristic_event = tourism_factory.TouristicEventFactory(
            published=True,
            type=cls.touristic_event_type
        )

    def test_touristic_event_type_list(self):
        response = self.get_touristiceventtype_list()
        self.assertEqual(response.json().get("count"), 1)
        self.assertEqual(len(response.json().get("results")), 1)

    def test_touristic_event_type_detail(self):
        response = self.get_touristiceventtype_detail(self.touristic_event_type.pk)
        self.check_structure_response(response, TOURISTIC_EVENT_TYPE_DETAIL_JSON_STRUCTURE)


class TouristicEventTypeFilterTestCase(BaseApiTest):
    """ Test filtering depending on published, deleted content for touristic event types """

    @classmethod
    def setUpTestData(cls):
        # ### Build all type scenarios
        #  Type with no content -> don't send it
        cls.type_with_no_content = tourism_factory.TouristicEventTypeFactory()
        #  Type with no published content -> don't send it
        cls.type_with_no_published_content = tourism_factory.TouristicEventTypeFactory()
        cls.not_published_event = tourism_factory.TouristicEventFactory(
            published=False,
            type=cls.type_with_no_published_content
        )
        # Type with no content that was not deleted -> don't send it
        cls.type_with_only_deleted_content = tourism_factory.TouristicEventTypeFactory()
        cls.deleted_event = tourism_factory.TouristicEventFactory(
            deleted=True,
            type=cls.type_with_only_deleted_content
        )
        # Type with published and not deleted content -> send it
        cls.type_with_published_and_not_deleted_content = tourism_factory.TouristicEventTypeFactory()
        cls.published_and_not_deleted_event = tourism_factory.TouristicEventFactory(
            deleted=False,
            published_en=True,
            type=cls.type_with_published_and_not_deleted_content
        )
        # Type with published_fr and not deleted content -> send it when language=fr
        cls.type_with_published_and_not_deleted_content_with_lang = tourism_factory.TouristicEventTypeFactory()
        cls.published_and_not_deleted_event_with_lang = tourism_factory.TouristicEventFactory(
            deleted=False,
            published_fr=True,
            type=cls.type_with_published_and_not_deleted_content_with_lang
        )

    def test_touristic_event_type_list_returns_published(self):
        """ Assert API returns only types with published events
        """
        response = self.get_touristiceventtype_list()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]
        self.assertNotIn(self.type_with_no_content.pk, all_ids)
        self.assertNotIn(self.type_with_no_published_content.pk, all_ids)
        self.assertNotIn(self.type_with_only_deleted_content.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_content.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_content_with_lang.pk, all_ids)

    def test_touristic_event_type_list_returns_published_in_language(self):
        """ Assert API returns only published events in specified language
        """
        response = self.get_touristiceventtype_list({'language': 'fr'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertNotIn(self.type_with_no_content.pk, all_ids)
        self.assertNotIn(self.type_with_no_published_content.pk, all_ids)
        self.assertNotIn(self.type_with_only_deleted_content.pk, all_ids)
        self.assertNotIn(self.type_with_published_and_not_deleted_content.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_content_with_lang.pk, all_ids)


class TouristicEventTypeFilterByPortalTestCase(TouristicEventTypeFilterTestCase):
    """ Test filtering depending on portal for touristic event types """

    @classmethod
    def setUpTestData(cls):
        # ### Duplicate all type scenarios based on portal
        super().setUpTestData()
        cls.queried_portal = common_factory.TargetPortalFactory()
        cls.other_portal = common_factory.TargetPortalFactory()
        #  Type with no content on this portal -> don't send it
        cls.event_on_other_portal = tourism_factory.TouristicEventFactory(
            published=False,
            type=cls.type_with_no_content,
        )
        cls.event_on_other_portal.portal.set([cls.other_portal])
        #  Type with no published content on portal-> don't send it
        cls.not_published_event.portal.set([cls.queried_portal])
        cls.published_event_on_other_portal = tourism_factory.TouristicEventFactory(
            published_en=True,
            type=cls.type_with_no_published_content,
        )
        cls.published_event_on_other_portal.portal.set([cls.other_portal])
        # Type with no content on portal that was not deleted -> don't send it
        cls.deleted_event.portal.set([cls.queried_portal])
        cls.not_deleted_event_on_other_portal = tourism_factory.TouristicEventFactory(
            deleted=False,
            type=cls.type_with_only_deleted_content,
        )
        cls.not_deleted_event_on_other_portal.portal.set([cls.other_portal])

    def test_touristic_event_type_list_returns_published(self):
        """ Assert API returns only types with published events on portal
        """
        response = self.get_touristiceventtype_list({'portals': self.queried_portal.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertNotIn(self.type_with_no_content.pk, all_ids)
        self.assertNotIn(self.type_with_no_published_content.pk, all_ids)
        self.assertNotIn(self.type_with_only_deleted_content.pk, all_ids)
        # Didn't set portal on these ones yet
        self.assertNotIn(self.type_with_published_and_not_deleted_content.pk, all_ids)
        self.assertNotIn(self.type_with_published_and_not_deleted_content_with_lang.pk, all_ids)

    def test_touristic_event_type_list_returns_published_2(self):
        """ Assert API returns only types with published events on portal
        """
        # Type with published and not deleted content on portal -> send it
        self.published_and_not_deleted_event.portal.set([self.queried_portal])
        # Type with published_fr and not deleted content on portal -> send it when language=fr
        self.published_and_not_deleted_event_with_lang.portal.set([self.queried_portal])
        response = self.get_touristiceventtype_list({'portals': self.queried_portal.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertNotIn(self.type_with_no_content.pk, all_ids)
        self.assertNotIn(self.type_with_no_published_content.pk, all_ids)
        self.assertNotIn(self.type_with_only_deleted_content.pk, all_ids)
        # Portal is set this time
        self.assertIn(self.type_with_published_and_not_deleted_content.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_content_with_lang.pk, all_ids)


class NearOutdoorFilterTestCase(BaseApiTest):
    """ Test near_outdoorsite and near_outdoorcourse filter on routes """

    @classmethod
    def setUpTestData(cls):
        cls.site = outdoor_factory.SiteFactory(
            published_fr=True,
            geom=GeometryCollection(Point(100.1, 100.1, srid=2154))
        )
        cls.course = outdoor_factory.CourseFactory(
            published_fr=True,
            geom=GeometryCollection(Point(100, 100, srid=2154)),
            parent_sites=[cls.site]
        )
        # trek1 is nearby
        cls.path1 = core_factory.PathFactory.create(geom=LineString((0.0, 0.0), (1.0, 1.0), srid=2154))
        cls.trek1 = trek_factory.TrekFactory.create(
            paths=[(cls.path1, 0, 1)],
            geom=cls.path1.geom,
            published_fr=True
        )
        # trek2 is far away
        cls.path2 = core_factory.PathFactory.create(geom=LineString((9999.0, 9999.0), (9999.0, 9998.0), srid=2154))
        cls.trek2 = trek_factory.TrekFactory.create(
            paths=[(cls.path2, 0, 1)],
            geom=cls.path2.geom,
            published_fr=True
        )
        # event1 is nearby
        cls.touristic_event1 = tourism_factory.TouristicEventFactory(
            geom=(Point(0.5, 0.5, srid=2154)),
            published=True,
        )
        # event2 is far away
        cls.touristic_event2 = tourism_factory.TouristicEventFactory(
            geom=(Point(9999.5, 9999.5, srid=2154)),
            published=True,
        )
        # content1 is nearby
        cls.touristic_content1 = tourism_factory.TouristicContentFactory(
            geom=(Point(0.5, 0.5, srid=2154)),
            published=True,
        )
        # content2 is far away
        cls.touristic_content2 = tourism_factory.TouristicContentFactory(
            geom=(Point(9999.5, 9999.5, srid=2154)),
            published=True,
        )
        # site1 is nearby
        cls.site1 = outdoor_factory.SiteFactory(
            published_fr=True,
            geom=GeometryCollection(Point(100.5, 100.5, srid=2154))
        )
        # site2 is far away
        cls.site2 = outdoor_factory.SiteFactory(
            published_fr=True,
            geom=GeometryCollection(Point(9999.5, 9999.5, srid=2154))
        )
        # course1 is nearby
        cls.course1 = outdoor_factory.CourseFactory(
            published_fr=True,
            geom=GeometryCollection(Point(100.5, 100.5, srid=2154)),
            parent_sites=[cls.site1]
        )
        # course2 is far away
        cls.course2 = outdoor_factory.CourseFactory(
            published_fr=True,
            geom=GeometryCollection(Point(9999.5, 9999.5, srid=2154)),
            parent_sites=[cls.site2]

        )
        # poi 1 is nearby
        cls.poi1 = trek_factory.POIFactory(
            paths=[(cls.path1, 0, 0)],
            geom=cls.path1.geom
        )
        # poi 2 isfar away
        cls.poi2 = trek_factory.POIFactory(
            paths=[(cls.path2, 0, 0)],
            geom=cls.path2.geom
        )
        # info desk 1 is nearby
        cls.info_desk1 = tourism_factory.InformationDeskFactory(
            geom=Point(0.0, 0.0, srid=2154)
        )
        # info desk 2 is far away
        cls.info_desk2 = tourism_factory.InformationDeskFactory(
            geom=Point(9999.5, 9999.5, srid=2154)
        )
        cls.trek1.information_desks.set([cls.info_desk1])
        cls.trek2.information_desks.set([cls.info_desk2])
        # sensitive area 1 is nearby
        cls.sensitivearea1 = sensitivity_factory.SensitiveAreaFactory(
            geom=Polygon(
                (
                    (0, 0),
                    (0, 1),
                    (1, 1),
                    (0, 0)
                ),
                srid=2154
            )
        )
        # sensitive area 2 is nearby
        cls.sensitivearea2 = sensitivity_factory.SensitiveAreaFactory(
            geom=Polygon(
                (
                    (9999, 9999),
                    (9999, 9998),
                    (9998, 9998),
                    (9999, 9999)
                ),
                srid=2154
            )
        )

    def test_trek_near_outdoorcourse(self):
        response = self.get_trek_list({'near_outdoorcourse': self.course.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.trek1.pk)

    def test_trek_near_outdoorsite(self):
        response = self.get_trek_list({'near_outdoorsite': self.site.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.trek1.pk)

    def test_touristicevent_near_outdoorcourse(self):
        response = self.get_touristicevent_list({'near_outdoorcourse': self.course.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.touristic_event1.pk)

    def test_touristicevent_near_outdoorsite(self):
        response = self.get_touristicevent_list({'near_outdoorsite': self.site.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.touristic_event1.pk)

    def test_touristiccontent_near_outdoorcourse(self):
        response = self.get_touristiccontent_list({'near_outdoorcourse': self.course.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.touristic_content1.pk)

    def test_touristiccontent_near_outdoorsite(self):
        response = self.get_touristiccontent_list({'near_outdoorsite': self.site.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.touristic_content1.pk)

    def test_outdoorcourse_near_outdoorcourse(self):
        response = self.get_course_list({'near_outdoorcourse': self.course.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.course1.pk)

    def test_outdoorcourse_near_outdoorsite(self):
        response = self.get_course_list({'near_outdoorsite': self.site.pk})
        self.assertEqual(response.json()["count"], 2)
        self.assertEqual(response.json()["results"][0]["id"], self.course.pk)
        self.assertEqual(response.json()["results"][1]["id"], self.course1.pk)

    def test_outdoorsite_near_outdoorcourse(self):
        response = self.get_site_list({'near_outdoorcourse': self.course.pk})
        self.assertEqual(response.json()["count"], 2)
        self.assertEqual(response.json()["results"][0]["id"], self.site.pk)
        self.assertEqual(response.json()["results"][1]["id"], self.site1.pk)

    def test_outdoorsite_near_outdoorsite(self):
        response = self.get_site_list({'near_outdoorsite': self.site.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.site1.pk)

    def test_poi_near_outdoorcourse(self):
        response = self.get_poi_list({'near_outdoorcourse': self.course.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.poi1.pk)

    def test_poi_near_outdoorsite(self):
        response = self.get_poi_list({'near_outdoorsite': self.site.pk})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.poi1.pk)

    def test_sensitivearea_near_outdoorcourse(self):
        response = self.get_sensitivearea_list({'near_outdoorcourse': self.course.pk, 'period': 'any'})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.sensitivearea1.pk)

    def test_sensitivearea_near_outdoorsite(self):
        response = self.get_sensitivearea_list({'near_outdoorsite': self.site.pk, 'period': 'any'})
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(response.json()["results"][0]["id"], self.sensitivearea1.pk)


class NearbyContentFilterTestCase(BaseApiTest):

    def test_list_objects_filtered_by_near_target(self):

        get_list_funcs = [
            self.get_site_list,
            self.get_course_list,
            self.get_trek_list,
            self.get_signage_list,
            self.get_service_list,
            self.get_poi_list,
            self.get_touristiccontent_list,
            self.get_touristicevent_list,
            self.get_sensitivearea_list,
            self.get_infrastructure_list,
        ]

        targets = {
            "near_trek": self.treks[0].pk,
            "near_touristiccontent": self.content.pk,
            "near_touristicevent": self.event.pk,
            "near_outdoorsite": self.site.pk,
            "near_outdoorcourse": self.course.pk,
        }

        for list_func in get_list_funcs:
            for filter_name, target_pk in targets.items():
                with self.subTest(list_func=list_func.__name__, filter=filter_name):
                    response = list_func(params={filter_name: target_pk})
                    self.assertEqual(response.status_code, 200)


class UpdateOrCreateDatesFilterTestCase(BaseApiTest):

    @classmethod
    def setUpTestData(cls):
        cls.path1 = core_factory.PathFactory()
        cls.path2 = core_factory.PathFactory()
        cls.user = SuperUserFactory()

    def setUp(self):
        self.client.force_login(self.user)

    def test_updated_after_filter(self):
        two_years_ago = (timezone.now() - relativedelta(years=2)).date()
        response = self.get_path_list({'updated_after': two_years_ago})
        self.assertEqual(response.json().get("count"), 2)

    def test_updated_after_filter_2(self):
        in_two_years = (timezone.now() + relativedelta(years=2)).date()
        response = self.get_path_list({'updated_after': in_two_years})
        self.assertEqual(response.json().get("count"), 0)

    def test_updated_before_filter(self):
        two_years_ago = (timezone.now() - relativedelta(years=2)).date()
        response = self.get_path_list({'updated_before': two_years_ago})
        self.assertEqual(response.json().get("count"), 0)

    def test_updated_before_filter_2(self):
        in_two_years = (timezone.now() + relativedelta(years=2)).date()
        response = self.get_path_list({'updated_before': in_two_years})
        self.assertEqual(response.json().get("count"), 2)

    def test_created_after_filter(self):
        two_years_ago = (timezone.now() - relativedelta(years=2)).date()
        response = self.get_path_list({'created_after': two_years_ago})
        self.assertEqual(response.json().get("count"), 2)

    def test_created_after_filter_2(self):
        in_two_years = (timezone.now() + relativedelta(years=2)).date()
        response = self.get_path_list({'created_after': in_two_years})
        self.assertEqual(response.json().get("count"), 0)

    def test_created_before_filter(self):
        two_years_ago = (timezone.now() - relativedelta(years=2)).date()
        response = self.get_path_list({'created_before': two_years_ago})
        self.assertEqual(response.json().get("count"), 0)

    def test_created_before_filter_2(self):
        in_two_years = (timezone.now() + relativedelta(years=2)).date()
        response = self.get_path_list({'created_before': in_two_years})
        self.assertEqual(response.json().get("count"), 2)


class RootSitesOnlyFilterTestCase(BaseApiTest):

    @classmethod
    def setUpTestData(cls):
        cls.site_root1 = outdoor_factory.SiteFactory()
        cls.site_root2 = outdoor_factory.SiteFactory()
        cls.site_child1 = outdoor_factory.SiteFactory(
            parent=cls.site_root1
        )
        cls.site_child2 = outdoor_factory.SiteFactory(
            parent=cls.site_child1
        )

    def test_return_all_sites_with_no_filter(self):
        response = self.get_site_list()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 4)

    def test_root_sites_only_filter(self):
        response = self.get_site_list({'root_sites_only': "true"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_sites = response.json()['results']
        all_ids = []
        for type in returned_sites:
            all_ids.append(type['id'])
        self.assertIn(self.site_root1.pk, all_ids)
        self.assertIn(self.site_root2.pk, all_ids)
        self.assertNotIn(self.site_child1.pk, all_ids)
        self.assertNotIn(self.site_child2.pk, all_ids)


class SitesTypesFilterTestCase(BaseApiTest):

    @classmethod
    def setUpTestData(cls):
        cls.site1 = outdoor_factory.SiteFactory()
        cls.site2 = outdoor_factory.SiteFactory()
        cls.site3 = outdoor_factory.SiteFactory()

    def test_sites_type_filter_1(self):
        response = self.get_site_list({'types': self.site1.type.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_sites = response.json()['results']
        all_ids = []
        for type in returned_sites:
            all_ids.append(type['id'])
        self.assertIn(self.site1.pk, all_ids)
        self.assertNotIn(self.site2.pk, all_ids)
        self.assertNotIn(self.site3.pk, all_ids)

    def test_sites_type_filter_2(self):
        response = self.get_site_list({'types': f"{self.site2.type.pk},{self.site3.type.pk}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_sites = response.json()['results']
        all_ids = []
        for type in returned_sites:
            all_ids.append(type['id'])
        self.assertNotIn(self.site1.pk, all_ids)
        self.assertIn(self.site2.pk, all_ids)
        self.assertIn(self.site3.pk, all_ids)


class SitesLabelsFilterTestCase(BaseApiTest):

    @classmethod
    def setUpTestData(cls):
        cls.label_published = common_factory.LabelFactory(published=True)
        cls.label_unpublished = common_factory.LabelFactory(published=False)
        cls.site1 = outdoor_factory.SiteFactory()
        cls.site1.labels.add(cls.label_published)
        cls.site2 = outdoor_factory.SiteFactory()
        cls.site2.labels.add(cls.label_unpublished)
        cls.site3 = outdoor_factory.SiteFactory()

    def test_sites_label_filter_1(self):
        response = self.get_site_list({'labels': self.label_published.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_sites = response.json()['results']
        all_ids = []
        for type in returned_sites:
            all_ids.append(type['id'])
        self.assertIn(self.site1.pk, all_ids)
        self.assertNotIn(self.site2.pk, all_ids)
        self.assertNotIn(self.site3.pk, all_ids)

    def test_sites_label_filter_2(self):
        response = self.get_site_list({'labels': f"{self.label_published.pk},{self.label_unpublished.pk}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_sites = response.json()['results']
        all_ids = []
        for type in returned_sites:
            all_ids.append(type['id'])
        self.assertIn(self.site1.pk, all_ids)
        self.assertIn(self.site2.pk, all_ids)
        self.assertNotIn(self.site3.pk, all_ids)

    def test_sites_labels_exclude_filter(self):
        response = self.get_site_list({'labels_exclude': self.label_published.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 2)
        self.assertSetEqual({result['id'] for result in json_response.get('results')},
                            {self.site2.pk, self.site3.pk})

        site_a = outdoor_factory.SiteFactory()
        label = common_factory.LabelFactory.create()
        site_a.labels.add(label, self.label_published)

        response = self.get_site_list({'labels_exclude': self.label_published.pk})
        #  test response code
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 2)
        self.assertSetEqual({result['id'] for result in json_response.get('results')},
                            {self.site2.pk, self.site3.pk})

        site_b = outdoor_factory.SiteFactory()
        label_2 = common_factory.LabelFactory.create()
        site_b.labels.add(label, label_2)

        response = self.get_site_list({'labels_exclude': f'{self.label_published.pk},{label.pk}'})
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 2)
        self.assertSetEqual({result['id'] for result in json_response.get('results')},
                            {self.site2.pk, self.site3.pk})

        response = self.get_site_list({'labels_exclude': label_2.pk})
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(len(json_response.get('results')), 4)
        self.assertSetEqual({result['id'] for result in json_response.get('results')},
                            {self.site1.pk, self.site2.pk, self.site3.pk, site_a.pk})

    def test_sites_label_filter_published(self):
        response = self.get_site_list()
        self.assertEqual(response.status_code, 200)
        results = response.json()['results']
        all_labels = [result['labels'] for result in results]

        self.assertIn([self.label_published.pk], all_labels)
        self.assertNotIn([self.label_unpublished.pk], all_labels)


class CoursesTypesFilterTestCase(BaseApiTest):

    @classmethod
    def setUpTestData(cls):
        cls.course1 = outdoor_factory.CourseFactory()
        cls.course2 = outdoor_factory.CourseFactory()
        cls.course3 = outdoor_factory.CourseFactory()

    def test_courses_type_filter_1(self):
        response = self.get_course_list({'types': self.course1.type.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_courses = response.json()['results']
        all_ids = []
        for type in returned_courses:
            all_ids.append(type['id'])
        self.assertIn(self.course1.pk, all_ids)
        self.assertNotIn(self.course2.pk, all_ids)
        self.assertNotIn(self.course3.pk, all_ids)

    def test_courses_type_filter_2(self):
        response = self.get_course_list({'types': f"{self.course2.type.pk},{self.course3.type.pk}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_courses = response.json()['results']
        all_ids = []
        for type in returned_courses:
            all_ids.append(type['id'])
        self.assertNotIn(self.course1.pk, all_ids)
        self.assertIn(self.course2.pk, all_ids)
        self.assertIn(self.course3.pk, all_ids)


class TouristicContentTypeFilterTestCase(BaseApiTest):

    @classmethod
    def setUpTestData(cls):
        cls.category1 = tourism_factory.TouristicContentCategoryFactory(label="POI")
        cls.category2 = tourism_factory.TouristicContentCategoryFactory(label="Food")
        cls.content_deleted = tourism_factory.TouristicContentFactory(
            category=cls.category1,
            deleted=True
        )
        cls.content_not_published = tourism_factory.TouristicContentFactory(
            category=cls.category1,
            published=False,
            published_fr=False,
        )
        cls.content_published_en = tourism_factory.TouristicContentFactory(
            category=cls.category1,
            published_fr=False,
            published_en=True,
        )
        cls.portal = tourism_factory.TargetPortalFactory()
        cls.content_published_es_portal = tourism_factory.TouristicContentFactory(
            category=cls.category1,
            published_fr=False,
            published_en=False,
            published_es=True,
        )
        cls.content_published_es_portal.portal.set([cls.portal])
        cls.content_cat2 = tourism_factory.TouristicContentFactory(
            category=cls.category2,
            published_fr=False,
            published_en=True,
        )

    def assert_types_returned_in_first_category(self, response, content_in_list, content_not_in_list):
        self.assertEqual(response.status_code, 200)
        self.assert_returned_types(1, response, content_in_list, content_not_in_list)
        self.assert_returned_types(2, response, content_in_list, content_not_in_list)

    def assert_returned_types(self, i, response, content_in_list, content_not_in_list):
        returned_types = response.json()['results'][0]['types'][i - 1]['values']
        self.assertEqual(len(returned_types), len(content_in_list))
        all_ids = [type['id'] for type in returned_types]

        # type1
        if i == 1:
            for content in content_in_list:
                self.assertIn(content.type1.all()[0].pk, all_ids)
            for content in content_not_in_list:
                self.assertNotIn(content.type1.all()[0].pk, all_ids)
        # type2
        elif i == 2:
            for content in content_in_list:
                self.assertIn(content.type2.all()[0].pk, all_ids)
            for content in content_not_in_list:
                self.assertNotIn(content.type2.all()[0].pk, all_ids)

    def test_returned_published_not_deleted(self):
        response = self.get_touristiccontentcategory_list()
        types_in_list = [self.content_published_en, self.content_published_es_portal]
        types_not_in_list = [self.content_deleted, self.content_not_published, self.content_cat2]
        self.assert_types_returned_in_first_category(response, types_in_list, types_not_in_list)

    def test_returned_published_not_deleted_by_lang(self):
        response = self.get_touristiccontentcategory_list({'language': 'en'})
        types_in_list = [self.content_published_en]
        types_not_in_list = [self.content_deleted, self.content_not_published, self.content_published_es_portal, self.content_cat2]
        self.assert_types_returned_in_first_category(response, types_in_list, types_not_in_list)

    def test_returned_published_not_deleted_by_portal(self):
        response = self.get_touristiccontentcategory_list({'portals': self.portal.pk})
        types_in_list = [self.content_published_es_portal]
        types_not_in_list = [self.content_deleted, self.content_not_published, self.content_published_en, self.content_cat2]
        self.assert_types_returned_in_first_category(response, types_in_list, types_not_in_list)

    def test_returned_published_not_deleted_by_portal_and_lang(self):
        response = self.get_touristiccontentcategory_list({'portals': self.portal.pk, 'language': 'es'})
        types_in_list = [self.content_published_es_portal]
        types_not_in_list = [self.content_deleted, self.content_not_published, self.content_published_en, self.content_cat2]
        self.assert_types_returned_in_first_category(response, types_in_list, types_not_in_list)


class SiteTypeFilterTestCase(BaseApiTest):
    """ Test filtering depending on published, deleted content for outdoor site types
    """

    @classmethod
    def setUpTestData(cls):
        # ### Build all type scenarios
        #  Type with no site -> don't send it
        cls.type_with_no_site = outdoor_factory.SiteTypeFactory()
        #  Type with no published site -> don't send it
        cls.type_with_no_published_site = outdoor_factory.SiteTypeFactory()
        cls.not_published_site = outdoor_factory.SiteFactory(
            published=False,
            type=cls.type_with_no_published_site
        )
        # Type with published and not deleted site -> send it
        cls.type_with_published_and_not_deleted_site = outdoor_factory.SiteTypeFactory()
        cls.published_and_not_deleted_site = outdoor_factory.SiteFactory(
            published_en=True,
            type=cls.type_with_published_and_not_deleted_site
        )
        # Type with published_fr and not deleted site -> send it when language=fr
        cls.type_with_published_and_not_deleted_site_with_lang = outdoor_factory.SiteTypeFactory()
        cls.published_and_not_deleted_site_with_lang = outdoor_factory.SiteFactory(
            published_fr=True,
            type=cls.type_with_published_and_not_deleted_site_with_lang
        )

    def test_sites_type_list_returns_published(self):
        """ Assert API returns only types with published sites
        """
        response = self.get_sitetype_list()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertNotIn(self.type_with_no_site.pk, all_ids)
        self.assertNotIn(self.type_with_no_published_site.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_site.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_site_with_lang.pk, all_ids)

    def test_sites_type_list_returns_published_in_language(self):
        """ Assert API returns only published sites in specified language
        """
        response = self.get_sitetype_list({'language': 'fr'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertNotIn(self.type_with_no_site.pk, all_ids)
        self.assertNotIn(self.type_with_no_published_site.pk, all_ids)
        self.assertNotIn(self.type_with_published_and_not_deleted_site.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_site_with_lang.pk, all_ids)


class SiteTypeFilterTestCaseByPortal(SiteTypeFilterTestCase):
    """ Test filtering depending on portal for outdoor site types
    """

    @classmethod
    def setUpTestData(cls):
        # ### Duplicate all type scenarios based on portal
        super().setUpTestData()
        cls.queried_portal = common_factory.TargetPortalFactory()
        cls.other_portal = common_factory.TargetPortalFactory()
        #  Type with no site on this portal -> don't send it
        cls.type_with_no_site = outdoor_factory.SiteTypeFactory()
        cls.site_on_other_portal = outdoor_factory.SiteFactory(
            published=False,
            type=cls.type_with_no_site,
        )
        cls.site_on_other_portal.portal.set([cls.other_portal])
        #  Type with no published site on portal-> don't send it
        cls.not_published_site.portal.set([cls.queried_portal])
        cls.published_site_on_other_portal = outdoor_factory.SiteFactory(
            published_en=True,
            type=cls.type_with_no_published_site,
        )
        cls.published_site_on_other_portal.portal.set([cls.other_portal])
        # Type with no site on portal that was not deleted -> don't send it
        cls.not_deleted_site_on_other_portal = outdoor_factory.SiteFactory(
            type=cls.type_with_no_published_site,
        )
        cls.not_deleted_site_on_other_portal.portal.set([cls.other_portal])

    def test_sites_type_list_returns_published(self):
        """ Assert API returns only types with published site on portal
        """
        response = self.get_sitetype_list({'portals': self.queried_portal.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertNotIn(self.type_with_no_site.pk, all_ids)
        self.assertNotIn(self.type_with_no_published_site.pk, all_ids)
        # Didn't set portal on these ones yet
        self.assertNotIn(self.type_with_published_and_not_deleted_site.pk, all_ids)
        self.assertNotIn(self.type_with_published_and_not_deleted_site_with_lang.pk, all_ids)

    def test_sites_type_list_returns_published_2(self):
        """ Assert API returns only types with published sites on portal
        """
        # Type with published and not deleted site on portal -> send it
        self.published_and_not_deleted_site.portal.set([self.queried_portal])
        # Type with published_fr and not deleted site on portal -> send it when language=fr
        self.published_and_not_deleted_site_with_lang.portal.set([self.queried_portal])
        response = self.get_sitetype_list({'portals': self.queried_portal.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertNotIn(self.type_with_no_site.pk, all_ids)
        self.assertNotIn(self.type_with_no_published_site.pk, all_ids)
        # Portal is set this time
        self.assertIn(self.type_with_published_and_not_deleted_site.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_site_with_lang.pk, all_ids)


class CourseTypeFilterTestCase(BaseApiTest):
    """ Test filtering depending on published, deleted content for outdoor course types
    """

    @classmethod
    def setUpTestData(cls):
        # ### Build all type scenarios
        #  Type with no course -> don't send it
        cls.type_with_no_course = outdoor_factory.CourseTypeFactory()
        #  Type with no published course -> don't send it
        cls.type_with_no_published_course = outdoor_factory.CourseTypeFactory()
        cls.not_published_course = outdoor_factory.CourseFactory(
            published=False,
            type=cls.type_with_no_published_course
        )
        # Type with published and not deleted course -> send it
        cls.type_with_published_and_not_deleted_course = outdoor_factory.CourseTypeFactory()
        cls.published_and_not_deleted_course = outdoor_factory.CourseFactory(
            published_en=True,
            type=cls.type_with_published_and_not_deleted_course
        )
        # Type with published_fr and not deleted course -> send it when language=fr
        cls.type_with_published_and_not_deleted_course_with_lang = outdoor_factory.CourseTypeFactory()
        cls.published_and_not_deleted_course_with_lang = outdoor_factory.CourseFactory(
            published_fr=True,
            type=cls.type_with_published_and_not_deleted_course_with_lang
        )

    def test_course_type_list_returns_published(self):
        """ Assert API returns only types with published course
        """
        response = self.get_coursetype_list()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertNotIn(self.type_with_no_course.pk, all_ids)
        self.assertNotIn(self.type_with_no_published_course.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_course.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_course_with_lang.pk, all_ids)

    def test_course_type_list_returns_published_in_language(self):
        """ Assert API returns only published course in specified language
        """
        response = self.get_coursetype_list({'language': 'fr'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertNotIn(self.type_with_no_course.pk, all_ids)
        self.assertNotIn(self.type_with_no_published_course.pk, all_ids)
        self.assertNotIn(self.type_with_published_and_not_deleted_course.pk, all_ids)
        self.assertIn(self.type_with_published_and_not_deleted_course_with_lang.pk, all_ids)


class OutdoorFilterByRatingsTestCase(BaseApiTest):
    """ Test filtering on ratings for outdoor course
    """

    @classmethod
    def setUpTestData(cls):
        cls.site1 = outdoor_factory.SiteFactory()
        cls.site2 = outdoor_factory.SiteFactory()
        cls.rating_scale = outdoor_factory.RatingScaleFactory(practice=cls.site1.practice)
        cls.rating1 = outdoor_factory.RatingFactory(scale=cls.rating_scale)
        cls.rating2 = outdoor_factory.RatingFactory(scale=cls.rating_scale)
        cls.site1.ratings.set([cls.rating1])
        cls.site2.ratings.set([cls.rating2])
        cls.course1 = outdoor_factory.CourseFactory()
        cls.course2 = outdoor_factory.CourseFactory()
        cls.course1.ratings.set([cls.rating1])
        cls.course2.ratings.set([cls.rating2])

    def test_site_list_ratings_filter(self):
        response = self.get_site_list({'ratings': self.rating1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_sites = response.json()['results']
        all_ids = []
        for site in returned_sites:
            all_ids.append(site['id'])
        self.assertIn(self.site1.pk, all_ids)
        self.assertNotIn(self.site2.pk, all_ids)

    def test_site_list_ratings_filter2(self):
        response = self.get_site_list({'ratings': self.rating2.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_sites = response.json()['results']
        all_ids = []
        for site in returned_sites:
            all_ids.append(site['id'])
        self.assertIn(self.site2.pk, all_ids)
        self.assertNotIn(self.site1.pk, all_ids)

    def test_site_list_ratings_filter3(self):
        response = self.get_site_list({'ratings': f"{self.rating1.pk},{self.rating2.pk}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_sites = response.json()['results']
        all_ids = []
        for site in returned_sites:
            all_ids.append(site['id'])
        self.assertIn(self.site1.pk, all_ids)
        self.assertIn(self.site2.pk, all_ids)

    def test_course_list_ratings_filter(self):
        response = self.get_course_list({'ratings': f"{self.rating1.pk},{self.rating2.pk}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        returned_sites = response.json()['results']
        all_ids = []
        for site in returned_sites:
            all_ids.append(site['id'])
        self.assertIn(self.course1.pk, all_ids)
        self.assertIn(self.course2.pk, all_ids)

    def test_course_list_ratings_filter2(self):
        response = self.get_course_list({'ratings': self.rating2.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_sites = response.json()['results']
        all_ids = []
        for site in returned_sites:
            all_ids.append(site['id'])
        self.assertNotIn(self.course1.pk, all_ids)
        self.assertIn(self.course2.pk, all_ids)


class OutdoorFilterBySuperPracticesTestCase(BaseApiTest):
    """ Test APIV2 filtering on ratings on sites
    """

    @classmethod
    def setUpTestData(cls):
        cls.practice1 = outdoor_factory.PracticeFactory()
        cls.practice2 = outdoor_factory.PracticeFactory()
        cls.practice3 = outdoor_factory.PracticeFactory()
        cls.practice3 = outdoor_factory.PracticeFactory()
        cls.practice4 = outdoor_factory.PracticeFactory()
        cls.site1 = outdoor_factory.SiteFactory(practice=cls.practice1)
        cls.site2 = outdoor_factory.SiteFactory(practice=cls.practice2, parent=cls.site1)
        cls.site3 = outdoor_factory.SiteFactory(practice=cls.practice3, parent=cls.site2)
        cls.site4 = outdoor_factory.SiteFactory(practice=cls.practice4, parent=cls.site2)

    def test_filter_practice_in_tree_hierarchy(self):
        response = self.get_site_list({'practices_in_hierarchy': self.practice1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertIn(self.site1.pk, all_ids)
        self.assertNotIn(self.site2.pk, all_ids)
        self.assertNotIn(self.site3.pk, all_ids)
        self.assertNotIn(self.site4.pk, all_ids)

    def test_filter_practice_in_tree_hierarchy2(self):
        response = self.get_site_list({'practices_in_hierarchy': self.practice3.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertIn(self.site1.pk, all_ids)
        self.assertIn(self.site2.pk, all_ids)
        self.assertIn(self.site3.pk, all_ids)
        self.assertNotIn(self.site4.pk, all_ids)


class OutdoorFilterBySuperRatingsTestCase(BaseApiTest):
    """ Test APIV2 filtering on ratings on sites in hierarchy
    """

    @classmethod
    def setUpTestData(cls):
        cls.site1 = outdoor_factory.SiteFactory()
        cls.rating_scale = outdoor_factory.RatingScaleFactory(practice=cls.site1.practice)
        cls.rating1 = outdoor_factory.RatingFactory(scale=cls.rating_scale)
        cls.rating2 = outdoor_factory.RatingFactory(scale=cls.rating_scale)
        cls.rating3 = outdoor_factory.RatingFactory(scale=cls.rating_scale)
        cls.rating4 = outdoor_factory.RatingFactory(scale=cls.rating_scale)
        cls.site2 = outdoor_factory.SiteFactory(parent=cls.site1)
        cls.site3 = outdoor_factory.SiteFactory(parent=cls.site2)
        cls.site4 = outdoor_factory.SiteFactory(parent=cls.site2)
        cls.site1.ratings.set([cls.rating1])
        cls.site2.ratings.set([cls.rating2])
        cls.site3.ratings.set([cls.rating3])
        cls.site4.ratings.set([cls.rating4])

    def test_filter_ratings_in_tree_hierarchy(self):
        response = self.get_site_list({'ratings_in_hierarchy': self.rating1.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertIn(self.site1.pk, all_ids)
        self.assertNotIn(self.site2.pk, all_ids)
        self.assertNotIn(self.site3.pk, all_ids)
        self.assertNotIn(self.site4.pk, all_ids)

    def test_filter_ratings_in_tree_hierarchy2(self):
        response = self.get_site_list({'ratings_in_hierarchy': self.rating3.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 3)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertIn(self.site1.pk, all_ids)
        self.assertIn(self.site2.pk, all_ids)
        self.assertIn(self.site3.pk, all_ids)
        self.assertNotIn(self.site4.pk, all_ids)

    def test_filter_ratings_in_tree_hierarchy3(self):
        response = self.get_site_list({'ratings_in_hierarchy': f"{self.rating3.pk}, {self.rating4.pk}"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 4)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertIn(self.site1.pk, all_ids)
        self.assertIn(self.site2.pk, all_ids)
        self.assertIn(self.site3.pk, all_ids)
        self.assertIn(self.site4.pk, all_ids)


class OutdoorSiteHierarchySerializingTestCase(BaseApiTest):
    """ Test APIV2 serialzing of parents and children in site detail
    """

    @classmethod
    def setUpTestData(cls):
        cls.site_root = outdoor_factory.SiteFactory(published=True)
        cls.site_node = outdoor_factory.SiteFactory(published=True, parent=cls.site_root)
        cls.site_leaf_published = outdoor_factory.SiteFactory(published=True, parent=cls.site_node)
        cls.site_leaf_published_2 = outdoor_factory.SiteFactory(published=True, parent=cls.site_node)
        cls.site_leaf_unpublished = outdoor_factory.SiteFactory(published=False, parent=cls.site_node)

        cls.site_root_unpublished = outdoor_factory.SiteFactory(published=False)
        cls.site_node_parent_unpublished = outdoor_factory.SiteFactory(published=True, parent=cls.site_root_unpublished)

        cls.site_root_fr = outdoor_factory.SiteFactory(published_fr=True)
        cls.site_node_fr = outdoor_factory.SiteFactory(published_fr=True, parent=cls.site_root_fr)
        cls.site_leaf_published_fr = outdoor_factory.SiteFactory(published_fr=True, parent=cls.site_node_fr)
        cls.site_leaf_published_not_fr = outdoor_factory.SiteFactory(published=True, published_fr=False, published_en=True, parent=cls.site_node_fr)
        cls.site_leaf_unpublished_fr = outdoor_factory.SiteFactory(published_fr=False, parent=cls.site_node_fr)

    def test_site_parent_published_serializing(self):
        response = self.get_site_detail(self.site_node.pk)
        self.assertEqual(response.status_code, 200)
        parent = response.json()['parent']
        self.assertEqual(parent, self.site_root.pk)

    def test_site_children_published_serializing(self):
        response = self.get_site_detail(self.site_node.pk)
        self.assertEqual(response.status_code, 200)
        children = response.json()['children']
        self.assertEqual(2, len(children))
        self.assertIn(self.site_leaf_published.pk, children)
        self.assertIn(self.site_leaf_published_2.pk, children)
        self.assertNotIn(self.site_leaf_unpublished.pk, children)
        children_uuids = response.json()['children_uuids']
        self.assertEqual(2, len(children_uuids))
        self.assertIn(str(self.site_leaf_published.uuid), children_uuids)
        self.assertIn(str(self.site_leaf_published_2.uuid), children_uuids)
        self.assertNotIn(str(self.site_leaf_unpublished.uuid), children_uuids)

    def test_site_parent_unpublished_serializing(self):
        response = self.get_site_detail(self.site_node_parent_unpublished.pk)
        self.assertEqual(response.status_code, 200)
        parent = response.json()['parent']
        self.assertEqual(parent, None)
        self.assertIsNotNone(self.site_node_parent_unpublished.parent)

    def test_site_parent_and_children_serializing_by_lang(self):
        response = self.get_site_list({'language': 'fr'})
        self.assertEqual(response.status_code, 200)
        returned_sites = response.json()['results']
        site_published_fr = next((site for site in returned_sites if site['id'] == self.site_node_fr.pk), None)
        self.assertIsNotNone(site_published_fr)
        children = site_published_fr['children']
        self.assertEqual(1, len(children))
        self.assertIn(self.site_leaf_published_fr.pk, children)
        self.assertNotIn(self.site_leaf_published_not_fr.pk, children)
        self.assertNotIn(self.site_leaf_unpublished_fr.pk, children)
        children_uuids = site_published_fr['children_uuids']
        self.assertEqual(1, len(children_uuids))
        self.assertIn(str(self.site_leaf_published_fr.uuid), children_uuids)
        self.assertNotIn(str(self.site_leaf_published_not_fr.uuid), children_uuids)
        self.assertNotIn(str(self.site_leaf_unpublished_fr.uuid), children_uuids)
        parent = site_published_fr['parent']
        parent_uuid = site_published_fr['parent_uuid']
        self.assertEqual(parent, self.site_root_fr.pk)
        self.assertEqual(parent_uuid, str(self.site_root_fr.uuid))


class OutdoorFilterByPracticesTestCase(BaseApiTest):
    """ Test APIV2 filtering by practices on courses
    """

    @classmethod
    def setUpTestData(cls):
        cls.practice = outdoor_factory.PracticeFactory()
        cls.site_practice = outdoor_factory.SiteFactory(practice=cls.practice)
        cls.course_practice = outdoor_factory.CourseFactory()
        cls.course_practice.parent_sites.set([cls.site_practice])
        cls.other_practice = outdoor_factory.PracticeFactory()
        cls.site_other_practice = outdoor_factory.SiteFactory(practice=cls.other_practice)
        cls.course_other_practice = outdoor_factory.CourseFactory()
        cls.course_other_practice.parent_sites.set([cls.site_other_practice])

        cls.site_no_practice = outdoor_factory.SiteFactory(practice=None)
        cls.course_site_no_practice = outdoor_factory.CourseFactory()
        cls.course_site_no_practice.parent_sites.set([cls.site_no_practice])

    def test_filter_practices_on_courses(self):
        response = self.get_course_list({'practices': self.practice.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertIn(self.course_practice.pk, all_ids)
        self.assertNotIn(self.course_site_no_practice.pk, all_ids)
        self.assertNotIn(self.course_other_practice.pk, all_ids)

    def test_filter_practices_on_courses2(self):
        self.course_practice.parent_sites.set([self.site_practice, self.site_other_practice])
        response = self.get_course_list({'practices': self.practice.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertIn(self.course_practice.pk, all_ids)
        self.assertNotIn(self.course_site_no_practice.pk, all_ids)
        self.assertNotIn(self.course_other_practice.pk, all_ids)


class OutdoorFilterByPortal(BaseApiTest):
    """ Test APIV2 filtering on ratings on sites in hierarchy
    """

    @classmethod
    def setUpTestData(cls):
        cls.portal = common_factory.TargetPortalFactory()
        cls.theme = common_factory.ThemeFactory()
        cls.site = outdoor_factory.SiteFactory()
        cls.site.portal.set([cls.portal.pk])
        cls.site.themes.set([cls.theme.pk])
        cls.course = outdoor_factory.CourseFactory()
        cls.course.parent_sites.set([cls.site.pk])
        cls.course2 = outdoor_factory.CourseFactory()
        cls.course3 = outdoor_factory.CourseFactory()
        cls.course4 = outdoor_factory.CourseFactory()
        outdoor_models.OrderedCourseChild.objects.create(parent=cls.course, child=cls.course2)
        outdoor_models.OrderedCourseChild.objects.create(parent=cls.course, child=cls.course4, order=1)
        outdoor_models.OrderedCourseChild.objects.create(parent=cls.course3, child=cls.course)
        cls.information_desk = tourism_factory.InformationDeskFactory()
        cls.site.information_desks.set([cls.information_desk])

    def test_filter_courses_by_portal(self):
        response = self.get_course_list({'portals': self.portal.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertIn(self.course.pk, all_ids)
        self.assertNotIn(self.course2.pk, all_ids)

    def test_course_serialized_parent_site_and_related_courses(self):
        response = self.get_course_detail(self.course.pk)
        self.assertEqual(response.status_code, 200)
        parent_sites_pk = response.json()['sites']
        parent_sites_uuid = response.json()['sites_uuids']
        parent_courses_uuid = response.json()['parents_uuids']
        parent_courses_pk = response.json()['parents']
        children_courses_uuid = response.json()['children_uuids']
        children_courses_pk = response.json()['children']
        self.assertEqual(parent_sites_pk, [self.site.pk])
        self.assertEqual(parent_sites_uuid, [str(self.site.uuid)])
        self.assertEqual(parent_courses_pk, [self.course3.pk])
        self.assertEqual(parent_courses_uuid, [str(self.course3.uuid)])
        self.assertEqual(children_courses_pk, [self.course2.pk, self.course4.pk])
        self.assertEqual(children_courses_uuid, [str(self.course2.uuid), str(self.course4.uuid)])
        response = self.get_course_detail(self.course.pk, params={'language': 'en'})
        self.assertEqual(response.status_code, 200)
        parent_sites_pk = response.json()['sites']
        parent_sites_uuid = response.json()['sites_uuids']
        parent_courses_uuid = response.json()['parents_uuids']
        parent_courses_pk = response.json()['parents']
        children_courses_uuid = response.json()['children_uuids']
        children_courses_pk = response.json()['children']
        self.assertEqual(parent_sites_pk, [self.site.pk])
        self.assertEqual(parent_sites_uuid, [str(self.site.uuid)])
        self.assertEqual(parent_courses_pk, [self.course3.pk])
        self.assertEqual(parent_courses_uuid, [str(self.course3.uuid)])
        self.assertEqual(children_courses_pk, [self.course2.pk, self.course4.pk])
        self.assertEqual(children_courses_uuid, [str(self.course2.uuid), str(self.course4.uuid)])

    def test_site_serialized_children_course(self):
        response = self.get_site_detail(self.site.pk)
        self.assertEqual(response.status_code, 200)
        child_course_pk = response.json()['courses']
        child_course_uuid = response.json()['courses_uuids']
        self.assertEqual(child_course_pk, [self.course.pk])
        self.assertEqual(child_course_uuid, [str(self.course.uuid)])

    def test_filter_courses_by_themes(self):
        response = self.get_course_list({'themes': self.theme.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertIn(self.course.pk, all_ids)
        self.assertNotIn(self.course2.pk, all_ids)

    def test_filter_info_desks_by_portal_and_outdoor(self):
        response = self.get_informationdesk_list()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)
        returned_types = response.json()['results']
        all_ids = [type['id'] for type in returned_types]

        self.assertIn(self.information_desk.pk, all_ids)


class AltimetryCacheTests(BaseApiTest):
    """ Test APIV2 DEM serialization is cached """
    @classmethod
    def setUpTestData(cls):
        # Create a simple fake DEM
        with connection.cursor() as cur:
            cur.execute('INSERT INTO altimetry_dem (rast) VALUES (ST_MakeEmptyRaster(100, 125, 0, 125, 25, -25, 0, 0, %s))', [settings.SRID])
            cur.execute('UPDATE altimetry_dem SET rast = ST_AddBand(rast, \'16BSI\')')
            demvalues = [[0, 0, 3, 5], [2, 2, 10, 15], [5, 15, 20, 25], [20, 25, 30, 35], [30, 35, 40, 45]]
            for y in range(0, 5):
                for x in range(0, 4):
                    cur.execute('UPDATE altimetry_dem SET rast = ST_SetValue(rast, %s, %s, %s::float)', [x + 1, y + 1, demvalues[y][x]])
        cls.path = core_factory.PathFactory.create(geom=LineString((1, 101), (81, 101), (81, 99)))
        cls.trek = trek_factory.TrekFactory.create(paths=[cls.path])

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_cache_is_used_when_getting_trek_DEM(self):
        # There are 9 queries to get trek DEM
        with self.assertNumQueries(10):
            response = self.client.get(reverse('apiv2:trek-dem', args=(self.trek.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        # When cache is used there is single query to get trek DEM
        with self.assertNumQueries(1):
            response = self.client.get(reverse('apiv2:trek-dem', args=(self.trek.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_cache_is_used_when_getting_trek_DEM_nds(self):
        trek = trek_factory.TrekFactory.create(geom=LineString((1, 101), (81, 101), (81, 99)))
        # There are 9 queries to get trek DEM
        with self.assertNumQueries(10):
            response = self.client.get(reverse('apiv2:trek-dem', args=(trek.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        # When cache is used there is single query to get trek DEM
        with self.assertNumQueries(1):
            response = self.client.get(reverse('apiv2:trek-dem', args=(trek.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_cache_is_used_when_getting_trek_profile(self):
        # There are 8 queries to get trek profile
        with self.assertNumQueries(10):
            response = self.client.get(reverse('apiv2:trek-profile', args=(self.trek.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn("profile", response.json().keys())
        # When cache is used there is single query to get trek profile
        with self.assertNumQueries(1):
            response = self.client.get(reverse('apiv2:trek-profile', args=(self.trek.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn("profile", response.json().keys())

    def test_cache_is_used_when_getting_trek_profile_svg(self):
        # There are 8 queries to get trek profile svg
        with self.assertNumQueries(10):
            response = self.client.get(reverse('apiv2:trek-profile', args=(self.trek.pk,)), {"format": "svg"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('image/svg+xml', response['Content-Type'])
        # When cache is used there is single query to get trek profile
        with self.assertNumQueries(1):
            response = self.client.get(reverse('apiv2:trek-profile', args=(self.trek.pk,)), {"format": "svg"})
        self.assertEqual(response.status_code, 200)
        self.assertIn('image/svg+xml', response['Content-Type'])


class GenericCacheTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.practice = PracticeFactory.create()

    def test_cache_invalidates_along_x_forwarded_proto_header(self):
        with self.assertNumQueries(2):
            response = self.client.get(reverse('apiv2:practice-detail', args=(self.practice.pk,)))
        data = response.json()
        self.assertTrue(data['pictogram'].startswith('http://'))

        # after cache hit, query number is 1
        with self.assertNumQueries(1):
            response = self.client.get(reverse('apiv2:practice-detail', args=(self.practice.pk,)))
        data = response.json()
        self.assertTrue(data['pictogram'].startswith('http://'))

        # we used custom header, cache is invalidate and url is now https
        with self.assertNumQueries(2):
            response = self.client.get(reverse('apiv2:practice-detail', args=(self.practice.pk,)),
                                       HTTP_X_FORWARDED_PROTO='https')
        data = response.json()
        self.assertTrue(data['pictogram'].startswith('https://'))

        # cache is hit
        with self.assertNumQueries(1):
            response = self.client.get(reverse('apiv2:practice-detail', args=(self.practice.pk,)),
                                       HTTP_X_FORWARDED_PROTO='https')
        data = response.json()
        self.assertTrue(data['pictogram'].startswith('https://'))

        # first request is always cached
        with self.assertNumQueries(1):
            response = self.client.get(reverse('apiv2:practice-detail', args=(self.practice.pk,)))
        data = response.json()
        self.assertTrue(data['pictogram'].startswith('http://'))


class CreateReportsAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.add_url = '/api/en/reports/report'
        cls.data = {
            'geom': '{"type": "Point", "coordinates": [3, 46.5]}',
            'email': 'yeah@you.com',
            'activity': feedback_factories.ReportActivityFactory.create().pk,
            'problem_magnitude': feedback_factories.ReportProblemMagnitudeFactory.create().pk
        }

    def post_report_data(self, data):
        client = APIClient()
        response = client.post(self.add_url, data=data,
                               allow_redirects=False)
        self.assertEqual(response.status_code, 201, self.add_url)
        return response

    def test_reports_can_be_created_using_post(self):
        self.post_report_data(self.data)
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())
        report = feedback_models.Report.objects.get()
        self.assertAlmostEqual(report.geom.x, 700000)
        self.assertAlmostEqual(report.geom.y, 6600000)

    def test_reports_can_be_created_without_geom(self):
        self.data.pop('geom')
        self.post_report_data(self.data)
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())

    def test_reports_with_file(self):
        self.data['image'] = get_dummy_uploaded_image()
        self.post_report_data(self.data)
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())
        report = feedback_models.Report.objects.get()
        self.assertEqual(report.attachments.count(), 1)
        regexp = f"dummy_img{random_suffix_regexp()}.jpeg"
        self.assertRegex(report.attachments.first().attachment_file.name, regexp)
        self.assertTrue(report.attachments.first().is_image)

    @mock.patch('geotrek.api.v2.views.feedback.logger')
    def test_reports_with_failed_image(self, mock_logger):
        self.data['image'] = get_dummy_uploaded_image_svg()
        self.data['comment'] = "We have a problem"
        new_report_id = self.post_report_data(self.data).data.get('id')
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())
        report = feedback_models.Report.objects.get(pk=new_report_id)
        self.assertEqual(report.comment, "We have a problem")
        mock_logger.error.assert_called_with(f"Failed to convert attachment dummy_img.svg for report {new_report_id}: cannot identify image file <InMemoryUploadedFile: dummy_img.svg (image/svg+xml)>")
        self.assertEqual(report.attachments.count(), 0)

    @mock.patch('geotrek.api.v2.views.feedback.logger')
    def test_reports_with_bad_file_format(self, mock_logger):
        self.data['image'] = get_dummy_uploaded_document()
        self.data['comment'] = "We have a problem"
        new_report_id = self.post_report_data(self.data).data.get('id')
        self.assertTrue(feedback_models.Report.objects.filter(email='yeah@you.com').exists())
        report = feedback_models.Report.objects.get(pk=new_report_id)
        self.assertEqual(report.comment, "We have a problem")
        mock_logger.error.assert_called_with(f"Invalid attachment dummy_file.odt for report {new_report_id} : {{\'attachment_file\': ['File mime type “text/plain” is not allowed for “odt”.']}}")
        self.assertEqual(report.attachments.count(), 0)


@freeze_time("2020-01-01")
class SensitivityAPIv2Test(TranslationResetMixin, TrekkingManagerTest):
    def setUp(self):
        super().setUp()
        self.structure = authent_models.default_structure()
        self.sensitivearea = SensitiveAreaFactory.create()
        self.species = self.sensitivearea.species
        self.pk = self.sensitivearea.pk
        self.expected_properties = {
            'create_datetime': self.sensitivearea.date_insert.isoformat().replace('+00:00', 'Z'),
            'update_datetime': self.sensitivearea.date_update.isoformat().replace('+00:00', 'Z'),
            'description': "Blabla",
            "elevation": None,
            'attachments': [],
            'contact': '<a href="mailto:toto@tata.com">toto@tata.com</a>',
            'kml_url': 'http://testserver/api/en/sensitiveareas/{pk}.kml'.format(pk=self.pk),
            'openair_url': 'http://testserver/api/en/sensitiveareas/{pk}/openair'.format(pk=self.pk),
            'info_url': self.species.url,
            'species_id': self.species.id,
            "name": self.species.name,
            "period": [False, False, False, False, False, True, True, False, False, False, False, False],
            'practices': [practice.pk for practice in self.species.practices.all()],
            'rules': [
                {'code': 'R1',
                 'description': None,
                 'id': self.sensitivearea.rules.all()[0].pk,
                 'name': 'Rule1',
                 'pictogram': 'http://testserver/media/picto_rule1.png',
                 'url': 'http://url.com'},
                {'code': 'R2',
                 'description': 'abcdefgh',
                 'id': self.sensitivearea.rules.all()[1].pk,
                 'name': 'Rule2',
                 'pictogram': 'http://testserver/media/picto_rule2.png',
                 'url': 'http://url.com'}],
            'provider': '',
            'structure': self.structure.pk,
            'published': True,
        }
        self.expected_geom = {
            'type': 'Polygon',
            'coordinates': [[
                [3.0, 46.5],
                [3.0, 46.500027],
                [3.0000391, 46.500027],
                [3.0000391, 46.5],
                [3.0, 46.5],
            ]],
        }
        self.expected_result = dict(self.expected_properties)
        self.expected_result['id'] = self.pk
        self.expected_result['geometry'] = self.expected_geom
        self.expected_result['url'] = 'http://testserver/api/v2/sensitivearea/{}/?format=json'.format(self.pk)
        self.expected_geo_result = {
            'bbox': [3.0, 46.5, 3.0000391, 46.500027],
            'geometry': self.expected_geom,
            'type': 'Feature',
            'id': self.pk,
            'properties': dict(self.expected_properties),
        }
        self.expected_geo_result['properties']['url'] = 'http://testserver/api/v2/sensitivearea/{}/?format=geojson'.format(self.pk)

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_detail_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-detail', args=(self.pk,))
        params = {'format': 'json', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertJSONEqual(response.content.decode(), self.expected_result)

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_detail_sensitivearea_regulatory(self):
        self.sensitivearea = RegulatorySensitiveAreaFactory.create(species__period01=True)
        url = reverse('apiv2:sensitivearea-detail', args=(self.sensitivearea.pk,))
        params = {'format': 'json', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertIsNone(response.json()['species_id'])

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_list_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertJSONEqual(response.content.decode(), {
            'count': 1,
            'previous': None,
            'next': None,
            'results': [self.expected_result],
        })

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_geo_detail_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-detail', args=(self.pk,))
        params = {'format': 'geojson', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertJSONEqual(response.content.decode(), self.expected_geo_result)

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_geo_list_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'geojson', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertJSONEqual(response.content.decode(), {
            'count': 1,
            'next': None,
            'previous': None,
            'type': 'FeatureCollection',
            'features': [self.expected_geo_result]
        })

    def test_no_duplicates_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'geojson', 'period': 'ignore', 'language': 'en'}
        params['practices'] = ','.join([str(p.pk) for p in self.species.practices.all()])
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 1, response.json())

    def test_multipolygon(self):
        sensitivearea = MultiPolygonSensitiveAreaFactory.create()
        expected_geom = {
            'type': 'MultiPolygon',
            'coordinates': [
                [[
                    [3.0, 46.5],
                    [3.0, 46.500027],
                    [3.0000391, 46.500027],
                    [3.0000391, 46.5],
                    [3.0, 46.5],
                ]],
                [[
                    [3.0001304, 46.50009],
                    [3.0001304, 46.5001171],
                    [3.0001695, 46.5001171],
                    [3.0001695, 46.50009],
                    [3.0001304, 46.50009],
                ]]
            ],
        }
        url = reverse('apiv2:sensitivearea-detail', args=(sensitivearea.pk,))
        params = {'format': 'json', 'period': 'ignore', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['geometry'], expected_geom)

    @override_settings(SENSITIVITY_OPENAIR_SPORT_PRACTICES=['Practice1', ])
    def test_list_bubble_sensitivearea(self):
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'period': 'ignore', 'language': 'en', 'bubble': 'True'}
        response = self.client.get(url, params)
        self.expected_result[u'radius'] = None
        self.assertJSONEqual(response.content.decode(), {
            u'count': 1,
            u'previous': None,
            u'next': None,
            u'results': [self.expected_result],
        })

    def test_list_bubble_sensitivearea_with_point(self):
        sensitive_area_point = SensitiveAreaFactory.create(geom='SRID=2154;POINT (700040 6600040)',
                                                           species__period01=True, species__radius=5)
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'language': 'en', 'bubble': 'True', 'period': '1'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['radius'], 5)
        self.assertEqual(response.json()['results'][0]['name'], sensitive_area_point.species.name)

    def test_list_sportpractice(self):
        url = reverse('apiv2:sportpractice-list')
        params = {'format': 'json', 'language': 'en'}
        response = self.client.get(url, params)
        sports_practice = SportPractice.objects.all()
        result_sportpractice = [{'id': sp.id, 'name': sp.name} for sp in sports_practice]
        self.assertJSONEqual(response.content.decode(), {
            'count': 2,
            'previous': None,
            'next': None,
            'results': result_sportpractice
        })

    def test_filters_structure(self):
        other_structure = StructureFactory.create(name='other')
        self.sensitivearea_other_structure = SensitiveAreaFactory.create(structure=other_structure)
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'period': 'ignore', 'language': 'en'}
        params['structures'] = other_structure.pk
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], self.sensitivearea_other_structure.species.name)

    def test_filters_no_period(self):
        StructureFactory.create()
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 0)

    def test_filters_any_period(self):
        SensitiveAreaFactory.create()
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'period': 'any', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 2)

    def test_filters_specific_period(self):
        sensitive_area_jf = SensitiveAreaFactory.create(species__period01=True, species__period02=True)
        SensitiveAreaFactory.create(species__period01=True)
        SensitiveAreaFactory.create(species__period04=True)
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'period': '2,3', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], sensitive_area_jf.species.name)

    def test_filters_no_period_get_month(self):
        sensitive_area_month = SensitiveAreaFactory.create(**{'species__period01': True})
        SensitiveAreaFactory.create(**{'species__period02': True})
        url = reverse('apiv2:sensitivearea-list')
        params = {'format': 'json', 'language': 'en'}
        response = self.client.get(url, params)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['name'], sensitive_area_month.species.name)
