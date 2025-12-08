from django.contrib.admin import AdminSite
from django.test import TestCase

from geotrek.outdoor.admin import RatingAdmin
from geotrek.outdoor.models import Rating
from geotrek.outdoor.tests.factories import RatingFactory


class AdminTest(TestCase):
    def test_color_markup(self):
        rating = RatingFactory(color="#AC2F89")
        admin = RatingAdmin(Rating, AdminSite())
        self.assertEqual(
            admin.color_markup(rating), '<span style="color: #AC2F89;">⬤</span> #AC2F89'
        )

    def test_no_color_markup(self):
        rating = RatingFactory(color="")
        admin = RatingAdmin(Rating, AdminSite())
        self.assertEqual(admin.color_markup(rating), "")
