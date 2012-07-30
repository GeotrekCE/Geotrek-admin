# -*- coding: utf-8 -*-
"""
    Unit tests
"""
from django.test import TestCase
from django.contrib.gis.geos import LineString

from caminae.authent.factories import UserFactory, PathManagerFactory
from caminae.authent.pyfixtures import populate_groups
from caminae.core.models import Path


class GroupTest(TestCase):
    def setUp(self):
        populate_groups() # TODO not best :/

    def test_path_manager_restricted(self):
        # TODO: use path factory
        p = Path(geom=LineString((0, 0), (1, 1)))
        p.save()
        
        # Try to edit path as user
        user = UserFactory(password="foo")
        self.assertFalse(user.profile.is_path_manager())
        success = self.client.login(username=user.username, password="foo")
        self.assertTrue(success)
        response = self.client.get(p.get_update_url())
        self.assertEqual(response.status_code, 302)
        self.client.logout()

        # Try to edit path as manager
        manager = PathManagerFactory(password="foo")
        self.assertTrue(manager.profile.is_path_manager())
        success = self.client.login(username=manager.username, password="foo")
        self.assertTrue(success)
        response = self.client.get(p.get_update_url())
        self.assertEqual(response.status_code, 200)
