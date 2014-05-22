# -*- coding: utf-8 -*-
"""
    Unit tests
"""
from .base import AuthentFixturesTest

from geotrek.authent.factories import StructureFactory, PathManagerFactory
from geotrek.core.factories import PathFactory


class StructureTest(AuthentFixturesTest):

    def test_basic(self):
        s = StructureFactory(name=u"Mércäntour")
        self.assertEqual(unicode(s), u"Mércäntour")

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
