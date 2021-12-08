from unittest import mock

from django.contrib.gis.geos.collections import MultiPoint
from django.contrib.gis.geos.point import Point
from django.test import TestCase
from django.test.utils import override_settings

from geotrek.common.tests.factories import RecordSourceFactory, TargetPortalFactory
from geotrek.outdoor.tests.factories import CourseFactory, SiteFactory
from geotrek.tourism.tests.test_views import PNG_BLACK_PIXEL


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


class CourseCustomViewTests(TestCase):
    @mock.patch('mapentity.helpers.requests.get')
    def test_public_document_pdf(self, mocked):
        course = CourseFactory.create(published=True)
        url = '/api/en/courses/{pk}/slug.pdf'.format(pk=course.pk)
        mocked.return_value.status_code = 200
        mocked.return_value.content = PNG_BLACK_PIXEL
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

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
