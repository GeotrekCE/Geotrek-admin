from unittest import mock

from django.contrib.gis.geos.collections import MultiPoint
from django.contrib.gis.geos.point import Point
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory

from geotrek.common.tests.factories import (RecordSourceFactory,
                                            TargetPortalFactory)
from geotrek.outdoor import views as course_views
from geotrek.outdoor.models import Site
from geotrek.outdoor.tests.factories import CourseFactory, SiteFactory
from geotrek.tourism.tests.test_views import PNG_BLACK_PIXEL
from geotrek.trekking.tests.factories import POIFactory


class SiteCustomViewTests(TestCase):
    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        site = SiteFactory.create(published=True)
        url = '/api/en/sites/{pk}/slug.pdf'.format(pk=site.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_api_filters(self):
        SiteFactory.create(name='site1', published=False)
        SiteFactory.create(name='site2', published=True)
        site3 = SiteFactory.create(name='site3', published=True)

        site3.source.add(RecordSourceFactory.create(name='source1'))
        site3.portal.add(TargetPortalFactory.create(name='portal1'))

        response1 = self.client.get('/api/en/sites.json')
        self.assertEqual(len(response1.json()), 2)
        self.assertEqual(set((site['name'] for site in response1.json())), set(('site2', 'site3')))

        response2 = self.client.get('/api/en/sites.json?source=source1')
        self.assertEqual(len(response2.json()), 1)
        self.assertEqual(response2.json()[0]['name'], 'site3')

        response3 = self.client.get('/api/en/sites.json?portal=portal1')
        self.assertEqual(len(response3.json()), 2)
        self.assertEqual(set((site['name'] for site in response3.json())), set(('site2', 'site3')))

        response4 = self.client.get('/api/en/sites.json?portal=portalX')
        self.assertEqual(len(response4.json()), 1)
        self.assertEqual(response4.json()[0]['name'], 'site2')

    @override_settings(TREK_EXPORT_POI_LIST_LIMIT=1)
    @mock.patch('mapentity.models.MapEntityMixin.prepare_map_image')
    @mock.patch('mapentity.models.MapEntityMixin.get_attributes_html')
    def test_site_export_poi_list_limit(self, mocked_prepare, mocked_attributes):
        site = SiteFactory.create(geom="SRID=2154;GEOMETRYCOLLECTION (POINT (700000 6600000))")
        POIFactory.create(published=True)
        self.assertEqual(len(site.pois), 1)
        view = course_views.SiteDocumentPublic()
        view.object = site
        view.request = RequestFactory().get('/')
        view.kwargs = {}
        view.kwargs[view.pk_url_kwarg] = site.pk
        context = view.get_context_data()
        self.assertEqual(len(context['pois']), 1)

    def test_init_form_with_parent_site(self):
        user = SuperUserFactory()
        self.client.force_login(user)
        parent = SiteFactory(name="Parent name")
        response = self.client.get(reverse('outdoor:site_add'), {'parent_sites': parent.pk}, follow=True)
        self.assertEqual(response.status_code, 200)
        selected = f"<option value=\"{parent.pk}\" selected> {parent.name}</option>"
        self.assertContains(response, selected)

    def test_lang_in_detail_page(self):
        site = SiteFactory.create(name_fr='un site', name_en='a site')
        self.client.force_login(SuperUserFactory())

        response = self.client.get(site.get_detail_url() + '?lang=fr')
        self.assertContains(response, 'un site')
        self.assertNotContains(response, 'a site')

        response = self.client.get(site.get_detail_url() + '?lang=en')
        self.assertContains(response, 'a site')
        self.assertNotContains(response, 'un site')


class CourseCustomViewTests(TestCase):
    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        course = CourseFactory.create(published=True)
        url = '/api/en/courses/{pk}/slug.pdf'.format(pk=course.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @override_settings(TREK_EXPORT_POI_LIST_LIMIT=1)
    @mock.patch('mapentity.models.MapEntityMixin.prepare_map_image')
    @mock.patch('mapentity.models.MapEntityMixin.get_attributes_html')
    def test_course_export_poi_list_limit(self, mocked_prepare, mocked_attributes):
        course = CourseFactory.create(geom="SRID=2154;GEOMETRYCOLLECTION (POINT (700000 6600000))")
        POIFactory.create(published=True)
        self.assertEqual(len(course.pois), 1)
        view = course_views.CourseDocumentPublic()
        view.object = course
        view.request = RequestFactory().get('/')
        view.kwargs = {}
        view.kwargs[view.pk_url_kwarg] = course.pk
        context = view.get_context_data()
        self.assertEqual(len(context['pois']), 1)

    def test_api_filters(self):
        CourseFactory.create(name='course1', published=False)
        CourseFactory.create(name='course2', published=True)
        course3 = CourseFactory.create(name='course3', published=True)
        course3.parent_sites.first().source.add(RecordSourceFactory.create(name='source1'))
        course3.parent_sites.first().portal.add(TargetPortalFactory.create(name='portal1'))

        response1 = self.client.get('/api/en/courses.json')
        self.assertEqual(len(response1.json()), 2)
        self.assertEqual(set((course['name'] for course in response1.json())), set(('course2', 'course3')))

        response2 = self.client.get('/api/en/courses.json?source=source1')
        self.assertEqual(len(response2.json()), 1)
        self.assertEqual(response2.json()[0]['name'], 'course3')

        response3 = self.client.get('/api/en/courses.json?portal=portal1')
        self.assertEqual(len(response3.json()), 2)
        self.assertEqual(set((course['name'] for course in response3.json())), set(('course2', 'course3')))

        response4 = self.client.get('/api/en/courses.json?portal=portalX')
        self.assertEqual(len(response4.json()), 1)
        self.assertEqual(response4.json()[0]['name'], 'course2')

    @override_settings(API_SRID=2154)
    def test_serialize_ref_points(self):
        CourseFactory.create(name='course_with_ref_points', published=True, points_reference=MultiPoint(Point(12, 12)))
        response = self.client.get('/api/en/courses.json')
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['name'], 'course_with_ref_points')
        data = "{'type': 'MultiPoint', 'coordinates': [[12.0, 12.0]]}"
        self.assertEqual(str(response.json()[0]['points_reference']), data)

    def test_lang_in_detail_page(self):
        course = CourseFactory.create(name_fr='un parcours', name_en='a course', published=True)
        self.client.force_login(SuperUserFactory())

        response = self.client.get(course.get_detail_url() + '?lang=fr')
        self.assertContains(response, 'un parcours')
        self.assertNotContains(response, 'a course')

        response = self.client.get(course.get_detail_url() + '?lang=en')
        self.assertContains(response, 'a course')
        self.assertNotContains(response, 'un parcours')


class SiteDeleteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        self.client.force_login(user=self.user)

    def test_view_delete_site(self):
        self.site_1 = SiteFactory.create(name="site_1")
        response = self.client.get(reverse('outdoor:site_delete', args=['%s' % self.site_1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Do you really wish to delete <strong>%s</strong> ?' % (self.site_1.name))

        self.site_2 = SiteFactory.create(name="site_2")
        self.site_3 = SiteFactory.create(name="site_3", parent=self.site_2)
        response = self.client.get(reverse('outdoor:site_delete', args=['%s' % self.site_2.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You can't delete <strong>%s</strong> because it has child outdoor sites associated with it. Modify or delete these child outdoor sites before proceeding." % (self.site_2.name))

    def test_delete_site(self):
        site_1 = SiteFactory.create(name="site_1")
        site_2 = SiteFactory.create(name="site_2")
        self.assertEqual(Site.objects.count(), 2)
        response = self.client.post(reverse('outdoor:site_delete', args=['%s' % site_2.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Site.objects.count(), 1)
        self.assertEqual(Site.objects.filter(pk=site_1.pk).exists(), True)
