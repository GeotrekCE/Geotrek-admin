from unittest import skipIf

from django.conf import settings
from django.urls import reverse

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import PathManagerFactory
from geotrek.core.tests.factories import PathFactory


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class PathFilterTest(AuthentFixturesTest):
    def test_paths_bystructure(self):
        PathFactory(geom="SRID=2154;LINESTRING(0 0, 1 0)")
        PathFactory(geom="SRID=2154;LINESTRING(0 0, 70 0)")

        user = PathManagerFactory()
        self.client.force_login(user=user)

        response = self.client.get(reverse("core:path_list"))
        self.assertEqual(response.status_code, 200)
