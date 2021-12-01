from django.http import QueryDict
from django.test import TestCase

from geotrek.common.factories import OrganismFactory
from geotrek.outdoor.factories import SiteFactory, PracticeFactory, CourseFactory
from geotrek.outdoor.filters import SiteFilterSet, CourseFilterSet


class SiteFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.practice = PracticeFactory(name="Child practice", sector__name="Child sector")
        cls.org_a = OrganismFactory(organism='a')
        cls.org_b = OrganismFactory(organism='b')
        cls.org_c = OrganismFactory(organism='c')
        cls.org_d = OrganismFactory(organism='d')
        parent = SiteFactory.create(practice=None, orientation=['E', 'S'], name='Parent site',
                                    managers=[cls.org_a, cls.org_b])
        SiteFactory.create(practice=cls.practice, orientation=['NE', 'W'], parent=parent, name='Child site',
                           managers=[cls.org_c, cls.org_d])
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

    def test_managers_filter(self):
        filterset = SiteFilterSet(QueryDict('managers={}'.format(self.org_a.pk)))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Site: Parent site>'])

    def test_managers_filter_or(self):
        filterset = SiteFilterSet(QueryDict('managers={}&managers={}'.format(self.org_b.pk, self.org_d.pk)))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Site: Parent site>', '<Site: Child site>'])


class CourseFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site1 = SiteFactory(orientation=['E', 'S'])
        cls.site2 = SiteFactory(orientation=['NE', 'W'])
        cls.course1 = CourseFactory.create(name='Course 1')
        cls.course2 = CourseFactory.create(name='Course 2')
        cls.course1.parent_sites.set([cls.site1])
        cls.course2.parent_sites.set([cls.site2])

    def test_orientation_filter(self):
        filterset = CourseFilterSet(QueryDict('orientation=E'))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Course: Course 1>'])

    def test_orientation_filter_or(self):
        filterset = CourseFilterSet(QueryDict('orientation=S&orientation=W'))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertQuerysetEqual(filterset.qs, ['<Course: Course 1>', '<Course: Course 2>'])
