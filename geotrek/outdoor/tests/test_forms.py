from django.test import TestCase
from geotrek.authent.factories import UserFactory
from geotrek.outdoor.factories import SiteFactory, RatingFactory, CourseFactory
from geotrek.outdoor.forms import SiteForm, CourseForm


class SiteFormTest(TestCase):
    def test_ratings_save(self):
        user = UserFactory()
        rating = RatingFactory()
        site = SiteFactory(practice=rating.scale.practice)
        form = SiteForm(user=user, instance=site, data={
            'name_en': 'Site',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'practice': str(rating.scale.practice.pk),
            'rating_scale_min{}'.format(rating.scale.pk): str(rating.pk),
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerysetEqual(site.ratings_min.all(), ['<Rating: Rating>'])
        self.assertQuerysetEqual(site.ratings_max.all(), [])


class CourseFormTest(TestCase):
    def test_ratings_save(self):
        user = UserFactory()
        rating = RatingFactory()
        course = CourseFactory(site__practice=rating.scale.practice)
        form = CourseForm(user=user, instance=course, data={
            'name_en': 'Course',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'site': str(course.site.pk),
            'rating_scale_{}'.format(rating.scale.pk): str(rating.pk),
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerysetEqual(course.ratings.all(), ['<Rating: Rating>'])
