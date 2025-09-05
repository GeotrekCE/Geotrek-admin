from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from mapentity.tests.factories import UserFactory


@override_settings(LOGIN_URL="/login/")
class LoginTestCase(TestCase):
    def test_login(self):
        response = self.client.get("/")
        _next = (settings.FORCE_SCRIPT_NAME or "") + "/"
        self.assertRedirects(response, "/login/?next=" + _next)


class UserProfileTest(TestCase):
    def test_link_to_admin_site_visible_to_staff(self):
        user_staff = UserFactory(is_staff=True)
        self.client.force_login(user_staff)
        response = self.client.get("/")
        self.assertContains(response, '<a class="dropdown-item" href="/admin/">')

    def test_link_to_admin_site_not_visible_to_others(self):
        user = UserFactory()
        self.client.force_login(user)
        response = self.client.get(reverse("core:path_list"))
        self.assertNotContains(response, 'href="/admin/"')
