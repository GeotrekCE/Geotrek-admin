# -*- coding: utf-8 -*-
"""
    Unit tests
"""
from django.test import TestCase
from django.contrib.gis.geos import LineString
from django.contrib.auth.models import Group

from caminae.authent import models as auth_models
from caminae.authent.factories import UserFactory, PathManagerFactory
from caminae.authent.fixtures.development import populate_groups
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

    def test_group(self):
        groups = (Group.objects.get(name=auth_models.GROUP_ADMINISTRATOR),
                  Group.objects.get(name=auth_models.GROUP_EDITOR),
                  Group.objects.get(name=auth_models.GROUP_PATH_MANAGER),
                  Group.objects.get(name=auth_models.GROUP_COMM_MANAGER),
                 )
        user = UserFactory()
        self.assertFalse(user.profile.is_administrator())
        self.assertFalse(user.profile.is_editor())
        self.assertFalse(user.profile.is_path_manager())
        self.assertFalse(user.profile.is_comm_manager())
        
        user = UserFactory(groups=groups)
        self.assertTrue(user.profile.is_administrator())
        self.assertTrue(user.profile.is_editor())
        self.assertTrue(user.profile.is_path_manager())
        self.assertTrue(user.profile.is_comm_manager())
