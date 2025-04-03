from django.urls import reverse

from geotrek.authent.tests.base import AuthentFixturesTest

from ..models import Dive
from .factories import (
    DifficultyFactory,
    DiveFactory,
    DivingManagerFactory,
    LevelFactory,
)


class DifficultyTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = DivingManagerFactory.create()
        cls.difficulty = DifficultyFactory.create()
        cls.level = LevelFactory.create()
        cls.dive = DiveFactory.create(difficulty=cls.difficulty)
        cls.dive.levels.add(cls.level)

    def setUp(self):
        self.client.force_login(self.user)

    def get_csrf_token(self, response):
        csrf = 'name="csrfmiddlewaretoken" value="'
        start = response.content.decode().find(csrf) + len(csrf)
        end = response.content.decode().find('"', start)
        return response.content[start:end]

    def test_cant_create_duplicate_id_difficulty(self):
        response = self.client.get(reverse("admin:diving_difficulty_add"))
        csrf = self.get_csrf_token(response)
        post_data = {
            "id": self.difficulty.pk,
            "name_en": "Dur-dur",
            "csrfmiddlewaretoken": csrf,
        }

        response = self.client.post(reverse("admin:diving_difficulty_add"), post_data)
        error_msg = (
            "Difficulty with id &#x27;%s&#x27; already exists" % self.difficulty.pk
        )
        self.assertContains(response, error_msg)

    def test_migrate_dive_difficulty(self):
        self.assertEqual(self.dive.difficulty, self.difficulty)
        self.assertEqual(self.dive.difficulty_id, self.difficulty.pk)
        response = self.client.get(
            reverse("admin:diving_difficulty_change", args=[self.difficulty.pk])
        )
        csrf = self.get_csrf_token(response)
        post_data = {"id": 5, "name_en": "Dur-dur", "csrfmiddlewaretoken": csrf}
        response = self.client.post(
            reverse("admin:diving_difficulty_change", args=[self.difficulty.pk]),
            post_data,
        )
        self.assertRedirects(response, reverse("admin:diving_difficulty_changelist"))
        trek = Dive.objects.get(pk=self.dive.pk)
        self.assertNotEqual(trek.difficulty.name, self.difficulty.name)
        self.assertEqual(trek.difficulty_id, 5)

    def test_migrate_dive_difficulty_not_changing_order(self):
        self.assertEqual(self.dive.difficulty, self.difficulty)
        self.assertEqual(self.dive.difficulty_id, self.difficulty.pk)
        response = self.client.get(
            reverse("admin:diving_difficulty_change", args=[self.difficulty.pk])
        )
        csrf = self.get_csrf_token(response)
        post_data = {
            "id": self.difficulty.pk,
            "name_en": "Dur-dur",
            "csrfmiddlewaretoken": csrf,
        }
        response = self.client.post(
            reverse("admin:diving_difficulty_change", args=[self.difficulty.pk]),
            post_data,
        )
        self.assertRedirects(response, reverse("admin:diving_difficulty_changelist"))
        trek = Dive.objects.get(pk=self.dive.pk)
        self.assertNotEqual(trek.difficulty.name, self.difficulty.name)
        self.assertEqual(trek.difficulty_id, self.difficulty.pk)

    def test_cant_create_duplicate_id_level(self):
        response = self.client.get(reverse("admin:diving_level_add"))
        csrf = self.get_csrf_token(response)
        post_data = {
            "id": self.level.pk,
            "name_en": "Dur-dur",
            "csrfmiddlewaretoken": csrf,
        }

        response = self.client.post(reverse("admin:diving_level_add"), post_data)
        error_msg = "Level with id &#x27;%s&#x27; already exists" % self.level.pk
        self.assertContains(response, error_msg)

    def test_migrate_dive_level(self):
        level_2 = LevelFactory.create(name="Level 2")
        self.dive.levels.add(level_2)
        self.assertEqual(self.dive.levels.first(), self.level)
        self.assertEqual(self.dive.levels.first().id, self.level.pk)
        response = self.client.get(
            reverse("admin:diving_level_change", args=[self.level.pk])
        )
        csrf = self.get_csrf_token(response)
        post_data = {"id": 5, "name_en": "Dur-dur", "csrfmiddlewaretoken": csrf}
        response = self.client.post(
            reverse("admin:diving_level_change", args=[self.level.pk]), post_data
        )
        self.assertRedirects(response, reverse("admin:diving_level_changelist"))
        dive = Dive.objects.get(pk=self.dive.pk)
        self.assertNotIn(self.level.name, [level.name for level in dive.levels.all()])
        self.assertIn(5, [level.id for level in dive.levels.all()])

    def test_migrate_dive_level_not_changing_order(self):
        level_2 = LevelFactory.create(name="Level 2")
        self.dive.levels.add(level_2)
        self.assertEqual(self.dive.levels.first(), self.level)
        self.assertEqual(self.dive.levels.first().id, self.level.pk)
        response = self.client.get(
            reverse("admin:diving_level_change", args=[self.level.pk])
        )
        csrf = self.get_csrf_token(response)
        post_data = {
            "id": self.level.pk,
            "name_en": "Dur-dur",
            "csrfmiddlewaretoken": csrf,
        }
        response = self.client.post(
            reverse("admin:diving_level_change", args=[self.level.pk]), post_data
        )
        self.assertRedirects(response, reverse("admin:diving_level_changelist"))
        dive = Dive.objects.get(pk=self.dive.pk)
        self.assertNotIn(self.level.name, [level.name for level in dive.levels.all()])
        self.assertIn(self.level.pk, [level.id for level in dive.levels.all()])
