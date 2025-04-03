from django.contrib.admin import AdminSite
from django.test import TestCase
from django.urls import reverse

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import TrekkingManagerFactory

from ..admin import RatingAdmin
from ..models import Rating, Trek
from .factories import DifficultyLevelFactory, RatingFactory, TrekFactory


class DifficultyLevelTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = TrekkingManagerFactory.create()
        cls.difficulty = DifficultyLevelFactory.create()
        cls.trek = TrekFactory.create(difficulty=cls.difficulty)

    def setUp(self):
        self.client.force_login(self.user)

    def get_csrf_token(self, response):
        csrf = 'name="csrfmiddlewaretoken" value="'
        start = response.content.decode().find(csrf) + len(csrf)
        end = response.content.decode().find('"', start)
        return response.content[start:end]

    def test_cant_create_duplicate_id(self):
        response = self.client.get(reverse("admin:trekking_difficultylevel_add"))
        csrf = self.get_csrf_token(response)
        post_data = {
            "id": self.difficulty.pk,
            "difficulty_fr": "Dur-dur",
            "csrfmiddlewaretoken": csrf,
        }

        response = self.client.post(
            reverse("admin:trekking_difficultylevel_add"), post_data
        )
        error_msg = (
            "Difficulty with id &#x27;%s&#x27; already exists" % self.difficulty.pk
        )
        self.assertContains(response, error_msg)

    def test_migrate_trek_difficulty(self):
        self.assertEqual(self.trek.difficulty, self.difficulty)
        self.assertEqual(self.trek.difficulty_id, self.difficulty.pk)
        response = self.client.get(
            reverse("admin:trekking_difficultylevel_change", args=[self.difficulty.pk])
        )
        csrf = self.get_csrf_token(response)
        post_data = {"id": 4, "difficulty_en": "Dur-dur", "csrfmiddlewaretoken": csrf}
        response = self.client.post(
            reverse("admin:trekking_difficultylevel_change", args=[self.difficulty.pk]),
            post_data,
        )
        self.assertRedirects(
            response, reverse("admin:trekking_difficultylevel_changelist")
        )
        trek = Trek.objects.get(pk=self.trek.pk)
        self.assertNotEqual(trek.difficulty, self.difficulty)
        self.assertEqual(trek.difficulty_id, 4)


class DeleteObjectTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = TrekkingManagerFactory.create()
        cls.difficulty = DifficultyLevelFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_weblink_can_be_deleted(self):
        delete_url = reverse(
            "admin:trekking_difficultylevel_delete", args=[self.difficulty.pk]
        )
        detail_url = reverse(
            "admin:trekking_difficultylevel_change", args=[self.difficulty.pk]
        )
        response = self.client.post(delete_url, {"post": "yes"})
        self.assertEqual(response.status_code, 302)
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/admin/")


class RatingAdminTest(TestCase):
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
