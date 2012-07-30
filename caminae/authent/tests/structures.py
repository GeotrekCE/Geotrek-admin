# -*- coding: utf-8 -*-
"""
    Unit tests
"""
from django.test import TestCase
from django.contrib.gis.geos import LineString

from caminae.authent.models import Structure
from caminae.authent.factories import PathManagerFactory, StructureFactory
from caminae.authent.pyfixtures import populate_groups
from caminae.core.models import Path

class StructureTest(TestCase):
    def setUp(self):
        self.structure = StructureFactory()
        populate_groups() # TODO not best :/

    def test_basic(self):
        s = Structure(name=u"Mércäntour")
        self.assertEqual(unicode(s), u"Mércäntour")

    def test_structure_restricted(self):
        # TODO: use path factory
        p = Path(geom=LineString((0, 0), (1, 1)))
        p.structure = self.structure
        p.save()
        # Login
        user = PathManagerFactory(password="foo")
        self.assertTrue(user.profile.is_path_manager())
        success = self.client.login(username=user.username, password="foo")
        self.assertTrue(success)
        # Try to edit path from other structure
        self.assertNotEqual(p.structure, user.profile.structure)
        response = self.client.get(p.get_update_url())
        self.assertEqual(response.status_code, 302)
        # Try to edit path from same structure
        p.structure = user.profile.structure
        p.save()
        response = self.client.get(p.get_update_url())
        self.assertEqual(response.status_code, 200)
