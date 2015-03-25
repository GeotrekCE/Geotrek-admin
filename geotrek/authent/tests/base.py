import os

from django.test import TestCase
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command

from mapentity import registry


class AuthentFixturesTest(TestCase):
    fixtures = [os.path.join(settings.PROJECT_ROOT_PATH, 'authent', 'fixtures', 'minimal.json'),
                os.path.join(settings.PROJECT_ROOT_PATH, 'authent', 'fixtures', 'basic.json')]

    def _pre_setup(self):
        """
        Override _pre_setup() of test to make sure MapEntity models are
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
            from geotrek.trekking import urls  # NOQA
            from geotrek.tourism import urls  # NOQA

        call_command('update_permissions')

        return super(AuthentFixturesTest, self)._pre_setup()
