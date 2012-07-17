# -*- coding: utf8 -*-

from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse

from models import Structure, UserProfile


@override_settings(LOGIN_URL='/login/')
class LoginTestCase(TestCase):

    def test_login(self):
        response = self.client.get('/')
        _next = settings.FORCE_SCRIPT_NAME + '/'
        self.assertRedirects(response, '/login/?next=' + _next)


class StructureTest(TestCase):
    def test_basic(self):
        s = Structure(name="Mercantour")
        self.assertEqual(unicode(s), "Mercantour")


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
        success = c.login(username="Joe", password="Bar")
        self.assertTrue(success)
        response = c.get(reverse('home'))
        self.assertEqual(200, response.status_code)
        self.assertTrue("déconnecter" in response.content)
        
        # Change user lang
        self.user.profile.language = "en"
        self.assertEqual(settings.LANGUAGE_CODE, self.user.profile.language)
        self.user.profile.save()
        # No effect if no logout
        response = c.get(reverse('home'))
        self.assertTrue("déconnecter" in response.content)
        
        c.logout()
        response = c.get(reverse('home'))
        self.assertEqual(response.status_code, 302)
        
        c.login(username="Joe", password="Bar")
        response = c.get(reverse('home'))
        self.assertEqual(c.session['django_language'], self.user.profile.language)
        self.assertFalse("déconnecter" in response.content)
