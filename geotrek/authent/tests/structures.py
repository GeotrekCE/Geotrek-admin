# -*- coding: utf-8 -*-
"""
    Unit tests
"""
from django.test import TestCase

from geotrek.authent.models import Structure
from geotrek.authent.factories import PathManagerFactory, StructureFactory
from geotrek.core.factories import PathFactory
from geotrek.authent.fixtures.development import populate_groups


class StructureTest(TestCase):
    def setUp(self):
        populate_groups() # TODO not best :/

    def test_basic(self):
        s = Structure(name=u"Mércäntour")
        self.assertEqual(unicode(s), u"Mércäntour")

    def test_structure_restricted(self):
        p = PathFactory()
        # Login
        user = PathManagerFactory(password="foo")
        self.assertTrue(user.profile.is_path_manager)
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
