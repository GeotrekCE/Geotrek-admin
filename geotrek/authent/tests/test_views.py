"""
Unit tests
"""

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory


@override_settings(LOGIN_URL="/login/")
class LoginTestCase(TestCase):
    def test_login(self):
        response = self.client.get("/")
        _next = (settings.FORCE_SCRIPT_NAME or "") + "/"
        self.assertRedirects(response, "/login/?next=" + _next)


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = SuperUserFactory(password="Bar")
        success = self.client.login(username=self.user.username, password="Bar")
        self.assertTrue(success)

    def test_link_to_adminsite_visible_to_staff(self):
        self.assertTrue(self.user.is_staff)
        response = self.client.get(reverse("core:path_list"))
        self.assertContains(response, '<a href="/admin/">Admin</a>')

    def test_link_to_adminsite_not_visible_to_others(self):
        self.user.is_staff = False
        self.user.save()
        self.client.login(username=self.user.username, password="Bar")
        response = self.client.get(reverse("core:path_list"))
        self.assertNotContains(response, '<a href="/admin/">Admin</a>')
