from django.test import TestCase
from django.contrib.gis.geos import LineString, Polygon, MultiPolygon
from django.utils import simplejson
from django.core.urlresolvers import reverse
from caminae.mapentity.tests import MapEntityTest
from caminae.authent.factories import TrekkingManagerFactory

from caminae.core.factories import PathFactory, PathAggregationFactory
from caminae.land.factories import DistrictFactory
from caminae.trekking.models import POI, Trek
from caminae.trekking.factories import (POIFactory, POITypeFactory, TrekFactory,
    TrekNetworkFactory, UsageFactory, WebLinkFactory, ThemeFactory)


class POIViewsTest(MapEntityTest):
    model = POI
    modelfactory = POIFactory
    userfactory = TrekkingManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'name_fr': 'test',
            'name_en': 'test',
            'name_it': 'testo',
            'description_fr': 'ici',
            'description_en': 'here',
            'description_it': 'aca',
            'type': POITypeFactory.create().pk,
            'topology': '{"paths": [%s], "offset": 18.4}' % path.pk,
        }


class TrekViewsTest(MapEntityTest):
    model = Trek
    modelfactory = TrekFactory
    userfactory = TrekkingManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'name_fr': 'Hoho',
            'name_it': '',
            'name_en': '',
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
            'parking_location': 'POINT (1.0 1.0 0.0)',
            'public_transport': 'huhu',
            'advice_fr': '',
            'advice_it': '',
            'advice_en': '',
            'themes': ThemeFactory.create().pk,
            'networks': TrekNetworkFactory.create().pk,
            'usages': UsageFactory.create().pk,
            'web_links': WebLinkFactory.create().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def test_badfield_goodgeom(self):
        self.login()
        
        bad_data, form_error = self.get_bad_data()
        bad_data['parking_location'] = 'POINT (1.0 1.0 0.0)'
        url = self.model.get_add_url()
        response = self.client.post(url, bad_data)
        self.assertEqual(response.status_code, 200)
        form = self.get_form(response)
        self.assertEqual(form.data['parking_location'], bad_data['parking_location'])


class TrekCustomViewTests(TestCase):

    def test_pois_geojson(self):
        trek = TrekFactory.create()
        url = reverse('trekking:trek_poi_geojson', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_gpx(self):
        trek = TrekFactory.create()
        url = reverse('trekking:trek_gpx_detail', kwargs={'pk': trek.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

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
        obj = simplejson.loads(response.content)
        self.assertEqual(obj['name'], trek.name)

        # Test with another language
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='it-IT')
        obj = simplejson.loads(response.content)
        self.assertEqual(obj['name'], trek.name_it)

        # Test with yet another language
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='fr-FR')
        obj = simplejson.loads(response.content)
        self.assertEqual(obj['name'], trek.name_fr)

    def test_geojson_translation(self):
        trek = TrekFactory.create(name='Voie lactee')
        trek.name_it = 'Via Lattea'
        trek.save()
        url = reverse('trekking:trek_layer')
        # Test with another language
        response = self.client.get(url, HTTP_ACCEPT_LANGUAGE='it-IT')
        obj = simplejson.loads(response.content)
        self.assertEqual(obj['features'][0]['properties']['name'], trek.name_it)

    def test_poi_geojson_translation(self):
        # Create a Trek with a POI
        trek = TrekFactory.create(no_path=True)
        p1 = PathFactory.create(geom=LineString((0,0,0), (4,4,2)))
        poi = POIFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=trek, path=p1,
                                      start_position=0.5)
        PathAggregationFactory.create(topo_object=poi, path=p1,
                                      start_position=0.6, end_position=0.6)
        # Check that it applies to GeoJSON also :
        self.assertEqual(len(trek.pois), 1)
        poi = trek.pois[0]
        for lang, expected in [('fr-FR', poi.name_fr), ('it-IT', poi.name_it)]:
            url = reverse('trekking:trek_poi_geojson', kwargs={'pk': trek.pk})
            response = self.client.get(url, HTTP_ACCEPT_LANGUAGE=lang)
            obj = simplejson.loads(response.content)
            jsonpoi = obj.get('features', [])[0]
            self.assertEqual(jsonpoi.get('properties', {}).get('label'), expected)


class RelatedObjectsTest(TestCase):
    def test_elevation(self):
        trek = TrekFactory.create(no_path=True)
        p1 = PathFactory.create(geom=LineString((1,0,1), (0,0,1), (0,1,1)))
        p2 = PathFactory.create(geom=LineString((0,1,1), (1,1,1), (1,2,2)))
        PathAggregationFactory.create(topo_object=trek, path=p1,
                                      start_position=0.5)
        PathAggregationFactory.create(topo_object=trek, path=p2)

        trek = Trek.objects.get(pk=trek.pk) # reload to get computed fields

        actual_profile = trek.elevation_profile
        expected_profile = ((0,1), (1,1), (2,1), (2+2**0.5,2),)
        self.assertItemsEqual(actual_profile, expected_profile)

    def test_helpers(self):
        trek = TrekFactory.create(no_path=True)
        p1 = PathFactory.create(geom=LineString((0,0,0), (4,4,2)))
        p2 = PathFactory.create(geom=LineString((4,4,2), (8,8,4)))
        poi = POIFactory.create(no_path=True)
        PathAggregationFactory.create(topo_object=trek, path=p1,
                                      start_position=0.5)
        PathAggregationFactory.create(topo_object=trek, path=p2)
        PathAggregationFactory.create(topo_object=poi, path=p1,
                                      start_position=0.6, end_position=0.6)
        # /!\ District are automatically linked to paths at DB level
        d1 = DistrictFactory.create(geom=MultiPolygon(
            Polygon(((-2,-2), (3,-2), (3,3), (-2,3), (-2,-2)))))

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
            Polygon(((3,3), (9,3), (9,9), (3,9), (3,3)))))
        self.assertItemsEqual(trek.districts, [d1, d2])
