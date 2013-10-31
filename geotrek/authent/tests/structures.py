# -*- coding: utf-8 -*-
"""
    Unit tests
"""
from django.test import TestCase
from django.contrib.auth.models import Group

from geotrek.authent.models import Structure
from geotrek.authent.factories import PathManagerFactory, StructureFactory
from geotrek.core.factories import PathFactory
from geotrek.authent.models import GROUP_PATH_MANAGER, GROUP_TREKKING_MANAGER, GROUP_EDITOR


class StructureTest(TestCase):
    def setUp(self):
        groups = (GROUP_PATH_MANAGER, GROUP_TREKKING_MANAGER, GROUP_EDITOR)
        for group in groups:
            Group.objects.get_or_create(name=group)

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
