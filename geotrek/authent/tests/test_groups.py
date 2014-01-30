# -*- coding: utf-8 -*-
"""
    Unit tests
"""
from django.test import TestCase
from django.contrib.auth.models import Group

from geotrek.authent import models as auth_models
from geotrek.authent.factories import UserFactory, PathManagerFactory
from geotrek.authent.models import GROUP_PATH_MANAGER, GROUP_TREKKING_MANAGER, GROUP_EDITOR
from geotrek.core.factories import PathFactory


class GroupTest(TestCase):
    def setUp(self):
        groups = (GROUP_PATH_MANAGER, GROUP_TREKKING_MANAGER, GROUP_EDITOR)
        for group in groups:
            Group.objects.get_or_create(name=group)

    def test_path_manager_restricted(self):
        p = PathFactory()
        # Try to edit path as user
        user = UserFactory(password="foo")
        self.assertFalse(user.profile.is_path_manager)
        success = self.client.login(username=user.username, password="foo")
        self.assertTrue(success)
        response = self.client.get(p.get_update_url())
        self.assertEqual(response.status_code, 302)
        self.client.logout()

        # Try to edit path as manager
        manager = PathManagerFactory(password="foo")
        self.assertTrue(manager.profile.is_path_manager)
        success = self.client.login(username=manager.username, password="foo")
        self.assertTrue(success)
        response = self.client.get(p.get_update_url())
        self.assertEqual(response.status_code, 200)

    def test_group(self):
        groups = (Group.objects.get(name=auth_models.GROUP_EDITOR),
                  Group.objects.get(name=auth_models.GROUP_PATH_MANAGER),
                  Group.objects.get(name=auth_models.GROUP_TREKKING_MANAGER),
                 )
        user = UserFactory()
        self.assertFalse(user.profile.is_editor)
        self.assertFalse(user.profile.is_path_manager)
        self.assertFalse(user.profile.is_trekking_manager)

        user = UserFactory(groups=groups)
        self.assertTrue(user.profile.is_editor)
        self.assertTrue(user.profile.is_path_manager)
        self.assertTrue(user.profile.is_trekking_manager)
