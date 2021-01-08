from django.test import TestCase
from geotrek.authent.factories import UserFactory
from geotrek.outdoor.factories import SiteFactory, RatingFactory
from geotrek.outdoor.forms import SiteForm


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
