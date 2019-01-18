from django.apps import apps
from django.test import TestCase
from django.contrib.auth.models import Permission
from django.conf import settings
from geotrek.signage.factories import SignageFactory, SignageTypeFactory
from unittest import skipIf

from django.db.migrations.recorder import MigrationRecorder

migrations = []
for app in apps.get_models():
    migrations.append(MigrationRecorder.Migration.objects.all())
print(migrations)


@skipIf(settings.TEST, "Test")
class TestMigrations(TestCase):
    def test_same_as_before_migrations(self):

        self.assertEqual([], Permission.objects.all())
