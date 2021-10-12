from django.core.exceptions import ValidationError
from django.test import TestCase
from geotrek.authent.factories import UserFactory
from geotrek.outdoor.factories import SiteFactory, RatingFactory, CourseFactory
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
        self.assertQuerysetEqual(site.ratings.all(), ['<Rating: Rating>'])


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
        self.assertQuerysetEqual(self.course.ratings.all(), ['<Rating: Rating>'])

    def test_no_rating_save(self):
        form = CourseForm(user=self.user, instance=self.course, data={
            'name_en': 'Course',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'parent_sites': [str(self.course.parent_sites.first().pk)],
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerysetEqual(self.course.ratings.all(), [])


class CourseItinerancyTestCase(TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.course1 = CourseFactory(name="1")
        self.course2 = CourseFactory(name="2")
        self.course3 = CourseFactory(name="3")

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
