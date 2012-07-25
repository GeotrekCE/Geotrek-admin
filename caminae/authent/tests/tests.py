# -*- coding: utf-8 -*-
"""
    Unit tests
"""
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import gettext as _

from ..models import Structure, UserProfile


@override_settings(LOGIN_URL='/login/')
class LoginTestCase(TestCase):
    def test_login(self):
        response = self.client.get('/')
        _next = settings.FORCE_SCRIPT_NAME + '/'
        self.assertRedirects(response, '/login/?next=' + _next)


class StructureTest(TestCase):
    def test_basic(self):
        s = Structure(name=u"Mercantour")
        self.assertEqual(unicode(s), u"Mercantour")


class UserProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('Joe', email='temporary@yopmail.com', password='Bar')
        self.user.set_password('Bar')
        self.user.save()

    def test_profile(self):
        self.assertTrue(isinstance(self.user.profile, UserProfile))
        self.assertEqual(self.user.profile.structure.name, settings.DEFAULT_STRUCTURE_NAME)
        self.assertEqual(self.user.profile.language, settings.LANGUAGE_CODE)
        
    def test_language(self):
        c = Client()
        success = c.login(username=u"Joe", password=u"Bar")
        self.assertTrue(success)
        response = c.get(reverse('home'))
        self.assertEqual(200, response.status_code)
        self.assertTrue(_("Logout") in response.content)
        
        # Change user lang
        self.assertNotEqual(settings.LANGUAGE_CODE, u"en")
        userprofile = UserProfile.objects.get(user=self.user)
        userprofile.language = u"en"
        userprofile.save()
        self.assertEqual(self.user.profile.language, u"en")
        # No effect if no logout
        response = c.get(reverse('home'))
        self.assertTrue(_("Logout") in response.content)
        
        c.logout()
        response = c.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        c.login(username=u"Joe", password=u"Bar")
        response = c.get(reverse('home'))

        self.assertEqual(c.session['django_language'], u"en")
        self.assertTrue(_("Logout") in response.content)

    def test_admin(self):
        self.assertFalse(self.user.is_staff)
        c = Client()
        success = c.login(username=u"Joe", password=u"Bar")
        self.assertTrue(success)
        
        response = c.get(reverse('home'))
        
        self.assertFalse(_("Admin") in response.content)
        
        self.user.is_staff = True
        self.user.save()
        response = c.get(reverse('home'))
        self.assertTrue(_("Admin") in response.content)
