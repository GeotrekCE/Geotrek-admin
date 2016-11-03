# -*- coding: utf-8 -*-
import json
import re

import mock
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from geotrek.authent.tests import AuthentFixturesTest
from geotrek.common.tests import CommonTest
from geotrek.common.utils import LTE

from geotrek.authent.factories import PathManagerFactory, StructureFactory
from geotrek.authent.models import default_structure
from geotrek.core.factories import (PathFactory, StakeFactory, TrailFactory, ComfortFactory)
from geotrek.core.models import Path, Trail


class PathViewsTest(CommonTest):
    model = Path
    modelfactory = PathFactory
    userfactory = PathManagerFactory

    def login(self):
        user = PathManagerFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

    def get_bad_data(self):
        return {'geom': '{"geom": "LINESTRING (0.0 0.0, 1.0 1.0)"}'}, _("Linestring invalid snapping.")

    def get_good_data(self):
        return {
            'name': '',
            'structure': default_structure().pk,
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
            self.assertTrue((stake.pk, unicode(stake)) in stakefield.choices)
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

    def test_basic_format(self):
        self.modelfactory.create()
        self.modelfactory.create(name=u"ãéè")
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

    def test_elevation_area_json(self):
        self.login()
        path = self.modelfactory.create()
        url = '/api/en/paths/{pk}/dem.json'.format(pk=path.pk)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')


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
        paths_json = json.loads(response.content)
        trails_column = paths_json['aaData'][0][6]
        self.assertTrue(trails_column == u'%s, %s' % (self.trail1.name_display, self.trail2.name_display) or
                        trails_column == u'%s, %s' % (self.trail2.name_display, self.trail1.name_display))


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
            'structure': default_structure().pk,
            'topology': '{"paths": [%s]}' % path.pk,
        }

    def test_detail_page(self):
        self.login()
        trail = TrailFactory()
        response = self.client.get(trail.get_detail_url())
        self.assertEqual(response.status_code, 200)

    @mock.patch('mapentity.models.MapEntityMixin.get_attributes_html')
    def test_document_export(self, get_attributes_html):
        get_attributes_html.return_value = '<p>mock</p>'
        trail = TrailFactory()
        self.login()
        with open(trail.get_map_image_path(), 'w') as f:
            f.write('***' * 1000)
        response = self.client.get(trail.get_document_url())
        self.assertEqual(response.status_code, 200)

    def test_add_trail_from_existing_topology_does_not_use_pk(self):
        import bs4

        self.login()
        trail = TrailFactory(offset=3.14)
        response = self.client.get(Trail.get_add_url() + '?topology=%s' % trail.pk)
        soup = bs4.BeautifulSoup(response.content)
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
        p = re.compile(r"http://testserver/trail/(\d+)/")
        m = p.match(response['Location'])
        new_pk = int(m.group(1))
        new_trail = Trail.objects.get(pk=new_pk)
        self.assertIn(trail, new_trail.trails.all())
