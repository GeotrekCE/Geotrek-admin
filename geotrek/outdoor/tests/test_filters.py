from django.http import QueryDict
from django.test import TestCase

from geotrek.common.models import Provider
from geotrek.common.tests.factories import OrganismFactory

from ..filters import CourseFilterSet, SiteFilterSet
from ..models import Course, Site
from .factories import CourseFactory, PracticeFactory, SiteFactory


class SiteFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.practice = PracticeFactory(
            name="Child practice", sector__name="Child sector"
        )
        cls.org_a = OrganismFactory(organism="a")
        cls.org_b = OrganismFactory(organism="b")
        cls.org_c = OrganismFactory(organism="c")
        cls.org_d = OrganismFactory(organism="d")
        cls.parent = SiteFactory.create(
            practice=None,
            orientation=["E", "S"],
            name="Parent site",
            managers=[cls.org_a, cls.org_b],
        )
        cls.child = SiteFactory.create(
            practice=cls.practice,
            orientation=["NE", "W"],
            parent=cls.parent,
            name="Child site",
            managers=[cls.org_c, cls.org_d],
        )
        SiteFactory.create(orientation=[], name="Alone site")

    def test_practice_filter(self):
        filterset = SiteFilterSet(QueryDict(f"practice={self.practice.pk}"))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertEqual(len(filterset.qs), 2)
        self.assertListEqual(
            list(filterset.qs.values_list("pk", flat=True)),
            [self.parent.pk, self.child.pk],
        )

    def test_sector_filter(self):
        filterset = SiteFilterSet(QueryDict(f"sector={self.practice.sector.pk}"))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertEqual(len(filterset.qs), 2)
        self.assertListEqual(
            list(filterset.qs.values_list("pk", flat=True)),
            [self.parent.pk, self.child.pk],
        )

    def test_orientation_filter(self):
        filterset = SiteFilterSet(QueryDict("orientation=E"))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertEqual(len(filterset.qs), 1)
        self.assertListEqual(
            list(filterset.qs.values_list("pk", flat=True)), [self.parent.pk]
        )

    def test_orientation_filter_or(self):
        filterset = SiteFilterSet(QueryDict("orientation=S&orientation=W"))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        queryset = filterset.qs
        self.assertEqual(len(queryset), 2)
        self.assertListEqual(
            list(queryset.values_list("pk", flat=True)), [self.parent.pk, self.child.pk]
        )

    def test_managers_filter(self):
        filterset = SiteFilterSet(QueryDict(f"managers={self.org_a.pk}"))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        queryset = filterset.qs
        self.assertEqual(len(queryset), 1)
        self.assertListEqual(
            list(queryset.values_list("pk", flat=True)), [self.parent.pk]
        )

    def test_managers_filter_or(self):
        filterset = SiteFilterSet(
            QueryDict(f"managers={self.org_b.pk}&managers={self.org_d.pk}")
        )
        self.assertTrue(filterset.is_valid(), filterset.errors)
        self.assertEqual(len(filterset.qs), 2)
        self.assertListEqual(
            list(filterset.qs.values_list("pk", flat=True)),
            [self.parent.pk, self.child.pk],
        )

    def test_provider_filter_without_provider(self):
        filter_set = SiteFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(
            Site.objects.filter(provider=None).count(), filter_set.qs.count()
        )

    def test_provider_filter_with_providers(self):
        provider1 = Provider.objects.create(name="Provider1")
        provider2 = Provider.objects.create(name="Provider2")
        site1 = SiteFactory.create(provider=provider1)
        site2 = SiteFactory.create(provider=provider2)

        filter_set = SiteFilterSet()
        filter_form = filter_set.form

        self.assertIn(
            f'<option value="{provider1.pk}">Provider1</option>', filter_form.as_p()
        )
        self.assertIn(
            f'<option value="{provider2.pk}">Provider2</option>', filter_form.as_p()
        )

        self.assertIn(site1, filter_set.qs)
        self.assertIn(site2, filter_set.qs)


class CourseFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.site1 = SiteFactory(orientation=["E", "S"])
        cls.site2 = SiteFactory(orientation=["NE", "W"])
        cls.course1 = CourseFactory.create(name="Course 1")
        cls.course2 = CourseFactory.create(name="Course 2")
        cls.course1.parent_sites.set([cls.site1])
        cls.course2.parent_sites.set([cls.site2])

    def test_orientation_filter(self):
        filterset = CourseFilterSet(QueryDict("orientation=E"))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        queryset = filterset.qs
        self.assertEqual(len(queryset), 1)
        self.assertListEqual(list(queryset), [self.course1])

    def test_orientation_filter_or(self):
        filterset = CourseFilterSet(QueryDict("orientation=S&orientation=W"))
        self.assertTrue(filterset.is_valid(), filterset.errors)
        queryset = filterset.qs
        self.assertEqual(len(queryset), 2)
        self.assertListEqual(list(queryset), [self.course1, self.course2])

    def test_provider_filter_without_provider(self):
        filter_set = CourseFilterSet(data={})
        filter_form = filter_set.form

        self.assertTrue(filter_form.is_valid())
        self.assertEqual(
            Course.objects.filter(provider=None).count(), filter_set.qs.count()
        )

    def test_provider_filter_with_providers(self):
        provider1 = Provider.objects.create(name="Provider1")
        provider2 = Provider.objects.create(name="Provider2")
        course1 = CourseFactory.create(provider=provider1)
        course2 = CourseFactory.create(provider=provider2)

        filter_set = CourseFilterSet()
        filter_form = filter_set.form

        self.assertIn(
            f'<option value="{provider1.pk}">Provider1</option>', filter_form.as_p()
        )
        self.assertIn(
            f'<option value="{provider2.pk}">Provider2</option>', filter_form.as_p()
        )

        self.assertIn(course1, filter_set.qs)
        self.assertIn(course2, filter_set.qs)
