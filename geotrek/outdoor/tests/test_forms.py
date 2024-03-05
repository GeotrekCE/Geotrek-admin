from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.utils import override_settings
from geotrek.authent.tests.factories import UserFactory
from geotrek.outdoor.tests.factories import SiteFactory, RatingFactory, CourseFactory
from geotrek.outdoor.forms import SiteForm, CourseForm
from geotrek.outdoor.models import OrderedCourseChild


class SiteFormTest(TestCase):
    def test_ratings_save(self):
        user = UserFactory()
        rating = RatingFactory()
        site = SiteFactory(practice=rating.scale.practice)
        form = SiteForm(user=user, instance=site, data={
            'name_en': 'Site',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'practice': str(rating.scale.practice.pk),
            'rating_scale_{}'.format(rating.scale.pk): [str(rating.pk)],
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertListEqual(list(site.ratings.all().values_list('pk', flat=True)), [rating.pk])

    def test_ratings_clean(self):
        user = UserFactory()
        rating = RatingFactory()
        other_rating = RatingFactory()
        site = SiteFactory(practice=rating.scale.practice)
        form = SiteForm(user=user, instance=site, data={
            'name_en': 'Site',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'practice': str(rating.scale.practice.pk),
            'rating_scale_{}'.format(other_rating.scale.pk): [str(other_rating.pk)],
        })
        self.assertFalse(form.is_valid())
        with self.assertRaisesRegex(ValidationError, 'One of the rating scale use is not part of the practice chosen'):
            form.clean()


class CourseFormTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.rating = RatingFactory()
        cls.site = SiteFactory(practice=cls.rating.scale.practice)
        cls.course = CourseFactory()
        cls.course.parent_sites.set([cls.site])

    def test_rating_save(self):
        form = CourseForm(user=self.user, instance=self.course, data={
            'name_en': 'Course',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'parent_sites': [str(self.course.parent_sites.first().pk)],
            'rating_scale_{}'.format(self.rating.scale.pk): str(self.rating.pk),
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertListEqual(list(self.course.ratings.all().values_list('pk', flat=True)), [self.rating.pk])

    def test_no_rating_save(self):
        form = CourseForm(user=self.user, instance=self.course, data={
            'name_en': 'Course',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'parent_sites': [str(self.site.pk)],
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerySetEqual(self.course.ratings.all(), [])

    def test_points_reference(self):
        form = CourseForm(user=self.user, instance=self.course, data={
            'name_en': 'Course',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'points_reference': "{\"type\":\"MultiPoint\",\"coordinates\":[[5.82618713378906,43.767622885160975]]}",
            'parent_sites': [str(self.course.parent_sites.first().pk)],
        })
        self.assertTrue(form.is_valid())
        created = form.save()
        self.assertEqual(len(created.points_reference), 1)

    def test_form_init(self):
        site = SiteFactory()
        course = CourseFactory()
        course.parent_sites.set([site])
        form = CourseForm(user=self.user, instance=course, parent_sites=site.pk)
        self.assertEqual(form.initial['parent_sites'], [site])

    @override_settings(OUTDOOR_COURSE_POINTS_OF_REFERENCE_ENABLED=False)
    def test_no_points_reference(self):
        form = CourseForm(user=self.user, instance=self.course, data={
            'name_en': 'Course',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'points_reference': "{\"type\":\"MultiPoint\",\"coordinates\":[[5.82618713378906,43.767622885160975]]}",
            'parent_sites': [str(self.course.parent_sites.first().pk)],
        })
        self.assertTrue(form.is_valid())
        created = form.save()
        self.assertIsNone(created.points_reference)

    def test_ratings_clean(self):
        user = UserFactory()
        rating = RatingFactory()
        other_rating = RatingFactory()
        site = SiteFactory(practice=rating.scale.practice)
        form = SiteForm(user=user, instance=site, data={
            'name_en': 'Site',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'practice': str(rating.scale.practice.pk),
            f'rating_scale_{other_rating.scale.pk}': [str(other_rating.pk)],
        })
        self.assertFalse(form.is_valid())
        with self.assertRaisesRegex(ValidationError, 'One of the rating scale use is not part of the practice chosen'):
            form.clean()


class CourseItinerancyTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.course1 = CourseFactory(name="1")
        cls.course2 = CourseFactory(name="2")
        cls.course3 = CourseFactory(name="3")

    def test_two_children(self):
        OrderedCourseChild(child=self.course1, parent=self.course2, order=0).save()
        form = CourseForm(instance=self.course2, user=self.user)
        form.cleaned_data = {
            'children_course': [self.course3],
            'hidden_ordered_children': str(self.course3.pk),
        }
        form.clean_children_course()

    def test_parent_as_child(self):
        OrderedCourseChild(child=self.course1, parent=self.course2, order=0).save()
        form = CourseForm(instance=self.course3, user=self.user)
        form.cleaned_data = {
            'children_course': [self.course2],
            'hidden_ordered_children': str(self.course2.pk),
        }
        with self.assertRaisesRegex(ValidationError, 'Cannot use parent course 2 as a child course.'):
            form.clean_children_course()

    def test_child_with_itself_child(self):
        OrderedCourseChild(child=self.course1, parent=self.course2, order=0).save()
        form = CourseForm(instance=self.course1, user=self.user)
        form.cleaned_data = {
            'children_course': [self.course3],
            'hidden_ordered_children': str(self.course3.pk),
        }
        with self.assertRaisesRegex(ValidationError, 'Cannot add children because this course is itself a child.'):
            form.clean_children_course()
