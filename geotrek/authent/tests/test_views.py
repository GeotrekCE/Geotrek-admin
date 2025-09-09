from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings


@override_settings(LOGIN_URL="/login/")
class LoginTestCase(TestCase):
    def test_login(self):
        response = self.client.get("/")
        _next = (settings.FORCE_SCRIPT_NAME or "") + "/"
        self.assertRedirects(response, "/login/?next=" + _next)
