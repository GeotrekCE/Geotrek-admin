from django.conf import settings
from django.core.checks import Error
from django.test import TestCase

from geotrek.common.apps import CommonConfig, srid_check


class StartupCheckTest(TestCase):
    def test_error_register(self):
        with self.settings(SRID=4326):
            self.assertListEqual(
                srid_check(CommonConfig),
                [
                    Error(
                        "Unit of SRID EPSG:%s is not meter." % settings.SRID,
                        id="geotrek.E001",
                    )
                ],
            )
