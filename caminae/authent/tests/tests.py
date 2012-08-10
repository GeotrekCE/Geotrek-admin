# -*- coding: utf-8 -*-
"""
    Unit tests
"""
from django.test import TestCase
from django.test.utils import override_settings
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import gettext as _

from caminae.authent.models import UserProfile
from caminae.authent.factories import UserFactory


@override_settings(LOGIN_URL='/login/')
class LoginTestCase(TestCase):
    def test_login(self):
        response = self.client.get('/')
        _next = settings.FORCE_SCRIPT_NAME + '/'
        self.assertRedirects(response, '/login/?next=' + _next)


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = UserFactory(password=u"Bar")

    def test_profile(self):
        self.assertTrue(isinstance(self.user.profile, UserProfile))
        self.assertEqual(self.user.profile, self.user.get_profile())

        self.assertEqual(self.user.profile.structure.name, settings.DEFAULT_STRUCTURE_NAME)
        self.assertEqual(self.user.profile.language, settings.LANGUAGE_CODE)

    def test_language(self):
        success = self.client.login(username=self.user.username, password=u"Bar")
        self.assertTrue(success)
        response = self.client.get(reverse('home'))
        self.assertEqual(200, response.status_code)
        self.assertTrue(_("Logout") in response.content)

        # Change user lang
        self.assertNotEqual(settings.LANGUAGE_CODE, u"en")
        userprofile = UserProfile.objects.get(user=self.user)
        userprofile.language = u"en"
        userprofile.save()
        self.assertEqual(self.user.profile.language, u"en")
        # No effect if no logout
        response = self.client.get(reverse('home'))
        self.assertTrue(_("Logout") in response.content)

        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        self.client.login(username=self.user.username, password=u"Bar")
        response = self.client.get(reverse('home'))

        self.assertEqual(self.client.session['django_language'], u"en")
        self.assertTrue(_("Logout") in response.content)

    def test_admin(self):
        self.assertFalse(self.user.is_staff)
        success = self.client.login(username=self.user.username, password=u"Bar")
        self.assertTrue(success)
        response = self.client.get(reverse('home'))
        self.assertFalse(_("Admin") in response.content)

        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse('home'))
        self.assertTrue(_("Admin") in response.content)
