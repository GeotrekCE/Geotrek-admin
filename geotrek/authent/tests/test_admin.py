from django.test import TestCase
from mapentity.tests.factories import SuperUserFactory
from mapentity.utils import get_internal_user

from . import factories
from .base import AuthentFixturesTest


class AdminSiteTest(AuthentFixturesTest):
    @classmethod
    def setUpTestData(cls):
        cls.admin = SuperUserFactory()
        cls.path_manager = factories.PathManagerFactory()
        cls.trek_manager = factories.TrekkingManagerFactory()

    def login(self, user):
        self.client.force_login(user)

    def test_path_manager_cannot_see_trekking_apps(self):
        self.login(self.path_manager)
        response = self.client.get("/admin/core/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/trekking/")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/admin/")
        self.assertContains(response, "Core")
        self.assertContains(response, "Maintenance")
        self.assertContains(response, "Infrastructure")
        self.assertContains(response, "Signage")
        self.assertContains(response, "Land")
        self.assertNotContains(response, "Zoning")
        self.assertNotContains(response, "Trekking")

    def test_trek_manager_cannot_see_core_apps(self):
        self.login(self.trek_manager)
        response = self.client.get("/admin/core/")
        self.assertEqual(response.status_code, 404)
        response = self.client.get("/admin/trekking/")
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/")
        self.assertContains(response, "Trekking")
        self.assertNotContains(response, "Core")
        self.assertNotContains(response, "Maintenance")
        self.assertNotContains(response, "Infrastructure")
        self.assertNotContains(response, "Signage")
        self.assertNotContains(response, "Zoning")
        self.assertNotContains(response, "Land")


class UserAdminTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory()
        cls.internal_user = get_internal_user()

    def setUp(self):
        self.client.force_login(self.user)

    def test_cant_change_internal_user(self):
        """For internal user, all fields are readonly"""
        response = self.client.get(f"/admin/auth/user/{self.internal_user.pk}/change/")
        self.assertNotContains(response, "Save")

    def test_cant_delete_internal_user(self):
        """Nobody, even superuser, can delete internal user"""
        response = self.client.post(f"/admin/auth/user/{self.internal_user.pk}/delete/")
        self.assertEqual(response.status_code, 403)

    def test_super_user_can_change_user(self):
        """Superuser can change any user else internal user"""
        response = self.client.get(f"/admin/auth/user/{self.user.pk}/change/")
        self.assertContains(response, "Save")
        self.assertContains(response, "Delete")
