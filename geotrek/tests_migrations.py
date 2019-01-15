from django.apps import apps
from django.test import TestCase
from django.contrib.auth.models import Permission
from django.conf import settings
from geotrek.signage.factories import SignageFactory, SignageTypeFactory
from unittest import skipIf


@skipIf(settings.TEST, "Test")
class TestMigrations(TestCase):
    def test_same_as_before_migrations(self):
        self.assertEqual([], Permission.objects.all())
