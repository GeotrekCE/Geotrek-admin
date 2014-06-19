#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
from collections import OrderedDict

import mock
from bs4 import BeautifulSoup

from django.conf import settings
from django.test import TestCase
from django.contrib.gis.geos import LineString
from django.core.urlresolvers import reverse
from django.db import connection
from django.template.loader import find_template

from mapentity.tests import MapEntityLiveTest
from mapentity.factories import SuperUserFactory

from geotrek.common.factories import AttachmentFactory
from geotrek.common.tests import CommonTest
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_document
from geotrek.authent.factories import TrekkingManagerFactory
from geotrek.core.factories import PathFactory
from geotrek.zoning.factories import DistrictFactory
from geotrek.trekking.models import POI, Trek
from geotrek.trekking.factories import (POIFactory, POITypeFactory, TrekFactory, TrekWithPOIsFactory,
                                        TrekNetworkFactory, UsageFactory, WebLinkFactory,
                                        ThemeFactory, InformationDeskFactory)
from geotrek.trekking.templatetags import trekking_tags

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
            'topology': '{"lat": 5.1, "lng": 6.6}'
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
            'usages': UsageFactory.create().pk,
            'web_links': WebLinkFactory.create().pk,
            'information_desks': InformationDeskFactory.create().pk,
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
        self.modelfactory.create(name="ukélélé")   # trek with utf8
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
        trek = TrekWithPOIsFactory.create()
        self.assertEqual(len(trek.pois), 2)
        poi = trek.pois[0]
        AttachmentFactory.create(obj=poi, attachment_file=get_dummy_uploaded_image())
        self.assertNotEqual(poi.thumbnail, None)
        self.assertEqual(len(trek.pois), 2)

        url = reverse('trekking:trek_poi_geojson', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        poislayer = json.loads(response.content)
        poifeature = poislayer['features'][0]
        self.assertTrue('thumbnail' in poifeature['properties'])

    def test_kml(self):
        trek = TrekWithPOIsFactory.create()
        url = reverse('trekking:trek_kml_detail', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.google-earth.kml+xml')

    def test_json_detail(self):
        trek = TrekFactory.create()
        self.information_desk = InformationDeskFactory.create()
        trek.information_desks.add(self.information_desk)

        url = reverse('trekking:trek_json_detail', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        detailjson = json.loads(response.content)
        self.assertDictEqual(detailjson['route'],
                             {"id": trek.route.id,
                              "label": trek.route.route})
        self.assertDictEqual(detailjson['difficulty'],
                             {"id": trek.difficulty.id,
                              "pictogram": os.path.join(settings.MEDIA_URL, trek.difficulty.pictogram.name),
                              "label": trek.difficulty.difficulty})
        self.assertDictEqual(detailjson['information_desk'],
                             detailjson['information_desks'][0])
        self.assertDictEqual(detailjson['information_desks'][0],
                             {u'description': u'<p>description 0</p>',
                              u'email': u'email-0@makina-corpus.com',
                              u'latitude': -5.983593666147552,
                              u'longitude': -1.3630761286186646,
                              u'name': u'information desk name 0',
                              u'phone': u'01 02 03 0',
                              u'photo': self.information_desk.photo_url,
                              u'postal_code': 28300,
                              u'street': u'0 baker street',
                              u'municipality': u"Bailleau L'évêque-0",
                              u'website': u'http://makina-corpus.com/0'})
        self.assertEqual(detailjson['information_desk_layer'],
                         '/api/trek/%s/information_desks.geojson' % trek.pk)
        self.assertEqual(detailjson['filelist_url'],
                         '/paperclip/get/trekking/trek/%s/' % trek.pk)

    def test_json_detail_has_elevation_area_url(self):
        trek = TrekFactory.create()
        url = reverse('trekking:trek_json_detail', kwargs={'pk': trek.pk})
        detailjson = json.loads((self.client.get(url)).content)
        self.assertEqual(detailjson['elevation_area_url'], '/api/trek/%s/dem.json' % trek.pk)

    @mock.patch('mapentity.models.MapEntityMixin.get_attributes_html')
    def test_overriden_document(self, get_attributes_html):
        trek = TrekFactory.create()

        get_attributes_html.return_value = '<p>mock</p>'
        with open(trek.get_map_image_path(), 'w') as f:
            f.write('***' * 1000)
        with open(trek.get_elevation_chart_path(), 'w') as f:
            f.write('***' * 1000)

        response = self.client.get(trek.get_document_public_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) > 1000)

        AttachmentFactory.create(obj=trek, title="docprint", attachment_file=get_dummy_uploaded_document(size=100))
        response = self.client.get(trek.get_document_public_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) < 1000)

    @mock.patch('django.template.loaders.filesystem.open', create=True)
    def test_overriden_public_template(self, open_patched):
        overriden_template = os.path.join(settings.MEDIA_ROOT, 'templates', 'trekking', 'trek_public.odt')
        def fake_exists(f, *args):
            if f == overriden_template:
                return mock.MagicMock(spec=file)
            raise IOError
        open_patched.side_effect = fake_exists
        find_template('trekking/trek_public.odt')
        open_patched.assert_called_with(overriden_template, 'rb')

    def test_profile_json(self):
        trek = TrekFactory.create()
        url = reverse('trekking:trek_profile', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_elevation_area_json(self):
        trek = TrekFactory.create()
        url = reverse('trekking:trek_elevation_area', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_profile_svg(self):
        trek = TrekFactory.create()
        url = reverse('trekking:trek_profile_svg', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/svg+xml')

    def test_weblink_popup(self):
        url = reverse('trekking:weblink_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class TrekGPXTest(TrekkingManagerTest):

    def setUp(self):
        self.login()

        self.trek = TrekWithPOIsFactory.create()
        self.trek.description_en = 'Nice trek'
        self.trek.description_it = 'Bonnito iti'
        self.trek.description_fr = 'Jolie rando'
        self.trek.save()

        for poi in self.trek.pois.all():
            poi.description_it = poi.description
            poi.save()

        url = reverse('trekking:trek_gpx_detail', kwargs={'pk': self.trek.pk})
        self.response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='it-IT')
        self.parsed = BeautifulSoup(self.response.content)

    def test_gpx_is_served_with_content_type(self):
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(self.response['Content-Type'], 'application/gpx+xml')

    def test_gpx_trek_as_route_points(self):
        self.assertEqual(len(self.parsed.findAll('rte')), 1)
        self.assertEqual(len(self.parsed.findAll('rtept')), 2)

    def test_gpx_translated_using_accept_language(self):
        route = self.parsed.findAll('rte')[0]
        description = route.find('desc').string
        self.assertTrue(description.startswith(self.trek.description_it))

    def test_gpx_contains_pois(self):
        waypoints = self.parsed.findAll('wpt')
        pois = self.trek.pois.all()
        self.assertEqual(len(waypoints), len(pois))
        waypoint = waypoints[0]
        name = waypoint.find('name').string
        description = waypoint.find('desc').string
        self.assertEqual(name, u"%s: %s" % (pois[0].type, pois[0].name))
        self.assertEqual(description, pois[0].description)


class TrekViewTranslationTest(TrekkingManagerTest):
    def setUp(self):
        self.trek = TrekFactory.build()
        self.trek.name_fr = 'Voie lactee'
        self.trek.name_en = 'Milky way'
        self.trek.name_it = 'Via Lattea'

        self.trek.published_fr = True
        self.trek.published_it = False
        self.trek.save()

    def tearDown(self):
        self.client.logout()

    def test_json_translation(self):
        url = reverse('trekking:trek_json_detail', kwargs={'pk': self.trek.pk})

        for lang, expected in [('fr-FR', self.trek.name_fr),
                               ('it-IT', self.trek.name_it)]:
            self.login()
            response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang)
            self.assertEqual(response.status_code, 200)
            obj = json.loads(response.content)
            self.assertEqual(obj['name'], expected)
            self.client.logout()  # Django 1.6 keeps language in session

    def test_geojson_translation(self):
        url = reverse('trekking:trek_layer')

        for lang, expected in [('fr-FR', self.trek.name_fr),
                               ('it-IT', self.trek.name_it)]:
            self.login()
            response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang)
            self.assertEqual(response.status_code, 200)
            obj = json.loads(response.content)
            self.assertEqual(obj['features'][0]['properties']['name'], expected)
            self.client.logout()  # Django 1.6 keeps language in session

    def test_published_translation(self):
        url = reverse('trekking:trek_layer')

        for lang, expected in [('fr-FR', self.trek.published_fr),
                               ('it-IT', self.trek.published_it)]:
            self.login()
            response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang)
            self.assertEqual(response.status_code, 200)
            obj = json.loads(response.content)
            self.assertEqual(obj['features'][0]['properties']['published'], expected)
            self.client.logout()  # Django 1.6 keeps language in session

    def test_poi_geojson_translation(self):
        # Create a Trek with a POI
        trek = TrekFactory.create(no_path=True)
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        poi = POIFactory.create(no_path=True)
        poi.name_fr = "Chapelle"
        poi.name_en = "Chapel"
        poi.name_it = "Capela"
        poi.save()
        trek.add_path(p1, start=0.5)
        poi.add_path(p1, start=0.6, end=0.6)
        # Check that it applies to GeoJSON also :
        self.assertEqual(len(trek.pois), 1)
        poi = trek.pois[0]
        for lang, expected in [('fr-FR', poi.name_fr),
                               ('it-IT', poi.name_it)]:
            url = reverse('trekking:trek_poi_geojson', kwargs={'pk': trek.pk})
            self.login()
            response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang)
            self.assertEqual(response.status_code, 200)
            obj = json.loads(response.content)
            jsonpoi = obj.get('features', [])[0]
            self.assertEqual(jsonpoi.get('properties', {}).get('name'), expected)
            self.client.logout() # Django 1.6 keeps language in session


class TrekInformationDeskGeoJSONTest(TrekkingManagerTest):

    def setUp(self):
        self.trek = TrekFactory.create()
        self.information_desk1 = InformationDeskFactory.create()
        self.information_desk2 = InformationDeskFactory.create(photo=None)
        self.information_desk3 = InformationDeskFactory.create()
        self.trek.information_desks.add(self.information_desk1)
        self.trek.information_desks.add(self.information_desk2)
        self.url = reverse('trekking:trek_information_desk_geojson', kwargs={'pk': self.trek.pk})

    def test_trek_layer_is_login_required(self):
        self.client.logout()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)

    def test_information_desks_layer_contains_only_trek_records(self):
        self.login()
        resp = self.client.get(self.url)
        dataset = json.loads(resp.content)
        self.assertEqual(len(dataset['features']), 2)

    def test_information_desk_layer_has_null_if_no_photo(self):
        self.login()
        resp = self.client.get(self.url)
        dataset = json.loads(resp.content)
        second = dataset['features'][1]
        self.assertEqual(second['properties']['photo_url'], None)

    def test_information_desk_layer_gives_all_model_attributes(self):
        self.login()
        resp = self.client.get(self.url)
        dataset = json.loads(resp.content)
        first = dataset['features'][0]
        self.assertEqual(sorted(first['properties'].keys()),
                         ['description',
                          'email',
                          'id',
                          'latitude',
                          'longitude',
                          'model',
                          'municipality',
                          'name',
                          'phone',
                          'photo_url',
                          'postal_code',
                          'website'])


class TemplateTagsTest(TestCase):
    def test_duration(self):
        self.assertEqual(u"15 min", trekking_tags.duration(0.25))
        self.assertEqual(u"30 min", trekking_tags.duration(0.5))
        self.assertEqual(u"1H", trekking_tags.duration(1))
        self.assertEqual(u"1H45", trekking_tags.duration(1.75))
        self.assertEqual(u"3H30", trekking_tags.duration(3.5))
        self.assertEqual(u"4H", trekking_tags.duration(4))
        self.assertEqual(u"6H", trekking_tags.duration(6))
        self.assertEqual(u"10H", trekking_tags.duration(10))
        self.assertEqual(u"2 days", trekking_tags.duration(11))
        self.assertEqual(u"2 days", trekking_tags.duration(48))
        self.assertEqual(u"More than 8 days", trekking_tags.duration(24*8))
        self.assertEqual(u"More than 8 days", trekking_tags.duration(24*9))
