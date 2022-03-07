from unittest import skipIf

from django.conf import settings
from django.urls import reverse

from geotrek.authent.tests.base import AuthentFixturesTest
from geotrek.authent.tests.factories import PathManagerFactory

from geotrek.core.tests.factories import PathFactory


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PathFilterTest(AuthentFixturesTest):

    def test_paths_bystructure(self):
        PathFactory(geom='SRID=2154;LINESTRING(0 0, 1 0)')
        PathFactory(geom='SRID=2154;LINESTRING(0 0, 70 0)')

        password = 'toto'
        user = PathManagerFactory(password=password)
        self.client.force_login(user=user)

        response = self.client.get(reverse('core:path_list'))
        self.assertEqual(response.status_code, 200)

        # def create_form_params(range_start='', range_end=''):
        #     """Return range form parameter as used in geotrek.core.filters.PathFilter"""
        #     return {'length_min': range_start, 'length_max': range_end}
        #
        # def test_response_content(length_range, queryset):
        #     response = self.client.get(reverse('core:path_json_list'), data=create_form_params(*length_range))
        #     self.assertEqual(response.status_code, 200)
        #     # We check the 'map_obj_pk' json attribute that should contain the paths' pk (used by map)
        #     jsondict = response.json()
        #     # The JSON should only contain filtered paths
        #     self.assertListEqual(
        #         sorted(jsondict['map_obj_pk']),
        #         sorted(list(queryset.values_list('pk', flat=True))),
        #     )
        #
        # # Simulate ajax call to populate the list
        # # The path returned as json should be all paths
        # test_response_content(['', ''], Path.objects.all())
        #
        # # Simulate ajax call to populate the list, but this time with a range filter
        # length_range = [50, 100]
        # test_response_content(length_range, Path.objects.filter(length__range=length_range))
