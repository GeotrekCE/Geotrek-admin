"""
    Unit tests
"""
from .base import AuthentFixturesTest

from geotrek.authent.tests.factories import StructureFactory, PathManagerFactory
from geotrek.core.tests.factories import PathFactory


class StructureRestrictionTest(AuthentFixturesTest):
    def test_structure_restricted(self):
        p = PathFactory()
        # Login
        user = PathManagerFactory(password="foo")
        success = self.client.login(username=user.username, password="foo")
        self.assertTrue(success)
        # Try to edit path from same structure
        response = self.client.get(p.get_update_url())
        self.assertEqual(response.status_code, 200)
        # Try to edit path from other structure
        p.structure = StructureFactory(name="Other")
        p.save()
        self.assertNotEqual(p.structure, user.profile.structure)
        response = self.client.get(p.get_update_url())
        self.assertEqual(response.status_code, 302)
