import csv
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
from geotrek.common.tests import CommonTest, CommonLiveTest, TranslationResetMixin
from geotrek.common.tests.factories import AttachmentFactory, ThemeFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.core.tests.factories import PathFactory
from geotrek.tourism.tests import factories as tourism_factories
# Make sur to register Trek model
from geotrek.trekking import urls  # NOQA
from geotrek.trekking import views as trekking_views
from geotrek.zoning.tests.factories import DistrictFactory, CityFactory
from .base import TrekkingManagerTest
from .factories import (POIFactory, POITypeFactory, TrekFactory, TrekWithPOIsFactory,
                        TrekNetworkFactory, WebLinkFactory, AccessibilityFactory,
                        ServiceFactory, ServiceTypeFactory,
                        TrekWithServicesFactory, TrekWithInfrastructuresFactory,
                        TrekWithSignagesFactory, PracticeFactory)
from ..models import POI, Trek, Service


class POIViewsTest(CommonTest):
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
            'name': self.obj.name,
            'published': self.obj.published
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

        with self.assertNumQueries(5):
            self.client.get(self.model.get_datatablelist_url())

        with self.assertNumQueries(8):
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


class TrekViewsTest(CommonTest):
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
            'name': self.obj.name,
            'published': self.obj.published
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
        self.parsed = BeautifulSoup(self.response.content, features='xml')

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
        self.client.logout()

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


class ServiceViewsTest(CommonTest):
    model = Service
    modelfactory = ServiceFactory
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
            'name': str(self.obj),
            'published': self.obj.type.published
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

        with self.assertNumQueries(5):
            self.client.get(self.model.get_datatablelist_url())

        with self.assertNumQueries(4):
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


class TrekPDFChangeAlongLinkedSignages(TestCase):
    def setUp(self):
        self.trek = TrekWithSignagesFactory.create()

    @mock.patch('mapentity.helpers.requests.get')
    def test_unpublish_signage_refreshes_pdf(self, mock_get):
        # Mock map screenshot
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        # Assert first access to PDF will trigger screenshot
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))
        self.client.get(
            reverse('trekking:trek_printable', kwargs={'lang': 'fr', 'pk': self.trek.pk, 'slug': self.trek.slug}))
        # Assert second access to PDF will not trigger screenshot
        self.trek.refresh_from_db()
        self.assertTrue(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))
        # Assert access to PDF if signages were changed will trigger screenshot
        self.trek.signages[0].published = False
        self.trek.signages[0].save()
        self.trek.refresh_from_db()
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))

    @mock.patch('mapentity.helpers.requests.get')
    def test_delete_signage_refreshes_pdf(self, mock_get):
        # Mock map screenshot
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        # Assert first access to PDF will trigger screenshot
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))
        self.client.get(
            reverse('trekking:trek_printable', kwargs={'lang': 'fr', 'pk': self.trek.pk, 'slug': self.trek.slug}))
        # Assert second access to PDF will not trigger screenshot
        self.trek.refresh_from_db()
        self.assertTrue(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))
        # Assert access to PDF if signage was deleted will trigger screenshot
        self.trek.signages[0].delete()
        self.trek.refresh_from_db()
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))


class TrekPDFChangeAlongLinkedInfrastructures(TestCase):
    def setUp(self):
        self.trek = TrekWithInfrastructuresFactory.create()

    @mock.patch('mapentity.helpers.requests.get')
    def test_unpublish_infrastructure_refreshes_pdf(self, mock_get):
        # Mock map screenshot
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        # Assert first access to PDF will trigger screenshot
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))
        response = self.client.get(reverse('trekking:trek_printable',
                                           kwargs={'lang': 'fr', 'pk': self.trek.pk, 'slug': self.trek.slug}))
        self.assertEqual(response.status_code, 200)
        # Assert second access to PDF will not trigger screenshot
        self.trek.refresh_from_db()
        self.assertTrue(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))
        # Assert access to PDF if signages were changed will trigger screenshot
        self.trek.infrastructures[0].published = False
        self.trek.infrastructures[0].save()
        self.trek.refresh_from_db()
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))

    @mock.patch('mapentity.helpers.requests.get')
    def test_delete_infrastructure_refreshes_pdf(self, mock_get):
        # Mock map screenshot
        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b'xxx'
        # Assert first access to PDF will trigger screenshot
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))
        self.client.get(
            reverse('trekking:trek_printable', kwargs={'lang': 'fr', 'pk': self.trek.pk, 'slug': self.trek.slug}))
        # Assert second access to PDF will not trigger screenshot
        self.trek.refresh_from_db()
        self.assertTrue(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))
        # Assert access to PDF if signage was deleted will trigger screenshot
        self.trek.infrastructures[0].delete()
        self.trek.refresh_from_db()
        self.assertFalse(is_file_uptodate(self.trek.get_map_image_path('fr'), self.trek.get_date_update()))
