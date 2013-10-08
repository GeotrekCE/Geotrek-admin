#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.test import TestCase

from django.contrib.gis.geos import LineString, Polygon, MultiPolygon, MultiLineString
import json
from django.core.urlresolvers import reverse
from django.db import connection

from mapentity.tests import MapEntityLiveTest

from geotrek.common.factories import AttachmentFactory
from geotrek.common.tests import CommonTest
from geotrek.common.utils.testdata import get_dummy_uploaded_image, get_dummy_uploaded_document
from geotrek.authent.factories import TrekkingManagerFactory
from geotrek.core.factories import PathFactory, PathAggregationFactory
from geotrek.land.factories import DistrictFactory
from geotrek.trekking.models import POI, Trek
from geotrek.trekking.factories import (POIFactory, POITypeFactory, TrekFactory,
                                        TrekNetworkFactory, UsageFactory, WebLinkFactory,
                                        ThemeFactory, InformationDeskFactory)

from ..templatetags import trekking_tags


class TrekTest(TestCase):
    def test_is_publishable(self):
        t = TrekFactory.create()
        t.geom = LineString((0, 0), (1, 1))
        self.assertTrue(t.has_geom_valid())

        t.description_teaser = ''
        self.assertFalse(t.is_complete())
        self.assertFalse(t.is_publishable())
        t.description_teaser = 'ba'
        t.departure = 'zin'
        t.arrival = 'ga'
        self.assertTrue(t.is_complete())
        self.assertTrue(t.is_publishable())

        t.geom = MultiLineString([LineString((0, 0), (1, 1)), LineString((2, 2), (3, 3))])
        self.assertFalse(t.has_geom_valid())
        self.assertFalse(t.is_publishable())


class POIViewsTest(CommonTest):
    model = POI
    modelfactory = POIFactory
    userfactory = TrekkingManagerFactory

    def get_good_data(self):
        PathFactory.create()
        return {
            'name_fr': 'test',
            'name_en': 'test',
            'name_it': 'testo',
            'description_fr': 'ici',
            'description_en': 'here',
            'description_it': 'aca',
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

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'name_fr': 'Huhu',
            'name_it': 'Hoho',
            'name_en': 'Hehe',
            'departure_fr': '',
            'departure_it': '',
            'departure_en': '',
            'arrival_fr': '',
            'arrival_en': '',
            'arrival_it': '',
            'published': '',
            'difficulty': '',
            'route': '',
            'description_teaser_fr': '',
            'description_teaser_it': '',
            'description_teaser_en': '',
            'description_fr': '',
            'description_it': '',
            'description_en': '',
            'ambiance_fr': '',
            'ambiance_it': '',
            'ambiance_en': '',
            'access_fr': '',
            'access_it': '',
            'access_en': '',
            'disabled_infrastructure_fr': '',
            'disabled_infrastructure_it': '',
            'disabled_infrastructure_en': '',
            'duration': '0',
            'is_park_centered': '',
            'advised_parking': 'Very close',
            'parking_location': 'POINT (1.0 1.0)',
            'public_transport': 'huhu',
            'advice_fr': '',
            'advice_it': '',
            'advice_en': '',
            'themes': ThemeFactory.create().pk,
            'networks': TrekNetworkFactory.create().pk,
            'usages': UsageFactory.create().pk,
            'web_links': WebLinkFactory.create().pk,
            'information_desk': InformationDeskFactory.create().pk,
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
    userfactory = TrekkingManagerFactory


class TrekCustomViewTests(TestCase):

    def test_pois_geojson(self):
        trek = TrekFactory.create(no_path=True)
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        poi = POIFactory(no_path=True)
        trek.add_path(p1, start=0.5, end=1.0)
        poi.add_path(p1, start=0.6, end=0.6)
        AttachmentFactory.create(obj=poi, attachment_file=get_dummy_uploaded_image())
        self.assertNotEqual(poi.thumbnail, None)
        self.assertEqual(len(trek.pois), 1)

        url = reverse('trekking:trek_poi_geojson', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        poislayer = json.loads(response.content)
        poifeature = poislayer['features'][0]
        self.assertTrue('serializable_thumbnail' in poifeature['properties'])

    def test_gpx(self):
        trek = TrekFactory.create()
        trek = TrekFactory.create()
        url = reverse('trekking:trek_gpx_detail', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.count('<rte>'), 1)
        self.assertTrue(response.content.count('<rtept') >= 2)

    def test_kml(self):
        trek = TrekFactory.create()
        url = reverse('trekking:trek_kml_detail', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_json_translation(self):
        trek = TrekFactory.build()
        trek.name_fr = 'Voie lactee'
        trek.name_en = 'Milky way'
        trek.name_it = 'Via Lattea'
        trek.save()
        url = reverse('trekking:trek_json_detail', kwargs={'pk': trek.pk})

        # Test default case
        response = self.client.get(url)
        obj = json.loads(response.content)
        self.assertEqual(obj['name'], trek.name)

        # Test with another language
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='it-IT')
        obj = json.loads(response.content)
        self.assertEqual(obj['name'], trek.name_it)

        # Test with yet another language
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='fr-FR')
        obj = json.loads(response.content)
        self.assertEqual(obj['name'], trek.name_fr)

    def test_geojson_translation(self):
        trek = TrekFactory.create(name='Voie lactee')
        trek.name_it = 'Via Lattea'
        trek.save()
        url = reverse('trekking:trek_layer')
        # Test with another language
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='it-IT')
        obj = json.loads(response.content)
        self.assertEqual(obj['features'][0]['properties']['name'], trek.name_it)

    def test_poi_geojson_translation(self):
        # Create a Trek with a POI
        trek = TrekFactory.create(no_path=True)
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        poi = POIFactory.create(no_path=True)
        poi.name_fr = "Chapelle"
        poi.name_it = "Capela"
        poi.save()
        trek.add_path(p1, start=0.5)
        poi.add_path(p1, start=0.6, end=0.6)
        # Check that it applies to GeoJSON also :
        self.assertEqual(len(trek.pois), 1)
        poi = trek.pois[0]
        for lang, expected in [('fr-FR', poi.name_fr), ('it-IT', poi.name_it)]:
            url = reverse('trekking:trek_poi_geojson', kwargs={'pk': trek.pk})
            response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang)
            obj = json.loads(response.content)
            jsonpoi = obj.get('features', [])[0]
            self.assertEqual(jsonpoi.get('properties', {}).get('name'), expected)

    def test_overriden_document(self):
        trek = TrekFactory.create()
        # Will have to mock screenshot, though.
        with open(trek.get_map_image_path(), 'w') as f:
            f.write('***' * 1000)
        response = self.client.get(trek.get_document_public_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) > 1000)

        AttachmentFactory.create(obj=trek, title="docprint", attachment_file=get_dummy_uploaded_document(size=100))
        response = self.client.get(trek.get_document_public_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.content) < 1000)


class RelatedObjectsTest(TestCase):
    def test_helpers(self):
        trek = TrekFactory.create(no_path=True)
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        p2 = PathFactory.create(geom=LineString((4, 4), (8, 8)))
        poi = POIFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=trek, path=p1,
                                      start_position=0.5)
        PathAggregationFactory.create(topo_object=trek, path=p2)
        PathAggregationFactory.create(topo_object=poi, path=p1,
                                      start_position=0.6, end_position=0.6)
        # /!\ District are automatically linked to paths at DB level
        d1 = DistrictFactory.create(geom=MultiPolygon(
            Polygon(((-2, -2), (3, -2), (3, 3), (-2, 3), (-2, -2)))))

        # Ensure related objects are accessible
        self.assertItemsEqual(trek.pois, [poi])
        self.assertItemsEqual(poi.treks, [trek])
        self.assertItemsEqual(trek.districts, [d1])

        # Ensure there is no duplicates
        PathAggregationFactory.create(topo_object=trek, path=p1,
                                      end_position=0.5)
        self.assertItemsEqual(trek.pois, [poi])
        self.assertItemsEqual(poi.treks, [trek])

        d2 = DistrictFactory.create(geom=MultiPolygon(
            Polygon(((3, 3), (9, 3), (9, 9), (3, 9), (3, 3)))))
        self.assertItemsEqual(trek.districts, [d1, d2])

    def test_deleted_pois(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        trek = TrekFactory.create(no_path=True)
        trek.add_path(p1)
        poi = POIFactory.create(no_path=True)
        poi.add_path(p1, start=0.6, end=0.6)
        self.assertItemsEqual(trek.pois, [poi])
        poi.delete()
        self.assertItemsEqual(trek.pois, [])

    def test_picture(self):
        trek = TrekFactory.create()
        AttachmentFactory.create(obj=trek)
        self.assertEqual(len(trek.attachments), 1)
        self.assertEqual(trek.thumbnail, None)
        self.assertEqual(trek.pictures, [])

        AttachmentFactory.create(obj=trek, attachment_file=get_dummy_uploaded_image())
        self.assertEqual(len(trek.attachments), 2)
        self.assertEqual(len(trek.pictures), 1)
        self.assertNotEqual(trek.thumbnail, None)


class TemplateTagsTest(TestCase):
    def test_duration(self):
        self.assertEqual(u"15 min", trekking_tags.duration(0.25))
        self.assertEqual(u"30 min", trekking_tags.duration(0.5))
        self.assertEqual(u"1H", trekking_tags.duration(1))
        self.assertEqual(u"1H45", trekking_tags.duration(1.75))
        self.assertEqual(u"1 day", trekking_tags.duration(13))
        self.assertEqual(u"2 days", trekking_tags.duration(48))
        self.assertEqual(u"More than 8 days", trekking_tags.duration(24*8))
        self.assertEqual(u"More than 8 days", trekking_tags.duration(24*9))
