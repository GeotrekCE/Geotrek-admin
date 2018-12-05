#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import datetime
from collections import OrderedDict

import mock
from bs4 import BeautifulSoup

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User, Group, Permission
from django.contrib.gis.geos import LineString, MultiPoint, Point
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.db import connection, connections, DEFAULT_DB_ALIAS
from django.template.loader import get_template
from django.test import RequestFactory
from django.test.utils import override_settings
from django.utils import translation
from django.utils.timezone import utc, make_aware
from unittest import util as testutil

from mapentity.tests import MapEntityLiveTest
from mapentity.factories import SuperUserFactory

from geotrek.authent.models import default_structure
from geotrek.common.factories import (AttachmentFactory, ThemeFactory,
                                      RecordSourceFactory, TargetPortalFactory)
from geotrek.common.tests import CommonTest, TranslationResetMixin
from geotrek.common.utils.testdata import get_dummy_uploaded_image
from geotrek.authent.factories import TrekkingManagerFactory, StructureFactory, UserProfileFactory
from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.core.factories import PathFactory
from geotrek.zoning.factories import DistrictFactory, CityFactory
from geotrek.trekking.models import POI, Trek, Service, OrderedTrekChild
from geotrek.trekking.factories import (POIFactory, POITypeFactory, TrekFactory, TrekWithPOIsFactory,
                                        TrekNetworkFactory, WebLinkFactory, AccessibilityFactory,
                                        TrekRelationshipFactory, ServiceFactory, ServiceTypeFactory,
                                        TrekWithServicesFactory)
from geotrek.trekking.templatetags import trekking_tags
from geotrek.trekking.serializers import timestamp
from geotrek.trekking import views as trekking_views
from geotrek.tourism import factories as tourism_factories

# Make sur to register Trek model
from geotrek.trekking import urls  # NOQA

from .base import TrekkingManagerTest


class POIViewsTest(CommonTest):
    model = POI
    modelfactory = POIFactory
    userfactory = TrekkingManagerFactory

    def get_good_data(self):
        PathFactory.create()
        return {
            'name_fr': 'test',
            'name_en': 'test',
            'description_fr': 'ici',
            'description_en': 'here',
            'type': POITypeFactory.create().pk,
            'topology': '{"lat": 5.1, "lng": 6.6}',
            'structure': default_structure().pk
        }

    def test_empty_topology(self):
        self.login()
        data = self.get_good_data()
        data['topology'] = ''

        response = self.client.post(self.model.get_add_url(), data)
        self.assertEqual(response.status_code, 200)
        form = self.get_form(response)
        self.assertEqual(form.errors, {'topology': [u'Topology is empty.']})

    def test_listing_number_queries(self):
        self.login()
        # Create many instances
        for i in range(100):
            self.modelfactory.create()
        for i in range(10):
            DistrictFactory.create()

        # Enable query counting
        settings.DEBUG = True

        for url in [self.model.get_jsonlist_url(),
                    self.model.get_format_list_url()]:
            num_queries_old = len(connection.queries)
            self.client.get(url)
            num_queries_new = len(connection.queries)

            nb_queries = num_queries_new - num_queries_old
            self.assertTrue(0 < nb_queries < 100, '%s queries !' % nb_queries)

        settings.DEBUG = False


class POIJSONDetailTest(TrekkingManagerTest):
    def setUp(self):
        self.login()

        polygon = 'SRID=%s;MULTIPOLYGON(((700000 6600000, 700000 6600003, 700003 6600003, 700003 6600000, 700000 6600000)))' % settings.SRID
        self.city = CityFactory(geom=polygon)
        self.district = DistrictFactory(geom=polygon)

        self.poi = POIFactory.create(published=True)

        self.attachment = AttachmentFactory.create(obj=self.poi,
                                                   attachment_file=get_dummy_uploaded_image())

        self.touristic_content = tourism_factories.TouristicContentFactory(
            geom='SRID=%s;POINT(700001 6600001)' % settings.SRID, published=True)
        tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(700001 6600001)' % settings.SRID,
                                                  published=False)  # not published
        tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(700001 6600001)' % settings.SRID,
                                                  published=True).delete()  # deleted
        tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(701000 6601000)' % settings.SRID,
                                                  published=True)  # too far
        self.touristic_event = tourism_factories.TouristicEventFactory(
            geom='SRID=%s;POINT(700002 6600002)' % settings.SRID, published=True)
        tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(700002 6600002)' % settings.SRID,
                                                published=False)  # not published
        tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(700002 6600002)' % settings.SRID,
                                                published=True).delete()  # deleted
        tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(702000 6602000)' % settings.SRID,
                                                published=True)  # too far

        self.pk = self.poi.pk
        url = '/api/en/pois/%s.json' % self.pk
        self.response = self.client.get(url)
        self.result = json.loads(self.response.content)

    def test_name(self):
        self.assertEqual(self.result['name'],
                         self.poi.name)

    def test_slug(self):
        self.assertEqual(self.result['slug'],
                         self.poi.slug)

    def test_published(self):
        self.assertEqual(self.result['published'], True)

    def test_published_status(self):
        self.assertDictEqual(self.result['published_status'][0],
                             {u'lang': u'en', u'status': True, u'language': u'English'})

    def test_type(self):
        self.assertDictEqual(self.result['type'],
                             {'id': self.poi.type.pk,
                              'label': self.poi.type.label,
                              'pictogram': os.path.join(settings.MEDIA_URL, self.poi.type.pictogram.name),
                              })

    def test_altimetry(self):
        self.assertEqual(self.result['min_elevation'], 0.0)

    def test_cities(self):
        self.assertEqual(self.result['cities'], [])

    def test_districts(self):
        self.assertDictEqual(self.result['districts'][0],
                             {u"id": self.district.id,
                              u"name": self.district.name})

    def test_related_urls(self):
        self.assertEqual(self.result['map_image_url'],
                         '/image/poi-%s.png' % self.pk)
        self.assertEqual(self.result['filelist_url'],
                         '/paperclip/get/trekking/poi/%s/' % self.pk)

    def test_touristic_contents(self):
        self.assertEqual(len(self.result['touristic_contents']), 1)
        self.assertDictEqual(self.result['touristic_contents'][0], {
            u'id': self.touristic_content.pk,
            u'category_id': self.touristic_content.prefixed_category_id})

    def test_touristic_events(self):
        self.assertEqual(len(self.result['touristic_events']), 1)
        self.assertDictEqual(self.result['touristic_events'][0], {
            u'id': self.touristic_event.pk,
            u'category_id': 'E'})


class TrekViewsTest(CommonTest):
    model = Trek
    modelfactory = TrekFactory
    userfactory = TrekkingManagerFactory

    def get_bad_data(self):
        return OrderedDict([
            ('name_en', ''),
            ('trek_relationship_a-TOTAL_FORMS', '0'),
            ('trek_relationship_a-INITIAL_FORMS', '1'),
            ('trek_relationship_a-MAX_NUM_FORMS', '0'),
        ]), u'This field is required.'

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'name_fr': 'Huhu',
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
            'disabled_infrastructure_fr': '',
            'disabled_infrastructure_en': '',
            'duration': '0',
            'is_park_centered': '',
            'advised_parking': 'Very close',
            'parking_location': 'POINT (1.0 1.0)',
            'public_transport': 'huhu',
            'advice_fr': '',
            'advice_en': '',
            'themes': ThemeFactory.create().pk,
            'networks': TrekNetworkFactory.create().pk,
            'practice': '',
            'accessibilities': AccessibilityFactory.create().pk,
            'web_links': WebLinkFactory.create().pk,
            'information_desks': tourism_factories.InformationDeskFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,

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
            'structure': default_structure().pk
        }

    def test_badfield_goodgeom(self):
        self.login()

        bad_data, form_error = self.get_bad_data()
        bad_data['parking_location'] = 'POINT (1.0 1.0)'  # good data

        url = self.model.get_add_url()
        response = self.client.post(url, bad_data)
        self.assertEqual(response.status_code, 200)
        form = self.get_form(response)
        self.assertEqual(form.data['parking_location'], bad_data['parking_location'])

    def test_basic_format(self):
        super(TrekViewsTest, self).test_basic_format()
        self.modelfactory.create(name="ukélélé")  # trek with utf8
        for fmt in ('csv', 'shp', 'gpx'):
            response = self.client.get(self.model.get_format_list_url() + '?format=' + fmt)
            self.assertEqual(response.status_code, 200)


class TrekViewsLiveTest(MapEntityLiveTest):
    model = Trek
    modelfactory = TrekFactory
    userfactory = SuperUserFactory


class TrekCustomViewTests(TrekkingManagerTest):
    def setUp(self):
        self.login()

    def test_pois_geojson(self):
        trek = TrekWithPOIsFactory.create(published=True)
        self.assertEqual(len(trek.pois), 2)
        poi = trek.pois[0]
        poi.published = True
        poi.save()
        AttachmentFactory.create(obj=poi, attachment_file=get_dummy_uploaded_image())
        self.assertNotEqual(poi.thumbnail, None)
        self.assertEqual(len(trek.pois), 2)

        url = '/api/en/treks/{pk}/pois.geojson'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        poislayer = json.loads(response.content)
        poifeature = poislayer['features'][0]
        self.assertTrue('thumbnail' in poifeature['properties'])

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
        serviceslayer = json.loads(response.content)
        servicefeature = serviceslayer['features'][0]
        self.assertTrue('type' in servicefeature['properties'])

    def test_kml(self):
        trek = TrekWithPOIsFactory.create()
        url = '/api/en/treks/{pk}/slug.kml'.format(pk=trek.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.google-earth.kml+xml')

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
        overriden_template = os.path.join(settings.MEDIA_ROOT, 'templates', 'trekking', 'trek_public.odt')

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


class TrekJSONDetailTest(TrekkingManagerTest):
    """ Since we migrated some code to Django REST Framework, we should test
    the migration extensively. Geotrek-rando mainly relies on this view.
    """

    def setUp(self):
        self.login()

        polygon = 'SRID=%s;MULTIPOLYGON(((0 0, 0 3, 3 3, 3 0, 0 0)))' % settings.SRID
        self.city = CityFactory(geom=polygon)
        self.district = DistrictFactory(geom=polygon)

        self.trek = TrekFactory.create(
            name='Step 2',
            no_path=True,
            points_reference=MultiPoint([Point(0, 0), Point(1, 1)], srid=settings.SRID),
            parking_location=Point(0, 0, srid=settings.SRID)
        )
        path1 = PathFactory.create(geom='SRID=%s;LINESTRING(0 0, 1 0)' % settings.SRID)
        self.trek.add_path(path1)

        self.attachment = AttachmentFactory.create(obj=self.trek,
                                                   attachment_file=get_dummy_uploaded_image())

        self.information_desk = tourism_factories.InformationDeskFactory.create()
        self.trek.information_desks.add(self.information_desk)

        self.theme = ThemeFactory.create()
        self.trek.themes.add(self.theme)

        self.accessibility = AccessibilityFactory.create()
        self.trek.accessibilities.add(self.accessibility)

        self.network = TrekNetworkFactory.create()
        self.trek.networks.add(self.network)

        self.weblink = WebLinkFactory.create()
        self.trek.web_links.add(self.weblink)

        self.source = RecordSourceFactory.create()
        self.trek.source.add(self.source)

        self.portal = TargetPortalFactory.create()
        self.trek.portal.add(self.portal)

        self.trek_b = TrekFactory.create(no_path=True,
                                         geom='SRID=%s;POINT(2 2)' % settings.SRID,
                                         published=True)
        path2 = PathFactory.create(geom='SRID=%s;LINESTRING(0 1, 1 1)' % settings.SRID)
        self.trek_b.add_path(path2)
        TrekRelationshipFactory.create(has_common_departure=True,
                                       has_common_edge=False,
                                       is_circuit_step=True,
                                       trek_a=self.trek,
                                       trek_b=self.trek_b)

        self.touristic_content = tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(1 1)' % settings.SRID,
                                                                           published=True)
        tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(1 1)' % settings.SRID,
                                                  published=False)  # not published
        tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(1 1)' % settings.SRID,
                                                  published=True).delete()  # deleted
        tourism_factories.TouristicContentFactory(geom='SRID=%s;POINT(1000 1000)' % settings.SRID,
                                                  published=True)  # too far
        self.touristic_event = tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(2 2)' % settings.SRID,
                                                                       published=True)
        tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(2 2)' % settings.SRID,
                                                published=False)  # not published
        tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(2 2)' % settings.SRID,
                                                published=True).delete()  # deleted
        tourism_factories.TouristicEventFactory(geom='SRID=%s;POINT(2000 2000)' % settings.SRID,
                                                published=True)  # too far
        trek2 = TrekFactory(no_path=True, published=False)  # not published
        trek2.add_path(path2)
        self.trek3 = TrekFactory(no_path=True, published=True)  # deleted
        self.trek3.add_path(path2)
        self.trek3.delete()
        trek4 = TrekFactory(no_path=True, published=True)  # too far
        trek4.add_path(PathFactory.create(geom='SRID=%s;LINESTRING(0 2000, 1 2000)' % settings.SRID))

        self.parent = TrekFactory.create(published=True, name='Parent')
        self.child1 = TrekFactory.create(published=False, name='Child 1')
        self.child2 = TrekFactory.create(published=True, name='Child 2')
        self.sibling = TrekFactory.create(published=True, name='Sibling')
        OrderedTrekChild(parent=self.parent, child=self.trek, order=0).save()
        OrderedTrekChild(parent=self.trek, child=self.child1, order=3).save()
        OrderedTrekChild(parent=self.trek, child=self.child2, order=2).save()
        OrderedTrekChild(parent=self.parent, child=self.sibling, order=1).save()

        self.pk = self.trek.pk
        url = '/api/en/treks/{pk}.json'.format(pk=self.pk)
        self.response = self.client.get(url)
        self.result = json.loads(self.response.content)

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
                             {u'lang': u'en', u'status': True, u'language': u'English'})

    def test_pictures(self):
        self.assertDictEqual(self.result['pictures'][0],
                             {u'url': os.path.join(settings.MEDIA_URL,
                                                   self.attachment.attachment_file.name) + '.800x800_q85.png',
                              u'title': self.attachment.title,
                              u'legend': self.attachment.legend,
                              u'author': self.attachment.author})

    def test_cities(self):
        self.assertDictEqual(self.result['cities'][0],
                             {u"code": self.city.code,
                              u"name": self.city.name})

    def test_districts(self):
        self.assertDictEqual(self.result['districts'][0],
                             {u"id": self.district.id,
                              u"name": self.district.name})

    def test_networks(self):
        self.assertDictEqual(self.result['networks'][0],
                             {u"id": self.network.id,
                              u"pictogram": None,
                              u"name": self.network.network})

    def test_practice_not_none(self):
        self.assertDictEqual(self.result['practice'],
                             {u"id": self.trek.practice.id,
                              u"pictogram": os.path.join(settings.MEDIA_URL, self.trek.practice.pictogram.name),
                              u"label": self.trek.practice.name})

    def test_usages(self):  # Rando v1 compat
        self.assertDictEqual(self.result['usages'][0],
                             {u"id": self.trek.practice.id,
                              u"pictogram": os.path.join(settings.MEDIA_URL, self.trek.practice.pictogram.name),
                              u"label": self.trek.practice.name})

    def test_accessibilities(self):
        self.assertDictEqual(self.result['accessibilities'][0],
                             {u"id": self.accessibility.id,
                              u"pictogram": os.path.join(settings.MEDIA_URL, self.accessibility.pictogram.name),
                              u"label": self.accessibility.name})

    def test_themes(self):
        self.assertDictEqual(self.result['themes'][0],
                             {u"id": self.theme.id,
                              u"pictogram": os.path.join(settings.MEDIA_URL, self.theme.pictogram.name),
                              u"label": self.theme.label})

    def test_weblinks(self):
        self.assertDictEqual(self.result['web_links'][0],
                             {u"id": self.weblink.id,
                              u"url": self.weblink.url,
                              u"name": self.weblink.name,
                              u"category": {
                                  u"id": self.weblink.category.id,
                                  u"pictogram": os.path.join(settings.MEDIA_URL, self.weblink.category.pictogram.name),
                                  u"label": self.weblink.category.label}
                              })

    def test_route_not_none(self):
        self.assertDictEqual(self.result['route'],
                             {u"id": self.trek.route.id,
                              u"pictogram": None,
                              u"label": self.trek.route.route})

    def test_difficulty_not_none(self):
        self.assertDictEqual(self.result['difficulty'],
                             {u"id": self.trek.difficulty.id,
                              u"pictogram": os.path.join(settings.MEDIA_URL, self.trek.difficulty.pictogram.name),
                              u"label": self.trek.difficulty.difficulty})

    def test_information_desks(self):
        desk_type = self.information_desk.type
        self.maxDiff = None
        self.assertDictEqual(self.result['information_desks'][0],
                             {u'description': self.information_desk.description,
                              u'email': self.information_desk.email,
                              u'latitude': self.information_desk.latitude,
                              u'longitude': self.information_desk.longitude,
                              u'name': self.information_desk.name,
                              u'phone': self.information_desk.phone,
                              u'photo_url': self.information_desk.photo_url,
                              u'postal_code': self.information_desk.postal_code,
                              u'street': self.information_desk.street,
                              u'municipality': self.information_desk.municipality,
                              u'website': self.information_desk.website,
                              u'type': {
                                  u'id': desk_type.id,
                                  u'pictogram': desk_type.pictogram.url,
                                  u'label': desk_type.label}})

    def test_relationships(self):
        self.assertDictEqual(self.result['relationships'][0],
                             {u'published': self.trek_b.published,
                              u'has_common_departure': True,
                              u'has_common_edge': False,
                              u'is_circuit_step': True,
                              u'trek': {u'pk': self.trek_b.pk,
                                        u'id': self.trek_b.id,
                                        u'slug': self.trek_b.slug,
                                        u'category_slug': u'trek',
                                        u'name': self.trek_b.name}})

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
            u'id': self.touristic_content.pk,
            u'category_id': self.touristic_content.prefixed_category_id})

    def test_touristic_events(self):
        self.assertEqual(len(self.result['touristic_events']), 1)
        self.assertDictEqual(self.result['touristic_events'][0], {
            u'id': self.touristic_event.pk,
            u'category_id': self.touristic_event.prefixed_category_id})

    def test_close_treks(self):
        self.assertEqual(len(self.result['treks']), 1)
        self.assertDictEqual(self.result['treks'][0], {
            u'id': self.trek_b.pk,
            u'category_id': self.trek_b.prefixed_category_id})

    def test_type1(self):
        self.assertDictEqual(self.result['type1'][0],
                             {u"id": self.trek.practice.id,
                              u"pictogram": os.path.join(settings.MEDIA_URL, self.trek.practice.pictogram.name),
                              u"name": self.trek.practice.name})

    def test_type2(self):
        self.assertDictEqual(self.result['type2'][0],
                             {u"id": self.accessibility.id,
                              u"pictogram": os.path.join(settings.MEDIA_URL, self.accessibility.pictogram.name),
                              u"name": self.accessibility.name})

    def test_category(self):
        self.assertDictEqual(self.result['category'],
                             {u"id": 'T',
                              u"order": None,
                              u"label": u"Trek",
                              u"slug": u"trek",
                              u"type1_label": u"Practice",
                              u"type2_label": u"Accessibility",
                              u"pictogram": u"/static/trekking/trek.svg"})

    def test_sources(self):
        self.assertDictEqual(self.result['source'][0], {
            u'name': self.source.name,
            u'website': self.source.website,
            u"pictogram": os.path.join(settings.MEDIA_URL, self.source.pictogram.name)})

    def portals(self):
        self.assertDictEqual(self.result['portal'][0], {
            u'name': self.portal.name,
            u'website': self.portal.website, })

    def test_children(self):
        self.assertEqual(self.result['children'], [self.child2.pk, self.child1.pk])

    def test_parents(self):
        self.assertEqual(self.result['parents'], [self.parent.pk])

    def test_previous(self):
        self.assertDictEqual(self.result['previous'],
                             {u"%s" % self.parent.pk: None})

    def test_next(self):
        self.assertDictEqual(self.result['next'],
                             {u"%s" % self.parent.pk: self.sibling.pk})


class TrekPointsReferenceTest(TrekkingManagerTest):
    def setUp(self):
        self.login()

        self.trek = TrekFactory.create()
        self.trek.points_reference = MultiPoint([Point(0, 0), Point(1, 1)], srid=settings.SRID)
        self.trek.save()

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
    def setUp(self):
        # Create a simple fake DEM
        conn = connections[DEFAULT_DB_ALIAS]
        cur = conn.cursor()
        cur.execute('CREATE TABLE mnt (rid serial primary key, rast raster)')
        cur.execute('INSERT INTO mnt (rast) VALUES (ST_MakeEmptyRaster(10, 10, 700040, 6600040, 10, 10, 0, 0, %s))',
                    [settings.SRID])
        cur.execute('UPDATE mnt SET rast = ST_AddBand(rast, \'16BSI\')')
        for y in range(0, 1):
            for x in range(0, 1):
                cur.execute('UPDATE mnt SET rast = ST_SetValue(rast, %s, %s, %s::float)', [x + 1, y + 1, 42])

        self.login()

        self.trek = TrekWithPOIsFactory.create()
        self.trek.description_en = 'Nice trek'
        self.trek.description_it = 'Bonnito iti'
        self.trek.description_fr = 'Jolie rando'
        self.trek.save()

        for poi in self.trek.pois.all():
            poi.description_it = poi.description
            poi.published_it = True
            poi.save()

        url = '/api/it/treks/{pk}/slug.gpx'.format(pk=self.trek.pk)
        self.response = self.client.get(url)
        self.parsed = BeautifulSoup(self.response.content)

    def tearDown(self):
        translation.deactivate()

    def test_gpx_is_served_with_content_type(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response['Content-Type'], 'application/gpx+xml')

    def test_gpx_trek_as_track_points(self):
        self.assertEqual(len(self.parsed.findAll('trk')), 1)
        self.assertEqual(len(self.parsed.findAll('trkpt')), 2)

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
        self.assertEqual(name, u"%s: %s" % (pois[0].type, pois[0].name))
        self.assertEqual(description, pois[0].description)
        self.assertEqual(waypoint['lat'], '46.5003601787')
        self.assertEqual(waypoint['lon'], '3.00052158552')
        self.assertEqual(elevation, '42.0')


class TrekViewTranslationTest(TrekkingManagerTest):
    def setUp(self):
        self.trek = TrekFactory.create()
        self.trek.name_fr = 'Voie lactee'
        self.trek.name_en = 'Milky way'
        self.trek.name_it = 'Via Lattea'

        self.trek.published_fr = True
        self.trek.published_it = False
        self.trek.save()

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
                obj = json.loads(response.content)
                self.assertEqual(obj['name'], expected)

    def test_geojson_translation(self):
        url = '/api/trek/trek.geojson'

        for lang, expected in [('fr', self.trek.name_fr),
                               ('it', self.trek.name_it)]:
            self.login()
            response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang)
            self.assertEqual(response.status_code, 200)
            obj = json.loads(response.content)
            self.assertEqual(obj['features'][0]['properties']['name'], expected)
            self.client.logout()  # Django 1.6 keeps language in session

    def test_published_translation(self):
        url = '/api/trek/trek.geojson'

        for lang, expected in [('fr', self.trek.published_fr),
                               ('it', self.trek.published_it)]:
            self.login()
            response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang)
            self.assertEqual(response.status_code, 200)
            obj = json.loads(response.content)
            self.assertEqual(obj['features'][0]['properties']['published'], expected)
            self.client.logout()  # Django 1.6 keeps language in session

    def test_poi_geojson_translation(self):
        # Create a Trek with a POI
        trek = TrekFactory.create(no_path=True, published_fr=True, published_it=True)
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        poi = POIFactory.create(no_path=True)
        poi.name_fr = "Chapelle"
        poi.name_en = "Chapel"
        poi.name_it = "Capela"
        poi.published_fr = True
        poi.published_en = True
        poi.published_it = True
        poi.save()
        trek.add_path(p1, start=0.5)
        poi.add_path(p1, start=0.6, end=0.6)
        # Check that it applies to GeoJSON also :
        self.assertEqual(len(trek.pois), 1)
        poi = trek.pois[0]
        for lang, expected in [('fr', poi.name_fr),
                               ('it', poi.name_it)]:
            url = '/api/{lang}/treks/{pk}/pois.geojson'.format(lang=lang, pk=trek.pk)
            self.login()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            obj = json.loads(response.content)
            jsonpoi = obj.get('features', [])[0]
            self.assertEqual(jsonpoi.get('properties', {}).get('name'), expected)
            self.client.logout()  # Django 1.6 keeps language in session


class TemplateTagsTest(TestCase):
    def test_duration(self):
        self.assertEqual(u"15 min", trekking_tags.duration(0.25))
        self.assertEqual(u"30 min", trekking_tags.duration(0.5))
        self.assertEqual(u"1 h", trekking_tags.duration(1))
        self.assertEqual(u"1 h 45", trekking_tags.duration(1.75))
        self.assertEqual(u"3 h 30", trekking_tags.duration(3.5))
        self.assertEqual(u"4 h", trekking_tags.duration(4))
        self.assertEqual(u"6 h", trekking_tags.duration(6))
        self.assertEqual(u"10 h", trekking_tags.duration(10))
        self.assertEqual(u"1 days", trekking_tags.duration(24))
        self.assertEqual(u"2 days", trekking_tags.duration(32))
        self.assertEqual(u"2 days", trekking_tags.duration(48))
        self.assertEqual(u"3 days", trekking_tags.duration(49))
        self.assertEqual(u"8 days", trekking_tags.duration(24 * 8))
        self.assertEqual(u"9 days", trekking_tags.duration(24 * 9))


class TrekViewsSameStructureTests(AuthentFixturesTest):
    def setUp(self):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh',
                                            language='en')
        self.user = profile.user
        self.user.groups.add(Group.objects.get(name=u"Référents communication"))
        self.client.login(username='homer', password='dooh')
        self.content1 = TrekFactory.create()
        structure = StructureFactory.create()
        self.content2 = TrekFactory.create(structure=structure)

    def add_bypass_perm(self):
        perm = Permission.objects.get(codename='can_bypass_structure')
        self.user.user_permissions.add(perm)

    def test_edit_button_same_structure(self):
        url = "/trek/{pk}/".format(pk=self.content1.pk)
        response = self.client.get(url)
        self.assertContains(response,
                            '<a class="btn btn-primary pull-right" '
                            'href="/trek/edit/{pk}/">'
                            '<i class="icon-pencil icon-white"></i> '
                            'Update</a>'.format(pk=self.content1.pk))

    def test_edit_button_other_structure(self):
        url = "/trek/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertContains(response,
                            '<span class="btn disabled pull-right" href="#">'
                            '<i class="icon-pencil"></i> Update</span>')

    def test_edit_button_bypass_structure(self):
        self.add_bypass_perm()
        url = "/trek/{pk}/".format(pk=self.content2.pk)
        response = self.client.get(url)
        self.assertContains(response,
                            '<a class="btn btn-primary pull-right" '
                            'href="/trek/edit/{pk}/">'
                            '<i class="icon-pencil icon-white"></i> '
                            'Update</a>'.format(pk=self.content2.pk))

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
    def setUp(self):
        profile = UserProfileFactory.create(user__username='homer',
                                            user__password='dooh')
        user = profile.user
        user.groups.add(Group.objects.get(name=u"Référents communication"))
        self.client.login(username=user.username, password='dooh')
        self.content1 = POIFactory.create()
        structure = StructureFactory.create()
        self.content2 = POIFactory.create(structure=structure)

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


class CirkwiTests(TranslationResetMixin, TestCase):
    def setUp(self):
        testutil._MAX_LENGTH = 10000
        creation = make_aware(datetime.datetime(2014, 1, 1), utc)
        self.trek = TrekFactory.create(published=True)
        self.trek.date_insert = creation
        self.trek.save()
        self.poi = POIFactory.create(published=True)
        self.poi.date_insert = creation
        self.poi.save()
        TrekFactory.create(published=False)
        POIFactory.create(published=False)

    def tearDown(self):
        testutil._MAX_LENGTH = 80

    def test_export_circuits(self):
        response = self.client.get('/api/cirkwi/circuits.xml')
        self.assertEqual(response.status_code, 200)
        attrs = {
            'pk': self.trek.pk,
            'title': self.trek.name,
            'date_update': timestamp(self.trek.date_update),
            'n': self.trek.description.replace('<p>description ', '').replace('</p>', ''),
            'poi_pk': self.poi.pk,
            'poi_title': self.poi.name,
            'poi_date_update': timestamp(self.poi.date_update),
            'poi_description': self.poi.description.replace('<p>', '').replace('</p>', ''),
        }
        self.assertXMLEqual(
            response.content,
            '<?xml version="1.0" encoding="utf8"?>\n'
            '<circuits version="2">'
            '<circuit id_circuit="{pk}" date_modification="{date_update}" date_creation="1388534400">'
            '<informations>'
            '<information langue="en">'
            '<titre>{title}</titre>'
            '<description>description_teaser {n}\n\ndescription {n}</description>'
            '<informations_complementaires>'
            '<information_complementaire><titre>Departure</titre><description>departure {n}</description></information_complementaire>'
            '<information_complementaire><titre>Arrival</titre><description>arrival {n}</description></information_complementaire>'
            '<information_complementaire><titre>Ambiance</titre><description>ambiance {n}</description></information_complementaire>'
            '<information_complementaire><titre>Access</titre><description>access {n}</description></information_complementaire>'
            '<information_complementaire><titre>Disabled infrastructure</titre><description>disabled_infrastructure {n}</description></information_complementaire>'
            '<information_complementaire><titre>Advised parking</titre><description>Advised parking {n}</description></information_complementaire>'
            '<information_complementaire><titre>Public transport</titre><description>Public transport {n}</description></information_complementaire>'
            '<information_complementaire><titre>Advice</titre><description>Advice {n}</description></information_complementaire></informations_complementaires>'
            '</information>'
            '</informations>'
            '<distance>141</distance>'
            '<locomotions><locomotion duree="5400"></locomotion></locomotions>'
            '<fichier_trace url="http://testserver/api/en/treks/{pk}/name-{n}.kml"/>'
            '<pois>'
            '<poi id_poi="{poi_pk}" date_modification="{poi_date_update}" date_creation="1388534400">'
            '<informations>'
            '<information langue="en"><titre>{poi_title}</titre><description>{poi_description}</description></information>'
            '</informations>'
            '<adresse><position><lat>46.5</lat><lng>3.0</lng></position></adresse>'
            '</poi>'
            '</pois>'
            '</circuit>'
            '</circuits>'.format(**attrs))

    def test_export_pois(self):
        response = self.client.get('/api/cirkwi/pois.xml')
        self.assertEqual(response.status_code, 200)
        attrs = {
            'pk': self.poi.pk,
            'title': self.poi.name,
            'description': self.poi.description.replace('<p>', '').replace('</p>', ''),
            'date_update': timestamp(self.poi.date_update),
        }
        self.assertXMLEqual(
            response.content,
            '<?xml version="1.0" encoding="utf8"?>\n'
            '<pois version="2">'
            '<poi id_poi="{pk}" date_modification="{date_update}" date_creation="1388534400">'
            '<informations>'
            '<information langue="en"><titre>{title}</titre><description>{description}</description></information>'
            '</informations>'
            '<adresse><position><lat>46.5</lat><lng>3.0</lng></position></adresse>'
            '</poi>'
            '</pois>'.format(**attrs))


class TrekWorkflowTest(TranslationResetMixin, TestCase):
    def setUp(self):
        call_command('update_geotrek_permissions')
        self.trek = TrekFactory.create(published=False)
        self.user = User.objects.create_user('omer', password='booh')
        self.user.user_permissions.add(Permission.objects.get(codename='add_trek'))
        self.user.user_permissions.add(Permission.objects.get(codename='change_trek'))
        self.client.login(username='omer', password='booh')

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


class SyncRandoViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('bart', password='mahaha')

    def test_return_redirect(self):
        response = self.client.get(reverse('trekking:sync_randos_view'))
        self.assertEqual(response.status_code, 302)

    def test_return_redirect_superuser(self):
        self.user.is_superuser = True
        response = self.client.get(reverse('trekking:sync_randos_view'))
        self.assertEqual(response.status_code, 302)

    def test_post_sync_redirect(self):
        """
        test if sync can be launched by superuser post
        """
        self.user.is_superuser = True
        response = self.client.post(reverse('trekking:sync_randos'))
        self.assertEqual(response.status_code, 302)


class ServiceViewsTest(CommonTest):
    model = Service
    modelfactory = ServiceFactory
    userfactory = TrekkingManagerFactory

    def get_good_data(self):
        PathFactory.create()
        return {
            'type': ServiceTypeFactory.create().pk,
            'topology': '{"lat": 5.1, "lng": 6.6}',
            'structure': default_structure().pk
        }

    def test_empty_topology(self):
        self.login()
        data = self.get_good_data()
        data['topology'] = ''
        response = self.client.post(self.model.get_add_url(), data)
        self.assertEqual(response.status_code, 200)
        form = self.get_form(response)
        self.assertEqual(form.errors, {'topology': [u'Topology is empty.']})

    def test_listing_number_queries(self):
        self.login()
        # Create many instances
        for i in range(100):
            self.modelfactory.create()
        for i in range(10):
            DistrictFactory.create()

        # Enable query counting
        settings.DEBUG = True

        for url in [self.model.get_jsonlist_url(),
                    self.model.get_format_list_url()]:
            with self.assertNumQueries(5):
                self.client.get(url)

        settings.DEBUG = False


class ServiceJSONTest(TrekkingManagerTest):
    def setUp(self):
        self.login()
        self.service = ServiceFactory.create(type__published=True)
        self.pk = self.service.pk

    def test_list(self):
        url = '/api/en/services.json'
        self.response = self.client.get(url)
        self.result = json.loads(self.response.content)
        self.assertEqual(len(self.result), 1)
        self.assertTrue('type' in self.result[0])

    def test_detail(self):
        url = '/api/en/services/%s.json' % self.pk
        self.response = self.client.get(url)
        self.result = json.loads(self.response.content)
        self.assertDictEqual(self.result['type'],
                             {'id': self.service.type.pk,
                              'name': self.service.type.name,
                              'pictogram': os.path.join(settings.MEDIA_URL, self.service.type.pictogram.name),
                              })
