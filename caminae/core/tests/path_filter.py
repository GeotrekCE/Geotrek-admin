from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase
from django.utils import simplejson

from caminae.authent.factories import UserProfileFactory, StructureFactory
from caminae.core.models import Path
from caminae.core.factories import PathFactory


class PathFilterTest(TestCase):

    def test_paths_bystructure(self):
        shared_structure = StructureFactory()
        not_shared_structure = StructureFactory()

        password = 'toto'
        user_profile = UserProfileFactory(structure=shared_structure, user__password='toto')
        user = user_profile.user

        path_share_structure_1 = PathFactory(structure=shared_structure, length=1)
        path_share_structure_2 = PathFactory(structure=shared_structure, length=70)
        path_other = PathFactory(structure=not_shared_structure)

        result = self.client.login(username=user.username,password=password)
        self.assertTrue(result, u"The client successfully logged in")

        response = self.client.get(reverse('core:path_list'))
        self.assertEquals(response.status_code, 200)

        def create_form_params(range_start='', range_end=''):
            """Return range form parameter as used in caminae.core.filters.PathFilter"""
            return { 'length_0': range_end, 'length_1': range_start }

        # Simulate ajax call to populate the list
        # The path returned as json should be all paths that share the user's structure
        # We check the 'map_path_pk' json attribute that should contain the paths' pk (used by map)
        response = self.client.get(reverse('core:path_ajax_list'), data=create_form_params('', ''))
        self.assertEquals(response.status_code, 200)

        json = simplejson.loads(response.content)
        self.assertListEqual(
                json['map_path_pk'],
                list(Path.in_structure.byUser(user).values_list('pk', flat=True)),
                """The JSON should only contain path filtered according to the
                structure of the user. No other filter are applied"""
        )

        # Simulate ajax call to populate the list, but this time with a range filter
        length_range = [50, 100]
        response = self.client.get(reverse('core:path_ajax_list'), data=create_form_params(*length_range))
        self.assertEquals(response.status_code, 200)

        json = simplejson.loads(response.content)
        self.assertListEqual(
                json['map_path_pk'],
                list(Path.in_structure.byUser(user)
                     .filter(length__range=length_range)
                     .values_list('pk', flat=True)),
                """The JSON should only contain path filtered according to the
                range and the structure of the user"""
        )
