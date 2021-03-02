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
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.rating = RatingFactory()
        cls.course = CourseFactory(site__practice=cls.rating.scale.practice)

    def test_rating_save(self):
        form = CourseForm(user=self.user, instance=self.course, data={
            'name_en': 'Course',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'site': str(self.course.site.pk),
            'rating_scale_{}'.format(self.rating.scale.pk): str(self.rating.pk),
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerysetEqual(self.course.ratings.all(), ['<Rating: Rating>'])

    def test_no_rating_save(self):
        form = CourseForm(user=self.user, instance=self.course, data={
            'name_en': 'Course',
            'geom': '{"type": "GeometryCollection", "geometries": [{"type": "Point", "coordinates": [3, 45]}]}',
            'site': str(self.course.site.pk),
        })
        self.assertTrue(form.is_valid())
        form.save()
        self.assertQuerysetEqual(self.course.ratings.all(), [])
