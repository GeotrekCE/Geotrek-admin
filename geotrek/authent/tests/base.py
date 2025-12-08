import os

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase
from mapentity.registry import registry


class AuthentFixturesMixin:
    fixtures = [
        os.path.join(settings.PROJECT_DIR, "authent", "fixtures", "minimal.json"),
        os.path.join(settings.PROJECT_DIR, "authent", "fixtures", "basic.json"),
    ]

    def _pre_setup(self):
        if not isinstance(self, TestCase):
            call_command("update_geotrek_permissions", verbosity=0)
        super()._pre_setup()

    @classmethod
    def setUpClass(cls):
        """
        Override setUpClass() of test to make sure MapEntity models are
        registered when test is setup.
        Indeed since permissions are created on model registering, and since
        models are registered in `urls.py` modules, and since `urls.py` are
        imported after test setup, importing them here allows permissions to be
        available before test `setUp()` methods.
        """

        # Workaround https://code.djangoproject.com/ticket/10827
        ContentType.objects.clear_cache()

        if not registry.registry.keys():
            from geotrek.core import urls  # NOQA
            from geotrek.land import urls  # NOQA
            from geotrek.maintenance import urls  # NOQA
            from geotrek.infrastructure import urls  # NOQA
            from geotrek.signage import urls  # NOQA
            from geotrek.trekking import urls  # NOQA
            from geotrek.tourism import urls  # NOQA

        call_command("update_geotrek_permissions", verbosity=0)

        return super().setUpClass()


class AuthentFixturesTest(AuthentFixturesMixin, TestCase):
    pass
