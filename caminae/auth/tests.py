from django.test import TestCase
from django.contrib.auth.models import User

from models import Structure, UserProfile


class StructureTest(TestCase):
    def test_basic(self):
        s = Structure(name="Mercantour")
        self.assertEqual(unicode(s), "Mercantour")


class UserProfileTest(TestCase):
    def test_profile(self):
        u = User(username="Joe", password="Bar")
        u.save()
        self.assertTrue(isinstance(u.profile, UserProfile))
