from django.http import QueryDict
from django.test import TestCase

from geotrek.outdoor.factories import SiteFactory, PracticeFactory, CourseFactory
from geotrek.outdoor.filters import SiteFilterSet, CourseFilterSet


class SiteFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.practice = PracticeFactory(name="Child practice", sector__name="Child sector")
        parent = SiteFactory.create(practice=None, orientation=['E', 'S'], name='Parent site')
        SiteFactory.create(practice=cls.practice, orientation=['NE', 'W'], parent=parent, name='Child site')
        SiteFactory.create(orientation=[], name="Alone site")

    def test_practice_filter(self):
        filterset = SiteFilterSet(QueryDict('practice={}'.format(self.practice.pk)))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Site: Parent site>', '<Site: Child site>'], ordered=False)

    def test_sector_filter(self):
        filterset = SiteFilterSet(QueryDict('sector={}'.format(self.practice.sector.pk)))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Site: Parent site>', '<Site: Child site>'], ordered=False)

    def test_orientation_filter(self):
        filterset = SiteFilterSet(QueryDict('orientation=E'))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Site: Parent site>'])

    def test_orientation_filter_or(self):
        filterset = SiteFilterSet(QueryDict('orientation=S&orientation=W'))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Site: Parent site>', '<Site: Child site>'])


class CourseFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        CourseFactory.create(site__orientation=['E', 'S'], name='Course 1')
        CourseFactory.create(site__orientation=['NE', 'W'], name='Course 2')

    def test_orientation_filter(self):
        filterset = CourseFilterSet(QueryDict('orientation=E'))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Course: Course 1>'])

    def test_orientation_filter_or(self):
        filterset = CourseFilterSet(QueryDict('orientation=S&orientation=W'))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Course: Course 1>', '<Course: Course 2>'])
