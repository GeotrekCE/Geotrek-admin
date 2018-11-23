# -*- coding: utf-8 -*-
import json
import re

import mock
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.gis.geos import LineString, Point
from django.test import TestCase
from django.conf import settings

from geotrek.authent.tests import AuthentFixturesTest
from geotrek.common.tests import CommonTest
from geotrek.common.utils import LTE
from geotrek.common.utils import almostequal

from geotrek.authent.factories import PathManagerFactory, StructureFactory

from geotrek.core.models import Path, Trail

from geotrek.trekking.factories import POIFactory, TrekFactory, ServiceFactory
from geotrek.infrastructure.factories import InfrastructureFactory, SignageFactory
from geotrek.maintenance.factories import InterventionFactory
from geotrek.core.factories import (PathFactory, StakeFactory, TrailFactory, ComfortFactory, TopologyFactory, PathAggregationFactory)


class PathViewsTest(CommonTest):
    model = Path
    modelfactory = PathFactory
    userfactory = PathManagerFactory

    def get_bad_data(self):
        return {'geom': '{"geom": "LINESTRING (0.0 0.0, 1.0 1.0)"}'}, _("Linestring invalid snapping.")

    def get_good_data(self):
        return {
            'name': '',
            'stake': '',
            'comfort': ComfortFactory.create().pk,
            'trail': '',
            'comments': '',
            'departure': '',
            'arrival': '',
            'source': '',
            'valid': 'on',
            'geom': '{"geom": "LINESTRING (99.0 89.0, 100.0 88.0)", "snap": [null, null]}',
        }

    def _post_add_form(self):
        # Avoid overlap, delete all !
        for p in Path.objects.all():
            p.delete()
        super(PathViewsTest, self)._post_add_form()

    def test_structurerelated_filter(self):
        def test_structure(structure, stake):
            user = self.userfactory(password='booh')
            p = user.profile
            p.structure = structure
            p.save()
            success = self.client.login(username=user.username, password='booh')
            self.assertTrue(success)
            response = self.client.get(Path.get_add_url())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('form' in response.context)
            form = response.context['form']
            self.assertTrue('stake' in form.fields)
            stakefield = form.fields['stake']
            self.assertTrue((stake.pk, str(stake)) in stakefield.choices)
            self.client.logout()
        # Test for two structures
        s1 = StructureFactory.create()
        s2 = StructureFactory.create()
        st1 = StakeFactory.create(structure=s1)
        StakeFactory.create(structure=s1)
        st2 = StakeFactory.create(structure=s2)
        StakeFactory.create(structure=s2)
        test_structure(s1, st1)
        test_structure(s2, st2)

    def test_structurerelated_filter_with_none(self):
        s1 = StructureFactory.create()
        s2 = StructureFactory.create()
        st0 = StakeFactory.create(structure=None)
        st1 = StakeFactory.create(structure=s1)
        st2 = StakeFactory.create(structure=s2)
        user = self.userfactory(password='booh')
        p = user.profile
        p.structure = s1
        p.save()
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)
        response = self.client.get(Path.get_add_url())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('form' in response.context)
        form = response.context['form']
        self.assertTrue('stake' in form.fields)
        stakefield = form.fields['stake']
        self.assertTrue((st0.pk, str(st0)) in stakefield.choices)
        self.assertTrue((st1.pk, str(st1)) in stakefield.choices)
        self.assertFalse((st2.pk, str(st2)) in stakefield.choices)

    def test_basic_format(self):
        self.modelfactory.create()
        self.modelfactory.create(name="ãéè")
        super(CommonTest, self).test_basic_format()

    def test_path_form_is_not_valid_if_no_geometry_provided(self):
        self.login()
        data = self.get_good_data()
        data['geom'] = ''
        response = self.client.post(Path.get_add_url(), data)
        self.assertEqual(response.status_code, 200)

    def test_manager_can_delete(self):
        self.login()
        path = PathFactory()
        response = self.client.get(path.get_detail_url())
        self.assertEqual(response.status_code, 200)
        response = self.client.post(path.get_delete_url())
        self.assertEqual(response.status_code, 302)

    def test_delete_show_topologies(self):
        self.login()
        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        poi = POIFactory.create(name='POI', no_path=True)
        poi.add_path(path, start=0.5, end=0.5)
        trail = TrailFactory.create(name='Trail', no_path=True)
        trail.add_path(path, start=0.1, end=0.2)
        trek = TrekFactory.create(name='Trek', no_path=True)
        trek.add_path(path, start=0.2, end=0.3)
        service = ServiceFactory.create(no_path=True, type__name='ServiceType')
        service.add_path(path, start=0.2, end=0.3)
        signage = SignageFactory.create(name='Signage', no_path=True)
        signage.add_path(path, start=0.2, end=0.2)
        infrastructure = InfrastructureFactory.create(name='Infrastructure', no_path=True)
        infrastructure.add_path(path, start=0.2, end=0.2)
        intervention1 = InterventionFactory.create(topology=signage, name='Intervention1')
        t = TopologyFactory.create(no_path=True)
        t.add_path(path, start=0.2, end=0.5)
        intervention2 = InterventionFactory.create(topology=t, name='Intervention2')
        response = self.client.get(path.get_delete_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Different topologies are linked with this path')
        self.assertContains(response, '<a href="/poi/%d/">POI</a>' % poi.pk)
        self.assertContains(response, '<a href="/trail/%d/">Trail</a>' % trail.pk)
        self.assertContains(response, '<a href="/trek/%d/">Trek</a>' % trek.pk)
        self.assertContains(response, '<a href="/service/%d/">ServiceType</a>' % service.pk)
        self.assertContains(response, '<a href="/signage/%d/">Signage</a>' % signage.pk)
        self.assertContains(response, '<a href="/infrastructure/%d/">Infrastructure</a>' % infrastructure.pk)
        self.assertContains(response, '<a href="/intervention/%d/">Intervention1</a>' % intervention1.pk)
        self.assertContains(response, '<a href="/intervention/%d/">Intervention2</a>' % intervention2.pk)

    def test_elevation_area_json(self):
        self.login()
        path = self.modelfactory.create()
        url = '/api/en/paths/{pk}/dem.json'.format(pk=path.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

    def test_sum_path_zero(self):
        self.login()
        response = self.client.get('/api/path/paths.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode())['sumPath'], 0.0)

    def test_sum_path_two(self):
        self.login()
        PathFactory()
        PathFactory()
        response = self.client.get('/api/path/paths.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode())['sumPath'], 0.3)

    def test_merge_fails(self):
        self.login()
        with self.assertRaises(AssertionError):
            self.client.post('/mergepath/')
        p1 = PathFactory.create()
        p1.save()
        p2 = PathFactory.create()
        p2.save()
        response = self.client.post('/mergepath/', {'path[]': [p1.pk, p2.pk]})
        self.assertEqual(response.content, b'error')

    def test_merge_fails_trigger(self):
        self.login()
        p1 = PathFactory.create(name="AB", geom=LineString((0, 0), (1, 0)))
        p2 = PathFactory.create(name="BC", geom=LineString((500, 0), (1000, 0)))
        response = self.client.post('/mergepath/', {'path[]': [p1.pk, p2.pk]})
        self.assertEqual(response.content, b'error')
        p3 = PathFactory.create(name="AB", geom=LineString((1, 0), (2, 0)))
        p4 = PathFactory.create(name="BC", geom=LineString((1, 0), (10, 10)))
        response = self.client.post('/mergepath/', {'path[]': [p3.pk, p4.pk]})
        self.assertEqual(response.content, b'error')

    def test_mege_works(self):
        self.login()
        p1 = PathFactory.create(name="AB", geom=LineString((0, 0), (1, 0)))
        p2 = PathFactory.create(name="BC", geom=LineString((1, 0), (2, 0)))
        response = self.client.post('/mergepath/', {'path[]': [p1.pk, p2.pk]})
        self.assertEqual(response.content, b'success')
        p1.reload()
        self.assertEqual(p1.geom, LineString((0, 0), (1, 0), (2, 0), srid=settings.SRID))


class DenormalizedTrailTest(AuthentFixturesTest):
    def setUp(self):
        self.trail1 = TrailFactory(no_path=True)
        self.trail2 = TrailFactory(no_path=True)
        self.path = PathFactory()
        self.trail1.add_path(self.path)
        self.trail2.add_path(self.path)

    def test_path_and_trails_are_linked(self):
        self.assertIn(self.trail1, self.path.trails.all())
        self.assertIn(self.trail2, self.path.trails.all())

    def login(self):
        user = PathManagerFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

    def test_denormalized_path_trails(self):
        PathFactory.create_batch(size=50)
        TrailFactory.create_batch(size=50)
        self.login()
        with self.assertNumQueries(LTE(15)):
            self.client.get(reverse('core:path_json_list'))

    def test_trails_are_shown_as_links_in_list(self):
        self.login()
        response = self.client.get(reverse('core:path_json_list'))
        self.assertEqual(response.status_code, 200)
        paths_json = json.loads(response.content.decode())
        trails_column = paths_json['aaData'][0][6]
        self.assertTrue(trails_column == '%s, %s' % (self.trail1.name_display, self.trail2.name_display)
                        or trails_column == '%s, %s' % (self.trail2.name_display, self.trail1.name_display))


class TrailViewsTest(CommonTest):
    model = Trail
    modelfactory = TrailFactory
    userfactory = PathManagerFactory

    def get_good_data(self):
        path = PathFactory.create()
        return {
            'name': 't',
            'departure': 'Below',
            'arrival': 'Above',
            'comments': 'No comment',
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def test_detail_page(self):
        self.login()
        trail = TrailFactory()
        response = self.client.get(trail.get_detail_url())
        self.assertEqual(response.status_code, 200)

    @mock.patch('mapentity.models.MapEntityMixin.get_attributes_html')
    def test_document_export(self, get_attributes_html):
        get_attributes_html.return_value = b'<p>mock</p>'
        trail = TrailFactory()
        self.login()
        with open(trail.get_map_image_path(), 'wb+') as f:
            f.write(b'***' * 1000)
        response = self.client.get(trail.get_document_url())
        self.assertEqual(response.status_code, 200)

    def test_add_trail_from_existing_topology_does_not_use_pk(self):
        import bs4

        self.login()
        trail = TrailFactory(offset=3.14)
        response = self.client.get(Trail.get_add_url() + '?topology=%s' % trail.pk)
        soup = bs4.BeautifulSoup(response.content, 'lxml')
        textarea_field = soup.find(id="id_topology")
        self.assertIn('"kind": "TOPOLOGY"', textarea_field.text)
        self.assertIn('"offset": 3.14', textarea_field.text)
        self.assertNotIn('"pk": %s' % trail.pk, textarea_field.text)

    def test_add_trail_from_existing_topology(self):
        self.login()
        trail = TrailFactory()
        form_data = self.get_good_data()
        form_data['topology'] = trail.serialize(with_pk=False)
        response = self.client.post(Trail.get_add_url(), form_data)
        self.assertEqual(response.status_code, 302)  # success, redirects to detail view
        p = re.compile(r"/trail/(\d+)/")
        m = p.match(response['Location'])
        new_pk = int(m.group(1))
        new_trail = Trail.objects.get(pk=new_pk)
        self.assertIn(trail, new_trail.trails.all())


class RemovePathKeepTopology(TestCase):
    def test_remove_poi(self):
        """
        poi is linked with AB

            poi
             +                D
             *                |
             *                |
        A---------B           C
             |----|
               e1

        we got after remove AB :

             poi
              + * * * * * * * D
                              |
                              |
                              C

        poi is linked with DC and e1 is deleted
        """
        ab = PathFactory.create(name="AB", geom=LineString((0, 0), (1, 0)))
        PathFactory.create(name="CD", geom=LineString((2, 0), (2, 1)))
        poi = POIFactory.create(no_path=True, offset=1)
        e1 = TopologyFactory.create(no_path=True)
        PathAggregationFactory.create(path=ab, topo_object=e1, start_position=0.5, end_position=1)
        poi.add_path(ab, start=0.5, end=0.5)
        poi.save()

        self.assertTrue(almostequal(1, poi.offset))

        self.assertEqual(poi.geom, Point(0.5, 1.0, srid=2154))

        ab.delete()
        poi.reload()
        e1.reload()

        self.assertEqual(len(Path.objects.all()), 1)

        self.assertEqual(e1.deleted, True)
        self.assertEqual(poi.deleted, False)

        self.assertTrue(almostequal(1.5, poi.offset))
