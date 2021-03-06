from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase


class StartupCheckTest(TestCase):
    def test_error_is_raised_if_srid_is_not_meters(self):
        with self.settings(SRID=4326):
            self.assertRaises(ImproperlyConfigured)
