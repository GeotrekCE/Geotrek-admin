import json

from django.core.urlresolvers import reverse

from geotrek.authent.tests import AuthentFixturesTest
from geotrek.authent.factories import PathManagerFactory

from geotrek.core.models import Path
from geotrek.core.factories import PathFactory


class PathFilterTest(AuthentFixturesTest):

    def test_paths_bystructure(self):
        PathFactory(length=1)
        PathFactory(length=70)

        password = 'toto'
        user = PathManagerFactory(password=password)
        result = self.client.login(username=user.username, password=password)
        self.assertTrue(result, u"The client successfully logged in")

        response = self.client.get(reverse('core:path_list'))
        self.assertEquals(response.status_code, 200)

        def create_form_params(range_start='', range_end=''):
            """Return range form parameter as used in geotrek.core.filters.PathFilter"""
            return {'length_0': range_end, 'length_1': range_start}

        def test_response_content(length_range, queryset):
            response = self.client.get(reverse('core:path_json_list'), data=create_form_params(*length_range))
            self.assertEquals(response.status_code, 200)
            # We check the 'map_obj_pk' json attribute that should contain the paths' pk (used by map)
            jsondict = json.loads(response.content)
            # The JSON should only contain filtered paths
            self.assertListEqual(
                sorted(jsondict['map_obj_pk']),
                sorted(list(queryset.values_list('pk', flat=True))),
            )

        # Simulate ajax call to populate the list
        # The path returned as json should be all paths
        test_response_content(['', ''], Path.objects.all())

        # Simulate ajax call to populate the list, but this time with a range filter
        length_range = [50, 100]
        test_response_content(length_range, Path.objects.filter(length__range=length_range))
