import csv
import hashlib
import os
from collections import OrderedDict
from io import StringIO
from unittest import skipIf, mock

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.contrib.gis.geos import LineString, MultiPoint, Point
from django.core import mail
from django.core.management import call_command
from django.db import connections, DEFAULT_DB_ALIAS
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.utils import translation
from mapentity.helpers import is_file_uptodate
from mapentity.tests.factories import SuperUserFactory
from rest_framework.reverse import reverse

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import TrekkingManagerFactory, StructureFactory, UserProfileFactory
from geotrek.common.templatetags import geotrek_tags
from geotrek.common.tests import CommonTest, CommonLiveTest, TranslationResetMixin, GeotrekAPITestCase
from geotrek.common.tests.factories import (AttachmentFactory, ThemeFactory, LabelFactory, RecordSourceFactory,
                                            TargetPortalFactory)
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.core.tests.factories import PathFactory
from geotrek.infrastructure.models import Infrastructure
from geotrek.infrastructure.tests.factories import InfrastructureFactory
from geotrek.signage.models import Signage
from geotrek.signage.tests.factories import SignageFactory
from geotrek.tourism.tests import factories as tourism_factories
# Make sur to register Trek model
from geotrek.trekking import urls  # NOQA
from geotrek.trekking import views as trekking_views
from geotrek.zoning.tests.factories import DistrictFactory, CityFactory
from .base import TrekkingManagerTest
from .factories import (POIFactory, POITypeFactory, TrekFactory, TrekWithPOIsFactory,
                        TrekNetworkFactory, WebLinkFactory, AccessibilityFactory,
                        TrekRelationshipFactory, ServiceFactory, ServiceTypeFactory,
                        TrekWithServicesFactory, TrekWithInfrastructuresFactory,
                        TrekWithSignagesFactory, PracticeFactory)
from ..models import POI, Trek, Service, OrderedTrekChild


class POIViewsTest(GeotrekAPITestCase, CommonTest):
    model = POI
    modelfactory = POIFactory
    userfactory = TrekkingManagerFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [3.0, 46.5]}
    extra_column_list = ['type', 'eid']
    expected_column_list_extra = ['id', 'name', 'type', 'eid']
    expected_column_formatlist_extra = ['id', 'type', 'eid']

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name
        }

    def get_expected_json_attrs(self):
        return {
            'areas': [],
            'cities': [],
            'description': '<p>Description</p>',
            'districts': [],
            'filelist_url': '/paperclip/get/trekking/poi/{}/'.format(self.obj.pk),
            'files': [],
            'map_image_url': '/image/poi-{}.png'.format(self.obj.pk),
            'max_elevation': 0,
            'min_elevation': 0,
            'name': 'POI',
            'pictures': [],
            'printable': '/api/en/pois/{}/poi.pdf'.format(self.obj.pk),
            'publication_date': '2020-03-17',
            'published': True,
            'published_status': [
                {'lang': 'en', 'language': 'English', 'status': True},
                {'lang': 'es', 'language': 'Spanish', 'status': False},
                {'lang': 'fr', 'language': 'French', 'status': False},
                {'lang': 'it', 'language': 'Italian', 'status': False},
            ],
            'slug': 'poi',
            'structure': {'id': self.obj.structure.pk, 'name': 'My structure'},
            'thumbnail': None,
            'type': {
                'id': self.obj.type.pk,
                'label': 'POI type',
                'pictogram': '/media/upload/poi-type.png',
            },
            'videos': [],
        }

    def get_expected_datatables_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name_display,
            'thumbnail': 'None',
            'type': self.obj.type.label
        }

    def get_good_data(self):
        good_data = {
            'name_fr': 'test',
            'name_en': 'test',
            'description_fr': 'ici',
            'description_en': 'here',
            'type': POITypeFactory.create().pk,
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            PathFactory.create()
            good_data['topology'] = '{"lat": 5.1, "lng": 6.6}'
        else:
            good_data['geom'] = 'POINT(5.1 6.6)'
        return good_data

    def test_status_only_review(self):
        element_not_published = self.modelfactory.create(published=False, review=True)
        element_not_published.save()
        response = self.client.get(self.model.get_datatablelist_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Waiting for publication')

    @override_settings(ALERT_REVIEW=True)
    def test_status_review_alert(self):
        element_not_published = self.modelfactory.create(published=False, review=False)
        element_not_published.save()
        self.assertEqual(len(mail.outbox), 0)
        element_not_published.review = True
        element_not_published.save()
        element_not_published.name = "Bar"
        element_not_published.save()
        self.assertEqual(len(mail.outbox), 1)
        element_not_published.review = False
        element_not_published.save()
        self.assertEqual(len(mail.outbox), 1)
        element_not_published.published = True
        element_not_published.save()
        self.assertEqual(len(mail.outbox), 1)
        element_not_published.published = False
        element_not_published.review = True
        element_not_published.save()
        self.assertEqual(len(mail.outbox), 2)

    @override_settings(ALERT_REVIEW=True)
    @mock.patch('geotrek.common.mixins.models.mail_managers')
    def test_status_review_fail_mail(self, mock_mail):
        mock_mail.side_effect = Exception("Test")
        element_not_published = self.modelfactory.create(published=False, review=False)
        element_not_published.save()
        self.assertEqual(len(mail.outbox), 0)
        element_not_published.review = True
        element_not_published.save()
        element_not_published.name = "Bar"
        element_not_published.save()
        self.assertEqual(len(mail.outbox), 0)

    def test_empty_topology(self):
        data = self.get_good_data()
        if settings.TREKKING_TOPOLOGY_ENABLED:
            data['topology'] = ''
        else:
            data['geom'] = ''
        response = self.client.post(self.model.get_add_url(), data)
        self.assertEqual(response.status_code, 200)
        form = self.get_form(response)
        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.assertEqual(form.errors, {'topology': ['Topology is empty.']})
        else:
            self.assertEqual(form.errors, {'geom': ['No geometry value provided.']})

    def test_listing_number_queries(self):
        # Create many instances
        self.modelfactory.build_batch(1000)
        DistrictFactory.build_batch(10)

        with self.assertNumQueries(6):
            self.client.get(self.model.get_datatablelist_url())

        with self.assertNumQueries(10):
            self.client.get(self.model.get_format_list_url())

    def test_list_in_csv(self):
        self.modelfactory.create()
        DistrictFactory.create(name="Refouilli", geom="SRID=2154;MULTIPOLYGON (((200000 750000, 699991 6600005, 700005 "
                                                      "6600005, 650000 1200000, 650000 750000, 200000 750000)))")
        DistrictFactory.create(name="Trifouilli",
                               geom="SRID=2154;MULTIPOLYGON (((200000 750000, 699991 6600005, 700005 "
                                    "6600005, 650000 1200000, 650000 750000, 200000 750000)))")
        response = self.client.get(self.model.get_format_list_url())
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        for row in reader:
            self.assertSetEqual({elem for elem in row['Districts'].split(', ')}, {'Trifouilli', 'Refouilli'})

    def test_pois_on_treks_do_not_exist(self):
        self.modelfactory.create()

        response = self.client.get(
            reverse('trekking:trek_poi_geojson', kwargs={'lang': translation.get_language(), 'pk': 0}))
        self.assertEqual(response.status_code, 404)

    def test_pois_on_treks_not_public(self):
        self.modelfactory.create()

        trek = TrekFactory.create(published=False)
        response = self.client.get(
            reverse('trekking:trek_poi_geojson', kwargs={'lang': translation.get_language(), 'pk': trek.pk}))
        self.assertEqual(response.status_code, 200)

    def test_pois_on_treks_not_public_anonymous(self):
        self.logout()
        self.modelfactory.create()

        trek = TrekFactory.create(published=False)
        response = self.client.get(
            reverse('trekking:trek_poi_geojson', kwargs={'lang': translation.get_language(), 'pk': trek.pk}))
        self.assertEqual(response.status_code, 404)

    def test_lang_in_detail_page(self):
        poi = POIFactory.create(name_fr='un POI', name_en='a POI')

        response = self.client.get(poi.get_detail_url() + '?lang=fr')
        self.assertContains(response, 'un POI')
        self.assertNotContains(response, 'a POI')

        response = self.client.get(poi.get_detail_url() + '?lang=en')
        self.assertContains(response, 'a POI')
        self.assertNotContains(response, 'un POI')


class TrekViewsTest(GeotrekAPITestCase, CommonTest):
    model = Trek
    modelfactory = TrekFactory
    userfactory = TrekkingManagerFactory
    expected_json_geom = {'type': 'LineString', 'coordinates': [[3.0, 46.5], [3.001304, 46.5009004]]}
    extra_column_list = ['type', 'eid']
    expected_column_list_extra = ['id', 'name', 'type', 'eid']
    expected_column_formatlist_extra = ['id', 'name', 'type', 'eid']
    length = 141.42135623731

    def get_expected_geojson_geom(self):
        return self.expected_json_geom

    def get_expected_geojson_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name
        }

    def get_expected_json_attrs(self):
        return {
            'access': '<p>Access</p>',
            'accessibilities': [],
            'accessibility_advice': '<p>Accessibility advice</p>',
            'accessibility_covering': '<p>Accessibility covering</p>',
            'accessibility_exposure': '<p>Accessibility exposure</p>',
            'accessibility_level': {'id': self.obj.accessibility_level.pk, 'label': 'Easy'},
            'accessibility_signage': '<p>Accessibility signage</p>',
            'accessibility_slope': '<p>Accessibility slope</p>',
            'accessibility_width': '<p>Accessibility width</p>',
            'advice': '<p>Advice</p>',
            'advised_parking': '<p>Advised parking</p>',
            'altimetric_profile': '/api/en/treks/{}/profile.json'.format(self.obj.pk),
            'ambiance': '<p>Ambiance</p>',
            'areas': [],
            'arrival': 'Arrival',
            'ascent': 0,
            'category': {
                'id': 'T',
                'label': 'Hike',
                'order': 1,
                'pictogram': '/static/trekking/trek.svg',
                'slug': 'trek',
                'type2_label': 'Accessibility type',
            },
            'children': [],
            'cities': [],
            'departure': 'Departure',
            'descent': 0,
            'description': '<p>Description</p>',
            'description_teaser': '<p>Description teaser</p>',
            'difficulty': {
                'id': self.obj.difficulty.pk,
                'label': 'Difficulty',
                'pictogram': '/media/upload/difficulty.png',
            },
            'accessibility_infrastructure': '<p>Accessibility infrastructure</p>',
            'districts': [],
            'dives': [],
            'duration': 1.5,
            'duration_pretty': '1 h 30',
            'elevation_area_url': '/api/en/treks/{}/dem.json'.format(self.obj.pk),
            'elevation_svg_url': '/api/en/treks/{}/profile.svg'.format(self.obj.pk),
            'gear': '<p>Gear</p>',
            'filelist_url': '/paperclip/get/trekking/trek/{}/'.format(self.obj.pk),
            'files': [],
            'gpx': '/api/en/treks/{}/trek.gpx'.format(self.obj.pk),
            'information_desks': [],
            'labels': [],
            'kml': '/api/en/treks/{}/trek.kml'.format(self.obj.pk),
            'map_image_url': '/image/trek-{}-en.png'.format(self.obj.pk),
            'max_elevation': 0,
            'min_elevation': 0,
            'name': 'Trek',
            'networks': [],
            'next': {},
            'parents': [],
            'parking_location': [-1.3630753, -5.9838497],
            'pictures': [],
            'points_reference': None,
            'portal': [],
            'practice': {
                'id': self.obj.practice.pk,
                'label': 'Usage',
                'pictogram': '/media/upload/practice.png',
            },
            'previous': {},
            'printable': '/api/en/treks/{}/trek.pdf'.format(self.obj.pk),
            'public_transport': '<p>Public transport</p>',
            'publication_date': '2020-03-17',
            'published': True,
            'published_status': [
                {'lang': 'en', 'language': 'English', 'status': True},
                {'lang': 'es', 'language': 'Spanish', 'status': False},
                {'lang': 'fr', 'language': 'French', 'status': False},
                {'lang': 'it', 'language': 'Italian', 'status': False}
            ],
            'relationships': [],
            'route': {
                'id': self.obj.route.pk,
                'label': 'Route',
                'pictogram': '/media/upload/routes.png',
            },
            'slope': 0.0,
            'slug': 'trek',
            'source': [],
            'structure': {
                'id': self.obj.structure.pk,
                'name': 'My structure',
            },
            'themes': [],
            'thumbnail': None,
            'touristic_contents': [],
            'touristic_events': [],
            'treks': [],
            'type2': [],
            'usages': [{
                'id': self.obj.practice.pk,
                'label': 'Usage',
                'pictogram': '/media/upload/practice.png'
            }],
            'videos': [],
            'web_links': [],
            'reservation_id': 'XXXXXXXXX',
            'reservation_system': self.obj.reservation_system.name,
            'ratings': [],
            'ratings_description': '',
        }

    def get_expected_datatables_attrs(self):
        return {
            'departure': 'Departure',
            'difficulty': 'Difficulty',
            'duration': 1.5,
            'id': self.obj.pk,
            'name': self.obj.name_display,
            'thumbnail': 'None',
        }

    def get_bad_data(self):
        return OrderedDict([
            ('name_en', ''),
            ('trek_relationship_a-TOTAL_FORMS', '0'),
            ('trek_relationship_a-INITIAL_FORMS', '1'),
            ('trek_relationship_a-MAX_NUM_FORMS', '0'),
        ]), 'This field is required.'

    def get_good_data(self):
        self.path = PathFactory.create()
        good_data = {
            'name_fr': 'Huh',
            'name_en': 'Hehe',
            'departure_fr': '',
            'departure_en': '',
            'arrival_fr': '',
            'arrival_en': '',
            'published': '',
            'difficulty': '',
            'route': '',
            'description_teaser_fr': '',
            'description_teaser_en': '',
            'description_fr': '',
            'description_en': '',
            'ambiance_fr': '',
            'ambiance_en': '',
            'access_fr': '',
            'access_en': '',
            'accessibility_infrastructure_fr': '',
            'accessibility_infrastructure_en': '',
            'duration': '0',
            'labels': [],
            'advised_parking': 'Very close',
            'parking_location': 'POINT (1.0 1.0)',
            'public_transport': 'huh',
            'advice_fr': '',
            'advice_en': '',
            'gear_fr': '',
            'gear_en': '',
            'themes': ThemeFactory.create().pk,
            'networks': TrekNetworkFactory.create().pk,
            'practice': '',
            'accessibilities': AccessibilityFactory.create().pk,
            'web_links': WebLinkFactory.create().pk,
            'information_desks': tourism_factories.InformationDeskFactory.create().pk,

            'trek_relationship_a-TOTAL_FORMS': '2',
            'trek_relationship_a-INITIAL_FORMS': '0',
            'trek_relationship_a-MAX_NUM_FORMS': '',

            'trek_relationship_a-0-id': '',
            'trek_relationship_a-0-trek_b': TrekFactory.create().pk,
            'trek_relationship_a-0-has_common_edge': 'on',
            'trek_relationship_a-0-has_common_departure': 'on',
            'trek_relationship_a-0-is_circuit_step': '',

            'trek_relationship_a-1-id': '',
            'trek_relationship_a-1-trek_b': TrekFactory.create().pk,
            'trek_relationship_a-1-has_common_edge': '',
            'trek_relationship_a-1-has_common_departure': '',
            'trek_relationship_a-1-is_circuit_step': 'on',

        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            good_data['topology'] = '{"paths": [%s]}' % self.path.pk
            good_data['pois_excluded'] = POIFactory.create(paths=[self.path]).pk
        else:
            good_data['geom'] = 'SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)'
            good_data['pois_excluded'] = POIFactory.create(geom='SRID=2154;POINT (700000 6600000)').pk
        return good_data

    def test_status(self):
        TrekFactory.create(duration=float('nan'))
        super().test_status()

    def test_badfield_goodgeom(self):
        bad_data, form_error = self.get_bad_data()
        bad_data['parking_location'] = 'POINT (1.0 1.0)'  # good data

        url = self.model.get_add_url()
        response = self.client.post(url, bad_data)
        self.assertEqual(response.status_code, 200)
        form = self.get_form(response)
        self.assertEqual(form.data['parking_location'], bad_data['parking_location'])

    def test_basic_format(self):
        super().test_basic_format()
        self.modelfactory.create(name="ukélélé")  # trek with utf8
        for fmt in ('csv', 'shp', 'gpx'):
            response = self.client.get(self.model.get_format_list_url() + '?format=' + fmt)
            self.assertEqual(response.status_code, 200)

    def test_no_pois_detached_in_create(self):
        response = self.client.get(self.model.get_add_url())
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'pois_excluded')

    def test_pois_detached_update(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
            trek = TrekFactory.create(paths=[p1])
            poi = POIFactory.create(paths=[(p1, 0.6, 0.6)])
        else:
            trek = TrekFactory.create(geom='SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)')
            poi = POIFactory.create(geom='SRID=4326;POINT (0.6 0.6)')
        good_data = self.get_good_data()
        good_data['pois_excluded'] = poi.pk
        self.client.post(self.model.get_update_url(trek), good_data)
        self.assertIn(poi, trek.pois_excluded.all())

    def test_detail_lother_language(self):

        bad_data, form_error = self.get_bad_data()
        bad_data['parking_location'] = 'POINT (1.0 1.0)'  # good data

        url = self.model.get_add_url()
        response = self.client.post(url, bad_data)
        self.assertEqual(response.status_code, 200)
        form = self.get_form(response)
        self.assertEqual(form.data['parking_location'], bad_data['parking_location'])

    def test_lang_in_detail_page(self):
        trek = TrekFactory.create(name_fr='un itinéraire', name_en='a trek')

        response = self.client.get(trek.get_detail_url() + '?lang=fr')
        self.assertContains(response, 'un itinéraire')
        self.assertNotContains(response, 'a trek')

        response = self.client.get(trek.get_detail_url() + '?lang=en')
        self.assertContains(response, 'a trek')
        self.assertNotContains(response, 'un itinéraire')

    def test_list_in_csv(self):
        if self.model is None:
            return  # Abstract test should not run

        polygon = 'SRID=%s;MULTIPOLYGON(((0 0, 0 3, 3 3, 3 0, 0 0)))' % settings.SRID
        self.city = CityFactory(geom=polygon, name="Trifouilli")
        self.city_2 = CityFactory(geom=polygon, name="Refouilli")
        self.district = DistrictFactory(geom=polygon, name="District")

        trek_args = {'name': 'Step 2',
                     'points_reference': MultiPoint([Point(0, 0), Point(1, 1)], srid=settings.SRID),
                     'parking_location': Point(0, 0, srid=settings.SRID)}
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path1 = PathFactory.create(geom='SRID=%s;LINESTRING(0 0, 1 0)' % settings.SRID)
            self.trek = TrekFactory.create(
                paths=[path1],
                **trek_args
            )
        else:
            self.trek = TrekFactory.create(
                geom='SRID=%s;LINESTRING(0 0, 1 0)' % settings.SRID,
                **trek_args
            )
        fmt = 'csv'
        response = self.client.get(self.model.get_format_list_url() + '?format=' + fmt)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'text/csv')

        # Read the csv
        reader = csv.DictReader(StringIO(response.content.decode("utf-8")), delimiter=',')
        for row in reader:
            self.assertEqual(row['Cities'], "Trifouilli, Refouilli")
            self.assertEqual(row['Districts'], self.district.name)

    @mock.patch('mapentity.helpers.requests')
    def test_document_public_export_without_pictogram(self, mock_requests):
        if self.model is None:
            return  # Abstract test should not run
        mock_requests.get.return_value.status_code = 200
        mock_requests.get.return_value.content = b'<p id="properties">Mock</p>'
        practice = PracticeFactory.create(pictogram=None)
        obj = self.modelfactory.create(practice=practice)
        response = self.client.get(
            reverse(f'{self.model._meta.app_label}:{self.model._meta.model_name}_printable',
                    kwargs={'lang': 'en', 'pk': obj.pk, 'slug': obj.slug}))
        self.assertEqual(response.status_code, 200)


class TrekViewsLiveTests(CommonLiveTest):
    model = Trek
    modelfactory = TrekFactory
    userfactory = SuperUserFactory


class TrekCustomViewTests(TrekkingManagerTest):
    def setUp(self):
        self.login()

    def test_trek_infrastructure_geojson(self):
        trek = TrekWithInfrastructuresFactory.create(published=True)
        self.assertEqual(len(trek.infrastructures), 2)
        infra = trek.infrastructures[0]
        infra.published = True
        infra.save()
        self.assertEqual(len(trek.infrastructures), 2)

        url = '/api/en/treks/{pk}/infrastructures.geojson'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        infrastructureslayer = response.json()
        names = [feature['properties']['name'] for feature in infrastructureslayer['features']]
        self.assertIn(infra.name, names)

    def test_trek_infrastructure_geojson_not_public_no_permission(self):
        trek = TrekWithInfrastructuresFactory.create(published=False)
        self.assertEqual(len(trek.infrastructures), 2)
        infra = trek.infrastructures[0]
        infra.published = True
        infra.save()
        self.assertEqual(len(trek.infrastructures), 2)
        self.user.groups.remove(Group.objects.first())
        self.user.groups.clear()
        self.user = get_object_or_404(User, pk=self.user.pk)
        self.client.login(username=self.user.username, password='booh')
        url = '/api/en/treks/{pk}/infrastructures.geojson'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_trek_signage_geojson(self):
        trek = TrekWithSignagesFactory.create(published=True)
        self.assertEqual(len(trek.signages), 2)
        signa = trek.signages[0]
        signa.published = True
        signa.save()
        self.assertEqual(len(trek.signages), 2)

        url = '/api/en/treks/{pk}/signages.geojson'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        signageslayer = response.json()
        names = [feature['properties']['name'] for feature in signageslayer['features']]
        self.assertIn(signa.name, names)

    def test_trek_pois_geojson(self):
        trek = TrekWithPOIsFactory.create(published=True)
        first_poi = trek.pois.first()
        trek.pois_excluded.add(first_poi)
        trek.save()
        self.assertEqual(len(trek.pois), 1)
        poi = trek.pois[0]
        poi.published = True
        poi.save()
        AttachmentFactory.create(content_object=poi, attachment_file=get_dummy_uploaded_image())
        self.assertNotEqual(poi.thumbnail, None)
        self.assertEqual(len(trek.pois), 1)

        url = '/api/en/treks/{pk}/pois.geojson'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        poislayer = response.json()
        poifeature = poislayer['features'][0]
        self.assertTrue('thumbnail' in poifeature['properties'])
        self.assertEqual(len(poislayer['features']), 1)
        self.assertEqual(poifeature['properties']['name'], poi.name)

    def test_pois_geojson(self):
        poi = POIFactory.create()
        poi2 = POIFactory.create()
        self.assertEqual(POI.objects.count(), 2)
        poi.published = True
        poi2.published = False
        poi.save()
        poi2.save()

        AttachmentFactory.create(content_object=poi, attachment_file=get_dummy_uploaded_image())
        self.assertNotEqual(poi.thumbnail, None)
        self.assertEqual(POI.objects.filter(published=True).count(), 1)

        response = self.client.get('/api/en/pois.geojson')
        self.assertEqual(response.status_code, 200)
        poislayer = response.json()
        poifeature = poislayer['features'][0]
        self.assertTrue('thumbnail' in poifeature['properties'])
        self.assertEqual(len(poislayer['features']), 1)
        self.assertEqual(poifeature['properties']['name'], poi.name)

    def test_infrastructures_geojson(self):
        infra = InfrastructureFactory.create()
        infra2 = InfrastructureFactory.create()
        self.assertEqual(Infrastructure.objects.count(), 2)
        infra.published = True
        infra2.published = False
        infra.save()
        infra2.save()

        self.assertEqual(Infrastructure.objects.filter(published=True).count(), 1)

        response = self.client.get('/api/en/infrastructures.geojson')
        self.assertEqual(response.status_code, 200)
        infraslayer = response.json()
        infrafeature = infraslayer['features'][0]
        self.assertEqual(len(infraslayer['features']), 1)
        self.assertEqual(infrafeature['properties']['name'], infra.name)

    def test_signages_geojson(self):
        signa = SignageFactory.create()
        signa2 = SignageFactory.create()
        self.assertEqual(Signage.objects.count(), 2)
        signa.published = True
        signa2.published = False
        signa.save()
        signa2.save()

        self.assertEqual(Signage.objects.filter(published=True).count(), 1)

        response = self.client.get('/api/en/signages.geojson')
        self.assertEqual(response.status_code, 200)
        poislayer = response.json()
        poifeature = poislayer['features'][0]
        self.assertEqual(len(poislayer['features']), 1)
        self.assertEqual(poifeature['properties']['name'], signa.name)

    def test_services_geojson(self):
        trek = TrekWithServicesFactory.create(published=True)
        self.assertEqual(len(trek.services), 2)
        service = trek.services[0]
        service.published = True
        service.save()
        self.assertEqual(len(trek.services), 2)

        url = '/api/en/treks/{pk}/services.geojson'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        serviceslayer = response.json()
        servicefeature = serviceslayer['features'][0]
        self.assertTrue('type' in servicefeature['properties'])

    def test_kml(self):
        trek = TrekWithPOIsFactory.create()
        url = '/api/en/treks/{pk}/slug.kml'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.google-earth.kml+xml')

    def test_kml_do_not_exist(self):
        url = '/api/en/treks/{pk}/slug.kml'.format(pk=999)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_not_published_profile_json(self):
        trek = TrekFactory.create(published=False)
        url = '/api/en/treks/{pk}/profile.json'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_not_published_elevation_area_json(self):
        trek = TrekFactory.create(published=False)
        url = '/api/en/treks/{pk}/dem.json'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_profile_svg(self):
        trek = TrekFactory.create()
        url = '/api/en/treks/{pk}/profile.svg'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/svg+xml')

    def test_weblink_popup(self):
        url = reverse('trekking:weblink_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(TREK_EXPORT_POI_LIST_LIMIT=1)
    @mock.patch('mapentity.models.MapEntityMixin.prepare_map_image')
    @mock.patch('mapentity.models.MapEntityMixin.get_attributes_html')
    def test_trek_export_poi_list_limit(self, mocked_prepare, mocked_attributes):
        trek = TrekWithPOIsFactory.create()
        self.assertEqual(len(trek.pois), 2)
        poi = trek.pois[0]
        poi.published = True
        poi.save()
        view = trekking_views.TrekDocumentPublic()
        view.object = trek
        view.request = RequestFactory().get('/')
        view.kwargs = {}
        view.kwargs[view.pk_url_kwarg] = trek.pk
        context = view.get_context_data()
        self.assertEqual(len(context['pois']), 1)


class TrekCustomPublicViewTests(TrekkingManagerTest):
    @mock.patch('djappypod.backend.os.path.exists', create=True)
    def test_overriden_public_template(self, exists_patched):
        overriden_template = os.path.join(settings.VAR_DIR, 'conf', 'extra_templates', 'trekking', 'trek_public.odt')

        def fake_exists(path):
            return path == overriden_template

        exists_patched.side_effect = fake_exists
        template = get_template('trekking/trek_public.odt')
        self.assertEqual(template.path, overriden_template)

    def test_profile_json(self):
        trek = TrekFactory.create(published=True)
        url = '/api/en/treks/{pk}/profile.json'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_not_published_profile_json(self):
        trek = TrekFactory.create(published=False)
        url = '/api/en/treks/{pk}/profile.json'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_elevation_area_json(self):
        trek = TrekFactory.create(published=True)
        url = '/api/en/treks/{pk}/dem.json'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_not_published_elevation_area_json(self):
        trek = TrekFactory.create(published=False)
        url = '/api/en/treks/{pk}/dem.json'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)


class TrekJSONSetUp(TrekkingManagerTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        polygon = 'SRID=%s;MULTIPOLYGON(((0 0, 0 3, 3 3, 3 0, 0 0)))' % settings.SRID
        cls.city = CityFactory(geom=polygon)
        cls.district = DistrictFactory(geom=polygon)

        trek_args = {'name': 'Step 2',
                     'points_reference': MultiPoint([Point(0, 0), Point(1, 1)], srid=settings.SRID),
                     'parking_location': Point(0, 0, srid=settings.SRID)}
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path1 = PathFactory.create(geom='SRID=%s;LINESTRING(0 0, 1 0)' % settings.SRID)
            cls.trek = TrekFactory.create(
                paths=[path1],
                **trek_args
            )
        else:
            cls.trek = TrekFactory.create(
                geom='SRID=%s;LINESTRING(0 0, 1 0)' % settings.SRID,
                **trek_args
            )
        cls.attachment = AttachmentFactory.create(content_object=cls.trek,
                                                  attachment_file=get_dummy_uploaded_image())

        cls.information_desk = tourism_factories.InformationDeskFactory.create()
        cls.trek.information_desks.add(cls.information_desk)

        cls.theme = ThemeFactory.create()
        cls.trek.themes.add(cls.theme)

        cls.accessibility = AccessibilityFactory.create()
        cls.trek.accessibilities.add(cls.accessibility)

        cls.network = TrekNetworkFactory.create()
        cls.trek.networks.add(cls.network)

        cls.weblink = WebLinkFactory.create()
        cls.trek.web_links.add(cls.weblink)

        cls.label = LabelFactory.create()
        cls.trek.labels.add(cls.label)

        cls.source = RecordSourceFactory.create()
        cls.trek.source.add(cls.source)

        cls.portal = TargetPortalFactory.create()
        cls.trek.portal.add(cls.portal)
        trek_b_args = {'published': True}
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path2 = PathFactory.create(geom='SRID=%s;LINESTRING(0 1, 1 1)' % settings.SRID)
            cls.trek_b = TrekFactory.create(paths=[path2], **trek_b_args)
            TrekFactory(paths=[path2], published=False)  # not published
            cls.trek3 = TrekFactory(paths=[path2], published=True)  # deleted
            cls.trek3.delete()
            TrekFactory(paths=[PathFactory.create(geom='SRID=%s;LINESTRING(0 2000, 1 2000)' % settings.SRID)],
                        published=True)  # too far
        else:
            cls.trek_b = TrekFactory.create(geom='SRID=%s;LINESTRING(0 1, 1 1)' % settings.SRID, **trek_b_args)
            TrekFactory(geom='SRID=%s;LINESTRING(0 1, 1 1)' % settings.SRID, published=False)
            trek3 = TrekFactory(geom='SRID=%s;LINESTRING(0 1, 1 1)' % settings.SRID, published=True)
            trek3.delete()
            TrekFactory(geom='SRID=%s;LINESTRING(0 2000, 1 2000)' % settings.SRID, published=True)  # too far

        TrekRelationshipFactory.create(has_common_departure=True,
                                       has_common_edge=False,
                                       is_circuit_step=True,
                                       trek_a=cls.trek,
                                       trek_b=cls.trek_b)

        cls.touristic_content = tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(1 1)' % settings.SRID,
                                                                          published=True)
        tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(1 1)' % settings.SRID,
                                                  published=False)  # not published
        tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(1 1)' % settings.SRID,
                                                  published=True).delete()  # deleted
        tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(1000 1000)' % settings.SRID,
                                                  published=True)  # too far
        cls.touristic_event = tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(2 2)' % settings.SRID,
                                                                      published=True)
        tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(2 2)' % settings.SRID,
                                                published=False)  # not published
        tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(2 2)' % settings.SRID,
                                                published=True).delete()  # deleted
        tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(2000 2000)' % settings.SRID,
                                                published=True)  # too far

        cls.parent = TrekFactory.create(published=True, name='Parent')
        cls.child1 = TrekFactory.create(published=False, name='Child 1')
        cls.child2 = TrekFactory.create(published=True, name='Child 2')
        cls.sibling = TrekFactory.create(published=True, name='Sibling')
        OrderedTrekChild(parent=cls.parent, child=cls.trek, order=0).save()
        OrderedTrekChild(parent=cls.trek, child=cls.child1, order=3).save()
        OrderedTrekChild(parent=cls.trek, child=cls.child2, order=2).save()
        OrderedTrekChild(parent=cls.parent, child=cls.sibling, order=1).save()
        cls.pk = cls.trek.pk

    @override_settings(THUMBNAIL_COPYRIGHT_FORMAT="{title} {author}")
    def setUp(self):
        self.login()
        url = '/api/en/treks/{pk}.json'.format(pk=self.pk)
        self.response = self.client.get(url)
        self.result = self.response.json()


@override_settings(SPLIT_TREKS_CATEGORIES_BY_PRACTICE=True)
class TrekPracticeTest(TrekJSONSetUp):
    def test_touristic_contents_practice(self):
        self.assertEqual(len(self.result['touristic_contents']), 1)
        self.assertDictEqual(self.result['touristic_contents'][0], {
            'id': self.touristic_content.pk,
            'category_id': self.touristic_content.prefixed_category_id})


class TrekJSONDetailTest(TrekJSONSetUp):
    """ Since we migrated some code to Django REST Framework, we should test
    the migration extensively. Geotrek-rando mainly relies on this view.
    """

    def test_related_urls(self):
        self.assertEqual(self.result['elevation_area_url'],
                         '/api/en/treks/{pk}/dem.json'.format(pk=self.pk))
        self.assertEqual(self.result['map_image_url'],
                         '/image/trek-%s-en.png' % self.pk)
        self.assertEqual(self.result['altimetric_profile'],
                         '/api/en/treks/{pk}/profile.json'.format(pk=self.pk))
        self.assertEqual(self.result['filelist_url'],
                         '/paperclip/get/trekking/trek/%s/' % self.pk)
        self.assertEqual(self.result['gpx'],
                         '/api/en/treks/{pk}/{slug}.gpx'.format(pk=self.pk, slug=self.trek.slug))
        self.assertEqual(self.result['kml'],
                         '/api/en/treks/{pk}/{slug}.kml'.format(pk=self.pk, slug=self.trek.slug))
        self.assertEqual(self.result['printable'],
                         '/api/en/treks/{pk}/{slug}.pdf'.format(pk=self.pk, slug=self.trek.slug))

    def test_thumbnail(self):
        self.assertEqual(self.result['thumbnail'],
                         os.path.join(settings.MEDIA_URL,
                                      self.attachment.attachment_file.name) + '.120x120_q85_crop.png')

    def test_published_status(self):
        self.assertDictEqual(self.result['published_status'][0],
                             {'lang': 'en', 'status': True, 'language': 'English'})

    @override_settings(THUMBNAIL_COPYRIGHT_FORMAT="{title} {author}")
    def test_pictures(self):
        url = '{url}.800x800_q85_watermark-{id}.png'.format(
            url=self.attachment.attachment_file.url,
            id=hashlib.md5(
                settings.THUMBNAIL_COPYRIGHT_FORMAT.format(
                    author=self.attachment.author,
                    title=self.attachment.title,
                    legend=self.attachment.legend).encode()).hexdigest())
        self.assertDictEqual(self.result['pictures'][0],
                             {'url': url,
                              'title': self.attachment.title,
                              'legend': self.attachment.legend,
                              'author': self.attachment.author})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_networks(self):
        self.assertDictEqual(self.result['networks'][0],
                             {"id": self.network.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, self.network.pictogram.name),
                              "name": self.network.network})

    def test_practice_not_none(self):
        self.assertDictEqual(self.result['practice'],
                             {"id": self.trek.practice.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, self.trek.practice.pictogram.name),
                              "label": self.trek.practice.name})

    def test_usages(self):  # Rando v1 compat
        self.assertDictEqual(self.result['usages'][0],
                             {"id": self.trek.practice.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, self.trek.practice.pictogram.name),
                              "label": self.trek.practice.name})

    def test_accessibilities(self):
        self.assertDictEqual(self.result['accessibilities'][0],
                             {"id": self.accessibility.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, self.accessibility.pictogram.name),
                              "label": self.accessibility.name})

    def test_themes(self):
        self.assertDictEqual(self.result['themes'][0],
                             {"id": self.theme.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, self.theme.pictogram.name),
                              "label": self.theme.label})

    def test_labels(self):
        self.assertDictEqual(self.result['labels'][0],
                             {"id": self.label.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, self.label.pictogram.name),
                              "name": self.label.name,
                              "advice": self.label.advice,
                              "filter_rando": self.label.filter})

    def test_weblinks(self):
        self.assertDictEqual(self.result['web_links'][0],
                             {"id": self.weblink.id,
                              "url": self.weblink.url,
                              "name": self.weblink.name,
                              "category": {
                                  "id": self.weblink.category.id,
                                  "pictogram": os.path.join(settings.MEDIA_URL, self.weblink.category.pictogram.name),
                                  "label": self.weblink.category.label}
                              })

    def test_route_not_none(self):
        self.assertDictEqual(self.result['route'],
                             {"id": self.trek.route.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, self.trek.route.pictogram.name),
                              "label": self.trek.route.route})

    def test_difficulty_not_none(self):
        self.assertDictEqual(self.result['difficulty'],
                             {"id": self.trek.difficulty.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, self.trek.difficulty.pictogram.name),
                              "label": self.trek.difficulty.difficulty})

    def test_information_desks(self):
        desk_type = self.information_desk.type
        self.maxDiff = None
        self.assertDictEqual(self.result['information_desks'][0],
                             {'accessibility': self.information_desk.accessibility,
                              'description': self.information_desk.description,
                              'email': self.information_desk.email,
                              'label_accessibility': {
                                  'id': self.information_desk.label_accessibility.pk,
                                  'pictogram': self.information_desk.label_accessibility.pictogram.url,
                                  'label': self.information_desk.label_accessibility.label,
                              },
                              'latitude': self.information_desk.latitude,
                              'longitude': self.information_desk.longitude,
                              'name': self.information_desk.name,
                              'phone': self.information_desk.phone,
                              'photo_url': self.information_desk.photo_url,
                              'postal_code': self.information_desk.postal_code,
                              'street': self.information_desk.street,
                              'municipality': self.information_desk.municipality,
                              'website': self.information_desk.website,
                              'type': {
                                  'id': desk_type.id,
                                  'pictogram': desk_type.pictogram.url,
                                  'label': desk_type.label}})

    def test_relationships(self):
        self.assertDictEqual(self.result['relationships'][0],
                             {'published': self.trek_b.published,
                              'has_common_departure': True,
                              'has_common_edge': False,
                              'is_circuit_step': True,
                              'trek': {'pk': self.trek_b.pk,
                                       'id': self.trek_b.id,
                                       'slug': self.trek_b.slug,
                                       'category_slug': 'trek',
                                       'name': self.trek_b.name}})

    def test_parking_location_in_wgs84(self):
        parking_location = self.result['parking_location']
        self.assertAlmostEqual(parking_location[0], -1.3630812101179008)

    def test_points_reference_are_exported_in_wgs84(self):
        geojson = self.result['points_reference']
        self.assertEqual(geojson['type'], 'MultiPoint')
        self.assertAlmostEqual(geojson['coordinates'][0][0], -1.363081210117901)

    def test_touristic_contents(self):
        self.assertEqual(len(self.result['touristic_contents']), 1)
        self.assertDictEqual(self.result['touristic_contents'][0], {
            'id': self.touristic_content.pk,
            'category_id': self.touristic_content.prefixed_category_id})

    def test_touristic_events(self):
        self.assertEqual(len(self.result['touristic_events']), 1)
        self.assertDictEqual(self.result['touristic_events'][0], {
            'id': self.touristic_event.pk,
            'category_id': self.touristic_event.prefixed_category_id})

    def test_close_treks(self):
        self.assertEqual(len(self.result['treks']), 1)
        self.assertDictEqual(self.result['treks'][0], {
            'id': self.trek_b.pk,
            'category_id': self.trek_b.prefixed_category_id})

    def test_type2(self):
        self.assertDictEqual(self.result['type2'][0],
                             {"id": self.accessibility.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, self.accessibility.pictogram.name),
                              "name": self.accessibility.name})

    def test_category(self):
        self.assertDictEqual(self.result['category'],
                             {"id": 'T',
                              "order": 1,
                              "label": "Hike",
                              "slug": "trek",
                              "type2_label": "Accessibility type",
                              "pictogram": "/static/trekking/trek.svg"})

    def test_sources(self):
        self.assertDictEqual(self.result['source'][0], {
            'name': self.source.name,
            'website': self.source.website,
            "pictogram": os.path.join(settings.MEDIA_URL, self.source.pictogram.name)})

    def portals(self):
        self.assertDictEqual(self.result['portal'][0], {
            'name': self.portal.name,
            'website': self.portal.website, })

    def test_children(self):
        self.assertEqual(self.result['children'], [self.child2.pk, self.child1.pk])

    def test_parents(self):
        self.assertEqual(self.result['parents'], [self.parent.pk])

    def test_previous(self):
        self.assertDictEqual(self.result['previous'],
                             {"%s" % self.parent.pk: None})

    def test_next(self):
        self.assertDictEqual(self.result['next'],
                             {"%s" % self.parent.pk: self.sibling.pk})

    def test_picture_print(self):
        self.assertIn(self.attachment.attachment_file.name, self.trek.picture_print.name)
        self.assertIn('.1000x500_q85_crop-smart.png', self.trek.picture_print.name)

    def test_thumbnail_display(self):
        self.assertIn('<img height="20" width="20" src="/media/%s.120x120_q85_crop.png"/>'
                      % self.attachment.attachment_file.name, self.trek.thumbnail_display)

    def test_thumbnail_csv_display(self):
        self.assertIn('%s.120x120_q85_crop.png'
                      % self.attachment.attachment_file.name, self.trek.thumbnail_csv_display)

    def test_reservation(self):
        self.assertEqual(self.result['reservation_system'], self.trek.reservation_system.name)
        self.assertEqual(self.result['reservation_id'], 'XXXXXXXXX')


class TrekPointsReferenceTest(TrekkingManagerTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.trek = TrekFactory.create()
        cls.trek.points_reference = MultiPoint([Point(0, 0), Point(1, 1)], srid=settings.SRID)
        cls.trek.save()

    def setUp(self):
        self.login()

    def test_points_reference_editable_as_hidden_input(self):
        url = self.trek.get_update_url()
        response = self.client.get(url)
        self.assertContains(response, 'name="points_reference"')

    @override_settings(TREK_POINTS_OF_REFERENCE_ENABLED=False)
    def test_points_reference_is_marked_as_disabled_when_disabled(self):
        url = self.trek.get_update_url()
        response = self.client.get(url)
        self.assertNotContains(response, 'name="points_reference"')


class TrekGPXTest(TrekkingManagerTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create a simple fake DEM
        conn = connections[DEFAULT_DB_ALIAS]
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO altimetry_dem (rast) VALUES (ST_MakeEmptyRaster(10, 10, 700040, 6600040, 10, 10, 0, 0, %s))',
            [settings.SRID])
        cur.execute('UPDATE altimetry_dem SET rast = ST_AddBand(rast, \'16BSI\')')
        for y in range(0, 1):
            for x in range(0, 1):
                cur.execute('UPDATE altimetry_dem SET rast = ST_SetValue(rast, %s, %s, %s::float)', [x + 1, y + 1, 42])

        cls.trek = TrekWithPOIsFactory.create()
        cls.trek.description_en = 'Nice trek'
        cls.trek.description_it = 'Bonnito iti'
        cls.trek.description_fr = 'Jolie rando'
        cls.trek.save()

        for poi in cls.trek.pois.all():
            poi.description_it = poi.description
            poi.published_it = True
            poi.save()

    def setUp(self):
        self.login()
        url = '/api/it/treks/{pk}/slug.gpx'.format(pk=self.trek.pk)
        self.response = self.client.get(url)
        self.parsed = BeautifulSoup(self.response.content, 'lxml')

    def tearDown(self):
        translation.deactivate()

    def test_gpx_is_served_with_content_type(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response['Content-Type'], 'application/gpx+xml')

    def test_gpx_trek_as_track_points(self):
        self.assertEqual(len(self.parsed.findAll('trk')), 1)
        self.assertEqual(len(self.parsed.findAll('trkpt')), 7)
        # 2 pois 7 treks
        self.assertEqual(len(self.parsed.findAll('ele')), 9)

    def test_gpx_translated_using_another_language(self):
        track = self.parsed.findAll('trk')[0]
        description = track.find('desc').string
        self.assertTrue(description.startswith(self.trek.description_it))

    def test_gpx_contains_pois(self):
        waypoints = self.parsed.findAll('wpt')
        pois = self.trek.published_pois.all()
        self.assertEqual(len(waypoints), len(pois))
        waypoint = waypoints[0]
        name = waypoint.find('name').string
        description = waypoint.find('desc').string
        elevation = waypoint.find('ele').string
        self.assertEqual(name, "%s: %s" % (pois[0].type, pois[0].name))
        self.assertEqual(description, pois[0].description)
        # POI order follows trek direction
        self.assertAlmostEqual(float(waypoint['lat']), 46.5003602)
        self.assertAlmostEqual(float(waypoint['lon']), 3.0005216)
        self.assertEqual(elevation, '42.0')


class TrekViewTranslationTest(TrekkingManagerTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.trek = TrekFactory.create()
        cls.trek.name_fr = 'Voie lactee'
        cls.trek.name_en = 'Milky way'
        cls.trek.name_it = 'Via Lattea'

        cls.trek.published_fr = True
        cls.trek.published_it = False
        cls.trek.save()

    def tearDown(self):
        translation.deactivate()
        self.client.logout()

    def test_json_translation(self):
        for lang, expected in [('fr', self.trek.name_fr),
                               ('it', 404)]:
            url = '/api/{lang}/treks/{pk}.json'.format(lang=lang, pk=self.trek.pk)
            response = self.client.get(url)
            if expected == 404:
                self.assertEqual(response.status_code, 404)
            else:
                self.assertEqual(response.status_code, 200)
                obj = response.json()
                self.assertEqual(obj['name'], expected)

    def test_geojson_translation(self):
        for lang, expected in [('fr', self.trek.name_fr),
                               ('it', self.trek.name_it)]:
            self.login()
            response = self.client.get(reverse('trekking:trek-drf-list', format="geojson"), HTTP_ACCEPT_LANGUAGE=lang)
            self.assertEqual(response.status_code, 200)
            obj = response.json()
            self.assertEqual(obj['features'][0]['properties']['name'], expected)
            self.client.logout()  # Django 1.6 keeps language in session

    def test_published_translation(self):
        for lang, expected in [('fr', self.trek.published_fr),
                               ('it', self.trek.published_it)]:
            self.login()
            response = self.client.get(reverse('trekking:trek-drf-list', format="geojson"), HTTP_ACCEPT_LANGUAGE=lang)
            self.assertEqual(response.status_code, 200)
            obj = response.json()
            self.assertEqual(obj['features'][0]['properties']['published'], expected)
            self.client.logout()  # Django 1.6 keeps language in session

    def test_poi_geojson_translation(self):
        # Create a Trek with a POI
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        poi = POIFactory.create(paths=[(p1, 0.6, 0.6)])
        poi.name_fr = "Chapelle"
        poi.name_en = "Chapel"
        poi.name_it = "Capela"
        poi.published_fr = True
        poi.published_en = True
        poi.published_it = True
        poi.save()
        trek = TrekFactory.create(paths=[(p1, 0.5, 1)], published_fr=True, published_it=True)
        # Check that it applies to GeoJSON also :
        self.assertEqual(len(trek.pois), 1)
        poi = trek.pois[0]
        for lang, expected in [('fr', poi.name_fr),
                               ('it', poi.name_it)]:
            url = '/api/{lang}/treks/{pk}/pois.geojson'.format(lang=lang, pk=trek.pk)
            self.login()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            obj = response.json()
            jsonpoi = obj.get('features', [])[0]
            self.assertEqual(jsonpoi.get('properties', {}).get('name'), expected)
            self.client.logout()  # Django 1.6 keeps language in session


class TemplateTagsTest(TestCase):
    def test_duration(self):
        self.assertEqual("15 min", geotrek_tags.duration(0.25))
        self.assertEqual("30 min", geotrek_tags.duration(0.5))
        self.assertEqual("1 h", geotrek_tags.duration(1))
        self.assertEqual("1 h 45", geotrek_tags.duration(1.75))
        self.assertEqual("3 h 30", geotrek_tags.duration(3.5))
        self.assertEqual("4 h", geotrek_tags.duration(4))
        self.assertEqual("6 h", geotrek_tags.duration(6))
        self.assertEqual("10 h", geotrek_tags.duration(10))
        self.assertEqual("1 day", geotrek_tags.duration(24))
        self.assertEqual("2 days", geotrek_tags.duration(32))
        self.assertEqual("2 days", geotrek_tags.duration(48))
        self.assertEqual("3 days", geotrek_tags.duration(49))
        self.assertEqual("8 days", geotrek_tags.duration(24 * 8))
        self.assertEqual("9 days", geotrek_tags.duration(24 * 9))


class TrekViewsSameStructureTests(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.content1 = TrekFactory.create()
        structure = StructureFactory.create()
        cls.content2 = TrekFactory.create(structure=structure)

    def setUp(self):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        self.user = profile.user
        self.user.groups.add(Group.objects.get(name="Référents communication"))
        self.client.force_login(user=self.user)

    def add_bypass_perm(self):
        perm = Permission.objects.get(codename='can_bypass_structure')
        self.user.user_permissions.add(perm)

    def test_edit_button_same_structure(self):
        url = "/trek/{pk}/".format(pk=self.content1.pk)
        response = self.client.get(url)
        self.assertContains(response,
                            '<a class="btn btn-primary ml-auto" '
                            'href="/trek/edit/{pk}/">'
                            '<i class="bi bi-pencil-square"></i> '
                            'Update</a>'.format(pk=self.content1.pk),
                            html=True)

    def test_edit_button_other_structure(self):
        url = "/trek/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertContains(response,
                            '<span class="btn ml-auto disabled" href="#">'
                            '<i class="bi bi-pencil-square"></i> Update</span>',
                            html=True)

    def test_edit_button_bypass_structure(self):
        self.add_bypass_perm()
        url = "/trek/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertContains(response,
                            '<a class="btn btn-primary ml-auto" '
                            'href="/trek/edit/{pk}/">'
                            '<i class="bi bi-pencil-square"></i> '
                            'Update</a>'.format(pk=self.content2.pk),
                            html=True)

    def test_can_edit_same_structure(self):
        url = "/trek/edit/{pk}/".format(pk=self.content1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_other_structure(self):
        url = "/trek/edit/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/trek/{pk}/".format(pk=self.content2.pk))

    def test_can_edit_bypass_structure(self):
        self.add_bypass_perm()
        url = "/trek/edit/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_can_delete_same_structure(self):
        url = "/trek/delete/{pk}/".format(pk=self.content1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_other_structure(self):
        url = "/trek/delete/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/trek/{pk}/".format(pk=self.content2.pk))

    def test_can_delete_bypass_structure(self):
        self.add_bypass_perm()
        url = "/trek/delete/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class POIViewsSameStructureTests(TranslationResetMixin, AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.content1 = POIFactory.create()
        structure = StructureFactory.create()
        cls.content2 = POIFactory.create(structure=structure)

    def setUp(self):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        user = profile.user
        user.groups.add(Group.objects.get(name="Référents communication"))
        self.client.force_login(user=user)

    def tearDown(self):
        self.client.logout()

    def test_can_edit_same_structure(self):
        url = "/poi/edit/{pk}/".format(pk=self.content1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_edit_other_structure(self):
        url = "/poi/edit/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/poi/{pk}/".format(pk=self.content2.pk))

    def test_can_delete_same_structure(self):
        url = "/poi/delete/{pk}/".format(pk=self.content1.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_cannot_delete_other_structure(self):
        url = "/poi/delete/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertRedirects(response, "/poi/{pk}/".format(pk=self.content2.pk))


class TrekWorkflowTest(TranslationResetMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('update_geotrek_permissions', verbosity=0)
        cls.trek = TrekFactory.create(published=False)
        cls.user = User.objects.create_user('omer', password='booh')
        cls.user.user_permissions.add(Permission.objects.get(codename='add_trek'))
        cls.user.user_permissions.add(Permission.objects.get(codename='change_trek'))

    def setUp(self):
        self.client.force_login(user=self.user)

    def tearDown(self):
        self.client.logout()

    def test_cannot_publish(self):
        response = self.client.get('/trek/add/')
        self.assertNotContains(response, 'Published')
        response = self.client.get('/trek/edit/%u/' % self.trek.pk)
        self.assertNotContains(response, 'Published')

    def test_can_publish(self):
        self.user.user_permissions.add(Permission.objects.get(codename='publish_trek'))
        response = self.client.get('/trek/add/')
        self.assertContains(response, 'Published')
        response = self.client.get('/trek/edit/%u/' % self.trek.pk)
        self.assertContains(response, 'Published')


class ServiceViewsTest(GeotrekAPITestCase, CommonTest):
    model = Service
    modelfactory = ServiceFactory
    userfactory = TrekkingManagerFactory
    expected_json_geom = {'type': 'Point', 'coordinates': [3.0, 46.5]}
    extra_column_list = ['type', 'eid']
    expected_column_list_extra = ['id', 'name', 'type', 'eid']
    expected_column_formatlist_extra = ['id', 'type', 'eid']

    def get_expected_json_attrs(self):
        return {
            'structure': {
                'id': self.obj.structure.pk,
                'name': 'My structure'
            },
            'type': {
                'id': self.obj.type.pk,
                'name': 'Service type',
                'pictogram': '/media/upload/service-type.png'
            }
        }

    def get_expected_datatables_attrs(self):
        return {
            'id': self.obj.pk,
            'name': self.obj.name_display,
        }

    def get_good_data(self):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            PathFactory.create()
            return {
                'type': ServiceTypeFactory.create().pk,
                'topology': '{"lat": 5.1, "lng": 6.6}',
            }
        else:
            return {
                'type': ServiceTypeFactory.create().pk,
                'geom': 'POINT(5.1 6.6)',
            }

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_empty_topology(self):
        data = self.get_good_data()
        data['topology'] = ''
        response = self.client.post(self.model.get_add_url(), data)
        self.assertEqual(response.status_code, 200)
        form = self.get_form(response)
        self.assertEqual(form.errors, {'topology': ['Topology is empty.']})

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_empty_topology_nds(self):
        data = self.get_good_data()
        data['geom'] = ''
        response = self.client.post(self.model.get_add_url(), data)
        self.assertEqual(response.status_code, 200)
        form = self.get_form(response)
        self.assertEqual(form.errors, {'geom': ['No geometry value provided.']})

    def test_listing_number_queries(self):
        # Create many instances
        self.modelfactory.build_batch(1000)
        DistrictFactory.build_batch(10)

        with self.assertNumQueries(6):
            self.client.get(self.model.get_datatablelist_url())

        with self.assertNumQueries(7):
            self.client.get(self.model.get_format_list_url())

    def test_services_on_treks_do_not_exist(self):
        self.modelfactory.create()

        response = self.client.get(reverse('trekking:trek_service_geojson',
                                           kwargs={'lang': translation.get_language(), 'pk': 0}))
        self.assertEqual(response.status_code, 404)

    def test_services_on_treks_not_public(self):
        self.modelfactory.create()

        trek = TrekFactory.create(published=False)
        response = self.client.get(reverse('trekking:trek_service_geojson',
                                           kwargs={'lang': translation.get_language(), 'pk': trek.pk}))
        self.assertEqual(response.status_code, 200)

    def test_services_on_treks_not_public_anonymous(self):
        self.logout()
        self.modelfactory.create()

        trek = TrekFactory.create(published=False)
        response = self.client.get(reverse('trekking:trek_service_geojson',
                                           kwargs={'lang': translation.get_language(), 'pk': trek.pk}))
        self.assertEqual(response.status_code, 404)


class ServiceJSONTest(TrekkingManagerTest):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.service = ServiceFactory.create(type__published=True)
        cls.pk = cls.service.pk

    def setUp(self):
        self.login()

    def test_list(self):
        url = '/api/en/services.json'
        self.response = self.client.get(url)
        self.result = self.response.json()
        self.assertEqual(len(self.result), 1)
        self.assertTrue('type' in self.result[0])

    def test_detail(self):
        url = '/api/en/services/%s.json' % self.pk
        self.response = self.client.get(url)
        self.result = self.response.json()
        self.assertDictEqual(self.result['type'],
                             {'id': self.service.type.pk,
                              'name': self.service.type.name,
                              'pictogram': os.path.join(settings.MEDIA_URL, self.service.type.pictogram.name),
                              })


class TestDepublishSignagesRemovedFromPDF(TestCase):

    def setUp(self):
        self.trek = TrekWithSignagesFactory.create()

    @mock.patch('mapentity.helpers.requests.get')
    def test_depublish_signage_refreshes_pdf(self, mock_get):
        # Mock map screenshot
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        # Assert first access to PDF will trigger screenshot
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path(), self.trek.get_date_update()))
        self.client.get(
            reverse('trekking:trek_printable', kwargs={'lang': 'fr', 'pk': self.trek.pk, 'slug': self.trek.slug}))
        # Assert second access to PDF will not trigger screenshot
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertTrue(is_file_uptodate(trek.get_map_image_path(), trek.get_date_update()))
        # Assert access to PDF if signages were changed will trigger screenshot
        trek.signages[0].published = False
        trek.signages[0].save()
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertFalse(is_file_uptodate(trek.get_map_image_path(), trek.get_date_update()))

    @mock.patch('mapentity.helpers.requests.get')
    def test_delete_signage_refreshes_pdf(self, mock_get):
        # Mock map screenshot
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        # Assert first access to PDF will trigger screenshot
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path(), self.trek.get_date_update()))
        self.client.get(
            reverse('trekking:trek_printable', kwargs={'lang': 'fr', 'pk': self.trek.pk, 'slug': self.trek.slug}))
        # Assert second access to PDF will not trigger screenshot
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertTrue(is_file_uptodate(trek.get_map_image_path(), trek.get_date_update()))
        # Assert access to PDF if signage was deleted will trigger screenshot
        trek.signages[0].delete()
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertFalse(is_file_uptodate(trek.get_map_image_path(), trek.get_date_update()))


class TestDepublishInfrastructuresRemovedFromPDF(TestCase):

    def setUp(self):
        self.trek = TrekWithInfrastructuresFactory.create()

    @mock.patch('mapentity.helpers.requests.get')
    def test_depublish_infrastructure_refreshes_pdf(self, mock_get):
        # Mock map screenshot
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        # Assert first access to PDF will trigger screenshot
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path(), self.trek.get_date_update()))
        self.client.get(
            reverse('trekking:trek_printable', kwargs={'lang': 'fr', 'pk': self.trek.pk, 'slug': self.trek.slug}))
        # Assert second access to PDF will not trigger screenshot
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertTrue(is_file_uptodate(trek.get_map_image_path(), trek.get_date_update()))
        # Assert access to PDF if signages were changed will trigger screenshot
        trek.infrastructures[0].published = False
        trek.infrastructures[0].save()
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertFalse(is_file_uptodate(trek.get_map_image_path(), trek.get_date_update()))

    @mock.patch('mapentity.helpers.requests.get')
    def test_delete_infrastructure_refreshes_pdf(self, mock_get):
        # Mock map screenshot
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        # Assert first access to PDF will trigger screenshot
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path(), self.trek.get_date_update()))
        self.client.get(
            reverse('trekking:trek_printable', kwargs={'lang': 'fr', 'pk': self.trek.pk, 'slug': self.trek.slug}))
        # Assert second access to PDF will not trigger screenshot
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertTrue(is_file_uptodate(trek.get_map_image_path(), trek.get_date_update()))
        # Assert access to PDF if signage was deleted will trigger screenshot
        trek.infrastructures[0].delete()
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertFalse(is_file_uptodate(trek.get_map_image_path(), trek.get_date_update()))
