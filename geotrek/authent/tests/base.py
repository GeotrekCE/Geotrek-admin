import os

from django.test import TestCase
from django.conf import settings


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
        from geotrek.core import urls
        from geotrek.land import urls
        from geotrek.maintenance import urls
        from geotrek.infrastructure import urls
        from geotrek.trekking import urls
        from geotrek.tourism import urls

        return super(AuthentFixturesTest, self)._pre_setup()
