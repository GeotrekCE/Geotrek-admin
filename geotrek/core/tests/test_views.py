from mapentity.views.generic import MapEntityList
from geotrek.common.mixins import CustomColumnsMixin
import re
from unittest import skipIf, mock

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth.models import Permission
from django.test.utils import override_settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.gis.geos import LineString, Point, Polygon, MultiPolygon
from django.test import TestCase

from mapentity.tests.factories import UserFactory

from geotrek.common.tests import CommonTest

from geotrek.authent.tests.factories import PathManagerFactory, StructureFactory
from geotrek.authent.tests.base import AuthentFixturesTest

from geotrek.core.views import PathFormatList, PathList
from geotrek.core.models import Path, Trail, PathSource

from geotrek.trekking.tests.factories import POIFactory, TrekFactory, ServiceFactory
from geotrek.infrastructure.tests.factories import InfrastructureFactory
from geotrek.signage.tests.factories import SignageFactory
from geotrek.maintenance.tests.factories import InterventionFactory
from geotrek.core.tests.factories import PathFactory, StakeFactory, TrailFactory, ComfortFactory, TopologyFactory
from geotrek.zoning.tests.factories import CityFactory, DistrictFactory, RestrictedAreaFactory, RestrictedAreaTypeFactory

from unittest.mock import patch


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class MultiplePathViewsTest(AuthentFixturesTest, TestCase):
    def setUp(self):
        self.login()

    def login(self):
        self.user = PathManagerFactory.create(password='booh')
        success = self.client.login(username=self.user.username, password='booh')
        self.assertTrue(success)

    def logout(self):
        self.client.logout()

    def test_show_delete_multiple_path_in_list(self):
        path_1 = PathFactory.create(name="path_1", geom=LineString((0, 0), (4, 0)))
        PathFactory.create(name="path_2", geom=LineString((2, 2), (2, -2)))
        POIFactory.create(paths=[(path_1, 0, 0)])
        response = self.client.get(reverse('core:path_list'))
        self.assertContains(response, '<a href="#delete" id="btn-delete" role="button">')

    def test_delete_view_multiple_path(self):
        path_1 = PathFactory.create(name="path_1", geom=LineString((0, 0), (4, 0)))
        path_2 = PathFactory.create(name="path_2", geom=LineString((2, 2), (2, -2)))
        response = self.client.get(reverse('core:multiple_path_delete', args=['%s,%s' % (path_1.pk, path_2.pk)]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Do you really wish to delete')

    def test_delete_view_multiple_path_one_wrong_structure(self):
        other_structure = StructureFactory(name="Other")
        path_1 = PathFactory.create(name="path_1", geom=LineString((0, 0), (4, 0)))
        path_2 = PathFactory.create(name="path_2", geom=LineString((2, 2), (2, -2)), structure=other_structure)
        POIFactory.create(paths=[(path_1, 0, 0)])
        response = self.client.get(reverse('core:multiple_path_delete', args=['%s,%s' % (path_1.pk, path_2.pk)]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('core:path_list'))
        self.assertIn(response.content, b'Access to the requested resource is restricted by structure.')
        self.assertEqual(Path.objects.count(), 4)

    def test_delete_multiple_path(self):
        path_1 = PathFactory.create(name="path_1", geom=LineString((0, 0), (4, 0)))
        path_2 = PathFactory.create(name="path_2", geom=LineString((2, 2), (2, -2)))
        POIFactory.create(paths=[(path_1, 0, 0)], name="POI_1")
        InfrastructureFactory.create(paths=[(path_1, 0, 1)], name="INFRA_1")
        signage = SignageFactory.create(paths=[(path_1, 0, 1)], name="SIGNA_1")
        TrailFactory.create(paths=[(path_2, 0, 1)], name="TRAIL_1")
        ServiceFactory.create(paths=[(path_2, 0, 1)])
        InterventionFactory.create(target=signage, name="INTER_1")
        response = self.client.get(reverse('core:multiple_path_delete', args=['%s,%s' % (path_1.pk, path_2.pk)]))
        self.assertContains(response, "POI_1")
        self.assertContains(response, "INFRA_1")
        self.assertContains(response, "SIGNA_1")
        self.assertContains(response, "TRAIL_1")
        self.assertContains(response, "Service type")
        self.assertContains(response, "INTER_1")
        response = self.client.post(reverse('core:multiple_path_delete', args=['%s,%s' % (path_1.pk, path_2.pk)]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Path.objects.count(), 2)
        self.assertEqual(Path.objects.filter(pk__in=[path_1.pk, path_2.pk]).count(), 0)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PathViewsTest(CommonTest):
    model = Path
    modelfactory = PathFactory
    userfactory = PathManagerFactory
    expected_json_geom = {
        'type': 'LineString',
        'coordinates': [[3.0, 46.5], [3.001304, 46.5009004]],
    }
    length = 141.42135623731

    def get_expected_json_attrs(self):
        return {
            'arrival': '',
            'ascent': 0,
            'departure': '',
            'descent': 0,
            'draft': False,
            'eid': None,
            'max_elevation': 0,
            'min_elevation': 0,
            'name': self.obj.name,
            'slope': 0.0,
            'valid': True,
            'visible': True
        }

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
        super()._post_add_form()

    def test_draft_permission_detail(self):
        path = PathFactory(name="DRAFT_PATH", draft=True)
        user = UserFactory(password='booh')
        p = user.profile
        p.save()
        perm_add_draft_path = Permission.objects.get(codename='add_draft_path')
        perm_delete_draft_path = Permission.objects.get(codename='delete_draft_path')
        perm_change_draft_path = Permission.objects.get(codename='change_draft_path')
        perm_read_path = Permission.objects.get(codename='read_path')
        user.user_permissions.add(perm_delete_draft_path)
        user.user_permissions.add(perm_read_path)
        user.user_permissions.add(perm_change_draft_path)
        user.user_permissions.add(perm_add_draft_path)
        self.client.login(username=user.username, password='booh')
        response = self.client.get(path.get_update_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, path.get_delete_url())

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

    def test_set_structure_with_permission_object_linked_none_structure(self):
        if not hasattr(self.model, 'structure'):
            return
        self.login()
        perm = Permission.objects.get(codename='can_bypass_structure')
        self.user.user_permissions.add(perm)
        structure = StructureFactory()
        st0 = StakeFactory.create(structure=None)
        self.assertNotEqual(structure, self.user.profile.structure)
        data = self.get_good_data()
        data['stake'] = st0.pk
        data['structure'] = self.user.profile.structure.pk
        response = self.client.post(self._get_add_url(), data)
        self.assertEqual(response.status_code, 302)
        obj = self.model.objects.last()
        self.assertEqual(obj.structure, self.user.profile.structure)
        self.logout()

    def test_basic_format(self):
        self.modelfactory.create()
        self.modelfactory.create(name="ãéè")
        super().test_basic_format()

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
        poi = POIFactory.create(name='POI', paths=[(path, 0.5, 0.5)])
        trail = TrailFactory.create(name='Trail', paths=[(path, 0.1, 0.2)])
        trek = TrekFactory.create(name='Trek', paths=[(path, 0.2, 0.3)])
        service = ServiceFactory.create(paths=[(path, 0.2, 0.3)], type__name='ServiceType')
        signage = SignageFactory.create(name='Signage', paths=[(path, 0.2, 0.2)])
        infrastructure = InfrastructureFactory.create(name='Infrastructure', paths=[(path, 0.2, 0.2)])
        intervention1 = InterventionFactory.create(target=signage, name='Intervention1')
        t = TopologyFactory.create(paths=[(path, 0.2, 0.5)])
        intervention2 = InterventionFactory.create(target=t, name='Intervention2')
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
        self.assertEqual(response.json()['sumPath'], 0.0)

    def test_sum_path_two(self):
        self.login()
        PathFactory()
        PathFactory()
        response = self.client.get('/api/path/paths.json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['sumPath'], 0.3)

    def test_sum_path_filter_cities(self):
        self.login()
        p1 = PathFactory(geom=LineString((0, 0), (0, 1000), srid=settings.SRID))
        city = CityFactory(code='09000', geom=MultiPolygon(Polygon(((200, 0), (300, 0), (300, 100), (200, 100), (200, 0)), srid=settings.SRID)))
        city2 = CityFactory(code='09001', geom=MultiPolygon(
            Polygon(((0, 0), (1000, 0), (1000, 1000), (0, 1000), (0, 0)), srid=settings.SRID)))
        self.assertEqual(len(p1.cities), 1)
        response = self.client.get('/api/path/paths.json?city=%s' % city.code)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['sumPath'], 0.0)
        response = self.client.get('/api/path/paths.json?city=%s' % city2.code)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['sumPath'], 1.0)

    def test_sum_path_filter_districts(self):
        self.login()
        p1 = PathFactory(geom=LineString((0, 0), (0, 1000), srid=settings.SRID))
        district = DistrictFactory(geom=MultiPolygon(Polygon(((200, 0), (300, 0), (300, 100), (200, 100), (200, 0)), srid=settings.SRID)))
        district2 = DistrictFactory(geom=MultiPolygon(
            Polygon(((0, 0), (1000, 0), (1000, 1000), (0, 1000), (0, 0)), srid=settings.SRID)))
        self.assertEqual(len(p1.districts), 1)
        response = self.client.get('/api/path/paths.json?district=%s' % district.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['sumPath'], 0.0)
        response = self.client.get('/api/path/paths.json?district=%s' % district2.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['sumPath'], 1.0)

    def test_merge_fails_parameters(self):
        """
        Should fail if path[] length != 2
        """
        self.login()
        p1 = PathFactory.create()
        p2 = PathFactory.create()
        response = self.client.post(reverse('core:merge_path'), {'path[]': [p1.pk]})
        self.assertEqual({'error': 'You should select two paths'}, response.json())

        response = self.client.post(reverse('core:merge_path'), {'path[]': [p1.pk, p1.pk, p2.pk]})
        self.assertEqual({'error': 'You should select two paths'}, response.json())
        self.logout()

    def test_merge_fails_donttouch(self):
        self.login()
        p3 = PathFactory.create(name="AB", geom=LineString((0, 0), (1, 0)))
        p4 = PathFactory.create(name="BC", geom=LineString((500, 0), (1000, 0)))

        response = self.client.post(reverse('core:merge_path'), {'path[]': [p3.pk, p4.pk]})
        self.assertEqual({'error': 'No matching points to merge paths found'}, response.json())
        self.logout()

    def test_merge_fails_other_path_intersection_less_than_snapping(self):
        """
        Merge should fail if other path share merge intersection

                          |
                          C
                          |

        |--------A--------|-----------B-----------|

        """
        self.login()
        path_a = PathFactory.create(name="A", geom=LineString((0, 0), (10, 0)))
        path_b = PathFactory.create(name="B", geom=LineString((11, 0), (20, 0)))
        PathFactory.create(name="C", geom=LineString((10, 1), (10, 10)))
        response = self.client.post(reverse('core:merge_path'), {'path[]': [path_a.pk, path_b.pk]})
        json_response = response.json()
        self.assertIn('error', json_response)
        self.assertEqual(json_response['error'], "You can't merge 2 paths with a 3rd path in the intersection")
        self.logout()

    def test_merge_fails_other_path_intersection(self):
        """
        Merge should fail if other path share merge intersection

                          |
                          C
                          |
        |--------A--------|-----------B-----------|

        """
        self.login()
        path_a = PathFactory.create(name="A", geom=LineString((0, 0), (10, 0)))
        path_b = PathFactory.create(name="B", geom=LineString((10, 0), (20, 0)))
        PathFactory.create(name="C", geom=LineString((10, 0), (10, 10)))
        response = self.client.post(reverse('core:merge_path'), {'path[]': [path_a.pk, path_b.pk]})
        json_response = response.json()
        self.assertIn('error', json_response)
        self.assertEqual(json_response['error'], "You can't merge 2 paths with a 3rd path in the intersection")
        self.logout()

    def test_merge_fails_other_path_intersection_2(self):
        """
        Merge should fail if other path share merge intersection

                          |
                          C (reversed)
                          |
        |--------A--------|-----------B-----------|

        """
        self.login()
        path_a = PathFactory.create(name="A", geom=LineString((0, 0), (10, 0)))
        path_b = PathFactory.create(name="B", geom=LineString((10, 0), (20, 0)))
        PathFactory.create(name="C", geom=LineString((10, 10), (10, 0)))
        response = self.client.post(reverse('core:merge_path'), {'path[]': [path_a.pk, path_b.pk]})
        json_response = response.json()
        self.assertIn('error', json_response)
        self.assertEqual(json_response['error'], "You can't merge 2 paths with a 3rd path in the intersection")
        self.logout()

    def test_merge_fails_other_path_intersection_3(self):
        """
        Merge should fail if other path share merge intersection

        |--------C--------|
        C                 C
        |                 |
        |--------A--------|-----------B-----------|

        """
        self.login()
        path_a = PathFactory.create(name="A", geom=LineString((0, 0), (10, 0)))
        path_b = PathFactory.create(name="B", geom=LineString((10, 0), (20, 0)))
        PathFactory.create(name="C", geom=LineString((0, 0), (0, 10), (10, 10), (10, 0)))
        response = self.client.post(reverse('core:merge_path'), {'path[]': [path_a.pk, path_b.pk]})
        json_response = response.json()
        self.assertIn('error', json_response)
        self.assertEqual(json_response['error'], "You can't merge 2 paths with a 3rd path in the intersection")
        self.logout()

    def test_merge_not_fail_draftpath_intersection(self):
        """
        Merge should not fail
                          .
                          C (draft)
                          .
        |--------A--------|-----------B-----------|

        """
        self.login()
        path_a = PathFactory.create(name="A", geom=LineString((0, 0), (10, 0)))
        path_b = PathFactory.create(name="B", geom=LineString((10, 0), (20, 0)))
        PathFactory.create(name="C", geom=LineString((10, 0), (10, 10)), draft=True)
        response = self.client.post(reverse('core:merge_path'), {'path[]': [path_a.pk, path_b.pk]})
        self.assertIn('success', response.json())
        self.logout()

    def test_merge_not_fail_start_point_end_point(self):
        """
        Merge should not fail
        |
        C
        |
        |--------A--------|-----------B-----------|

        """
        self.login()
        path_a = PathFactory.create(name="A", geom=LineString((0, 0), (10, 0)))
        path_b = PathFactory.create(name="B", geom=LineString((10, 0), (20, 0)))
        PathFactory.create(name="C", geom=LineString((0, 0), (0, 10)))
        response = self.client.post(reverse('core:merge_path'), {'path[]': [path_a.pk, path_b.pk]})
        self.assertIn('success', response.json())
        self.logout()

    def test_merge_not_fail_start_point_end_point_2(self):
        """
        Merge should not fail
        |
        C (reversed)
        |
        |--------A--------|-----------B-----------|

        """
        self.login()
        path_a = PathFactory.create(name="A", geom=LineString((0, 0), (10, 0)))
        path_b = PathFactory.create(name="B", geom=LineString((10, 0), (20, 0)))
        PathFactory.create(name="C", geom=LineString((0, 10), (0, 0)))
        response = self.client.post(reverse('core:merge_path'), {'path[]': [path_a.pk, path_b.pk]})
        self.assertIn('success', response.json())
        self.logout()

    def test_merge_not_fail_start_point_end_point_3(self):
        """
        Merge should not fail
                                                  |
                                                  C
                                                  |
        |--------A--------|-----------B-----------|

        """
        self.login()
        path_a = PathFactory.create(name="A", geom=LineString((0, 0), (10, 0)))
        path_b = PathFactory.create(name="B", geom=LineString((10, 0), (20, 0)))
        PathFactory.create(name="C", geom=LineString((20, 0), (20, 10)))
        response = self.client.post(reverse('core:merge_path'), {'path[]': [path_a.pk, path_b.pk]})
        self.assertIn('success', response.json())
        self.logout()

    def test_merge_not_fail_start_point_end_point_4(self):
        """
        Merge should not fail
                                                  |
                                                  C (reversed)
                                                  |
        |--------A--------|-----------B-----------|

        """
        self.login()
        path_a = PathFactory.create(name="A", geom=LineString((0, 0), (10, 0)))
        path_b = PathFactory.create(name="B", geom=LineString((10, 0), (20, 0)))
        PathFactory.create(name="C", geom=LineString((20, 10), (20, 0)))
        response = self.client.post(reverse('core:merge_path'), {'path[]': [path_a.pk, path_b.pk]})
        self.assertIn('success', response.json())
        self.logout()

    def test_merge_works(self):
        self.login()
        p1 = PathFactory.create(name="AB", geom=LineString((0, 0), (1, 0)))
        p2 = PathFactory.create(name="BC", geom=LineString((1, 0), (2, 0)))
        response = self.client.post(reverse('core:merge_path'), {'path[]': [p1.pk, p2.pk]})
        self.assertIn('success', response.json())
        self.logout()

    def test_merge_works_wrong_structure(self):
        self.login()
        other_structure = StructureFactory(name="Other")
        p1 = PathFactory.create(name="AB", geom=LineString((0, 0), (1, 0)))
        p2 = PathFactory.create(name="BC", geom=LineString((1, 0), (2, 0)), structure=other_structure)
        response = self.client.post(reverse('core:merge_path'), {'path[]': [p1.pk, p2.pk]})
        self.assertEqual({'error': "You don't have the right to change these paths"}, response.json())
        self.logout()

    def test_merge_works_other_line(self):
        self.login()
        p1 = PathFactory.create(name="AB", geom=LineString((0, 0), (1, 0)))
        p2 = PathFactory.create(name="BC", geom=LineString((1, 0), (2, 0)))

        PathFactory.create(name="CD", geom=LineString((2, 1), (3, 1)))
        response = self.client.post(reverse('core:merge_path'), {'path[]': [p1.pk, p2.pk]})
        self.assertIn('success', response.json())
        self.logout()

    def test_merge_fails_draft_with_nodraft(self):
        """
            Draft               Not Draft
        A---------------B + C-------------------D

        Do not merge !
        """
        self.login()
        p1 = PathFactory.create(name="PATH_AB", geom=LineString((0, 1), (10, 1)), draft=True)
        p2 = PathFactory.create(name="PATH_CD", geom=LineString((10, 1), (20, 1)), draft=False)
        response = self.client.post(reverse('core:merge_path'), {'path[]': [p1.pk, p2.pk]})
        self.assertIn('error', response.json())
        self.logout()

    def test_merge_ok_draft_with_draft(self):
        """
            Draft               Draft
        A---------------B + C-------------------D

        Merge !
        """
        self.login()
        p1 = PathFactory.create(name="PATH_AB", geom=LineString((0, 1), (10, 1)), draft=True)
        p2 = PathFactory.create(name="PATH_CD", geom=LineString((10, 1), (20, 1)), draft=True)
        response = self.client.post(reverse('core:merge_path'), {'path[]': [p1.pk, p2.pk]})
        self.assertIn('success', response.json())
        self.logout()

    def test_structure_is_not_changed_with_permission_error(self):
        self.login()
        perm = Permission.objects.get(codename='can_bypass_structure')
        self.user.user_permissions.add(perm)
        structure = StructureFactory()
        structure_2 = StructureFactory()
        source = PathSource.objects.create(source="Source_1", structure=structure)
        self.assertNotEqual(structure, self.user.profile.structure)
        obj = self.modelfactory.create(structure=structure)
        data = self.get_good_data().copy()
        data['source'] = source.pk
        data['structure'] = structure_2.pk
        response = self.client.post(obj.get_update_url(), data)
        self.assertContains(response, "Please select a choice related to all structures")
        self.logout()

    def test_restricted_area_urls_fragment(self):
        area_type = RestrictedAreaTypeFactory(name="Test")
        self.login()
        obj = self.modelfactory()
        response = self.client.get(obj.get_detail_url())
        self.assertNotContains(response, '/api/restrictedarea/type/{}/restrictedarea.geojson'.format(area_type.pk))

        self.restricted_area = RestrictedAreaFactory(area_type=area_type, name="Tel",
                                                     geom=MultiPolygon(Polygon(((0, 0), (300, 0), (300, 100), (200, 100), (0, 0)),
                                                                               srid=settings.SRID)))
        response = self.client.get(obj.get_detail_url())
        self.assertContains(response, '/api/restrictedarea/type/{}/restrictedarea.geojson'.format(area_type.pk))

    def test_draft_path_layer(self):
        self.login()
        obj = self.modelfactory(draft=False)
        self.modelfactory(draft=False)
        self.modelfactory(draft=True)
        response = self.client.get(obj.get_layer_url(), {"no_draft": "true"})
        self.assertEqual(len(response.json()['features']), 2)

    @override_settings(COLUMNS_LISTS={'path_view': ['length_2d', 'valid', 'structure', 'visible', 'min_elevation', 'max_elevation']})
    def test_custom_columns_mixin_on_list(self):
        # Assert columns equal mandatoy columns plus custom extra columns
        self.assertEqual(PathList().columns, ['id', 'checkbox', 'name', 'length', 'length_2d', 'valid', 'structure', 'visible', 'min_elevation', 'max_elevation'])

    @override_settings(COLUMNS_LISTS={'path_export': ['length_2d', 'valid', 'structure', 'visible', 'min_elevation', 'max_elevation']})
    def test_custom_columns_mixin_on_export(self):
        # Assert columns equal mandatoy columns plus custom extra columns
        self.assertEqual(PathFormatList().columns, ['id', 'length_2d', 'valid', 'structure', 'visible', 'min_elevation', 'max_elevation'])

    @override_settings(COLUMNS_LISTS={})
    @patch('geotrek.common.mixins.logger')
    def test_custom_columns_mixin_error_log(self, mock_logger):
        # Create view where columns fields are omitted
        class MissingColumns(CustomColumnsMixin, MapEntityList):
            model = Path
            # columns = None

        MissingColumns()
        # Assert logger raises error message
        message = "Cannot build columns for class MissingColumns.\nPlease define on this class either : \n  - a field 'columns'\nOR \n  - two fields 'mandatory_columns' AND 'default_extra_columns'"
        mock_logger.error.assert_called_with(message)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PathKmlGPXTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(is_staff=True, is_superuser=True)
        self.client.force_login(self.user)

        self.path = PathFactory.create(comments='exportable path')

        self.gpx_response = self.client.get(reverse('core:path_gpx_detail', args=('en', self.path.pk, 'slug')))
        self.gpx_parsed = BeautifulSoup(self.gpx_response.content, 'lxml')

        self.kml_response = self.client.get(reverse('core:path_kml_detail', args=('en', self.path.pk, 'slug')))

    def test_gpx_is_served_with_content_type(self):
        self.assertEqual(self.gpx_response.status_code, 200)
        self.assertEqual(self.gpx_response['Content-Type'], 'application/gpx+xml')

    def test_gpx_trek_as_track_points(self):
        self.assertEqual(len(self.gpx_parsed.findAll('trk')), 1)
        self.assertEqual(len(self.gpx_parsed.findAll('trkpt')), 2)
        self.assertEqual(len(self.gpx_parsed.findAll('ele')), 2)

    def test_kml_is_served_with_content_type(self):
        self.assertEqual(self.kml_response.status_code, 200)
        self.assertEqual(self.kml_response['Content-Type'], 'application/vnd.google-earth.kml+xml')


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class DenormalizedTrailTest(AuthentFixturesTest):
    def setUp(self):
        self.path = PathFactory()
        self.trail1 = TrailFactory(paths=[self.path])
        self.trail2 = TrailFactory(paths=[self.path])

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
        with self.assertNumQueries(7):
            self.client.get(reverse('core:path_json_list'))


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class TrailViewsTest(CommonTest):
    model = Trail
    modelfactory = TrailFactory
    userfactory = PathManagerFactory
    expected_json_geom = {
        'type': 'LineString',
        'coordinates': [[3.0, 46.5], [3.001304, 46.5009004]],
    }

    def get_expected_json_attrs(self):
        return {
            'name': self.obj.name,
            'departure': self.obj.departure,
            'arrival': self.obj.arrival,
            'comments': self.obj.comments,
        }

    def get_good_data(self):
        good_data = {
            'name': 't',
            'departure': 'Below',
            'arrival': 'Above',
            'comments': 'No comment'
        }
        if settings.TREKKING_TOPOLOGY_ENABLED:
            path = PathFactory.create()
            good_data['topology'] = '{"paths": [%s]}' % path.pk
        else:
            good_data['geom'] = 'SRID=4326;LINESTRING (0.0 0.0, 1.0 1.0)'
        return good_data

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
        with open(trail.get_map_image_path(), 'wb') as f:
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
        self.assertIn('"kind": "TMP"', textarea_field.text)
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


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class TrailKmlGPXTest(TestCase):
    def setUp(self):
        super().setUp()
        self.user = UserFactory.create(is_staff=True, is_superuser=True)
        self.client.force_login(self.user)

        self.trail = TrailFactory.create(comments='exportable trail')

        self.gpx_response = self.client.get(reverse('core:trail_gpx_detail', args=('en', self.trail.pk, 'slug')))
        self.gpx_parsed = BeautifulSoup(self.gpx_response.content, 'lxml')

        self.kml_response = self.client.get(reverse('core:trail_kml_detail', args=('en', self.trail.pk, 'slug')))

    def test_gpx_is_served_with_content_type(self):
        self.assertEqual(self.gpx_response.status_code, 200)
        self.assertEqual(self.gpx_response['Content-Type'], 'application/gpx+xml')

    def test_gpx_trek_as_track_points(self):
        self.assertEqual(len(self.gpx_parsed.findAll('trk')), 1)
        self.assertEqual(len(self.gpx_parsed.findAll('trkpt')), 2)
        self.assertEqual(len(self.gpx_parsed.findAll('ele')), 2)

    def test_kml_is_served_with_content_type(self):
        self.assertEqual(self.kml_response.status_code, 200)
        self.assertEqual(self.kml_response['Content-Type'], 'application/vnd.google-earth.kml+xml')


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
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
        poi = POIFactory.create(paths=[(ab, 0.5, 0.5)], offset=1)
        e1 = TopologyFactory.create(paths=[(ab, 0.5, 1)])

        self.assertAlmostEqual(1, poi.offset)
        self.assertEqual(poi.geom, Point(0.5, 1.0, srid=2154))

        ab.delete()
        poi.reload()
        e1.reload()

        self.assertEqual(len(Path.objects.all()), 1)

        self.assertEqual(e1.deleted, True)
        self.assertEqual(poi.deleted, False)

        self.assertAlmostEqual(1.5, poi.offset)
