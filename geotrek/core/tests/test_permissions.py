from unittest import skipIf

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import LineString
from django.test import TestCase
from django.urls import reverse
from mapentity.tests.factories import UserFactory

from geotrek.core.models import Path
from geotrek.core.tests.factories import ComfortFactory, PathFactory


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, "Test with dynamic segmentation only")
class PermissionDraftPath(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.comfort = ComfortFactory.create()

    def get_good_data(self):
        return {
            "name": "",
            "stake": "",
            "comfort": self.comfort.pk,
            "trail": "",
            "comments": "",
            "departure": "",
            "arrival": "",
            "source": "",
            "valid": "on",
            "geom": '{"geom": "LINESTRING (99.0 89.0, 100.0 88.0)", "snap": [null, null]}',
        }

    def test_permission_view_add_path_with_draft_permission(self):
        """Check draft checkbox visible if user have add_draft_path permission"""
        user = UserFactory.create()
        user.user_permissions.add(Permission.objects.get(codename="add_path"))
        user.user_permissions.add(Permission.objects.get(codename="add_draft_path"))

        self.client.force_login(user=user)

        response = self.client.get("/path/add/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="draft"')

    def test_permission_view_add_path_without_draft_permission(self):
        """Check draft checkbox not visible if user have only add_path permission"""
        user = UserFactory.create()

        user.user_permissions.add(Permission.objects.get(codename="add_path"))

        self.client.force_login(user=user)
        response = self.client.get("/path/add/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="draft"')

    def test_permission_view_add_path_with_2_permissions(self):
        """
        Check draft checkbox visible if user have 2 permissions : add_path, add_draft_path
        """
        user = UserFactory.create()

        user.user_permissions.add(Permission.objects.get(codename="add_path"))
        user.user_permissions.add(Permission.objects.get(codename="add_draft_path"))
        self.client.force_login(user=user)

        response = self.client.get("/path/add/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="draft"')

    def test_permission_view_change_path_with_draft_permission(self):
        """
        Check user can edit a draft path if user has change_draft_path permission only
        but can not edit normal path
        Check draft checkbox not visible if user have only change_draft_path
        """
        user = UserFactory.create()
        self.client.force_login(user=user)

        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        draft_path = PathFactory(
            name="PATH_AB", geom=LineString((0, 0), (4, 0)), draft=True
        )

        response = self.client.get(f"/path/edit/{path.pk}/")
        self.assertEqual(response.status_code, 302)

        response = self.client.get(f"/path/edit/{draft_path.pk}/")
        self.assertEqual(response.status_code, 302)

        user.user_permissions.add(Permission.objects.get(codename="change_draft_path"))
        self.client.force_login(user=user)

        response = self.client.post(f"/path/edit/{path.pk}/")
        self.assertEqual(response.status_code, 302)

        response = self.client.get(f"/path/edit/{draft_path.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="draft"')

    def test_permission_view_change_path_without_draft_permission(self):
        """
        Check user can not edit a draft path if user has change_path permission only
        but can edit normal path
        Check draft checkbox not visible if user have only change_path
        """
        user = UserFactory.create()
        self.client.force_login(user=user)

        path = PathFactory(name="path", geom=LineString((0, 0), (4, 0)))
        draft_path = PathFactory(
            name="draft_path", geom=LineString((0, 0), (4, 0)), draft=True
        )

        response = self.client.get(f"/path/edit/{path.pk}/")
        self.assertEqual(response.status_code, 302)

        response = self.client.get(f"/path/edit/{draft_path.pk}/")
        self.assertEqual(response.status_code, 302)

        user.user_permissions.add(Permission.objects.get(codename="change_path"))
        self.client.force_login(user=user)

        response = self.client.get(f"/path/edit/{path.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="draft"')

        response = self.client.get(f"/path/edit/{draft_path.pk}/")
        self.assertEqual(response.status_code, 302)

    def test_permission_view_change_path_with_2_permissions(self):
        """
        Check draft checkbox visible if user have 2 permissions : change_path, change_draft_path
        """
        user = UserFactory.create()
        self.client.force_login(user=user)

        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        draft_path = PathFactory(
            name="draft_path", geom=LineString((0, 0), (4, 0)), draft=True
        )

        response = self.client.get(f"/path/edit/{path.pk}/")
        self.assertEqual(response.status_code, 302)

        response = self.client.get(f"/path/edit/{draft_path.pk}/")
        self.assertEqual(response.status_code, 302)

        user.user_permissions.add(Permission.objects.get(codename="change_path"))
        user.user_permissions.add(Permission.objects.get(codename="change_draft_path"))
        self.client.force_login(user=user)

        response = self.client.get(f"/path/edit/{path.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="draft"')

        response = self.client.get(f"/path/edit/{draft_path.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="draft"')

    def test_permission_view_delete_path_with_draft_permission(self):
        """
        Check user can not delete a normal path if user has delete_draft_path permission
        but can delete draft path
        """
        user = UserFactory.create()
        self.client.force_login(user=user)

        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        draft_path = PathFactory(
            name="PATH_BC", geom=LineString((0, 2), (4, 2)), draft=True
        )

        response = self.client.post(f"/path/delete/{path.pk}/")
        self.assertEqual(response.status_code, 302)

        response = self.client.post(f"/path/delete/{draft_path.pk}/")
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 2)

        user.user_permissions.add(Permission.objects.get(codename="delete_draft_path"))
        self.client.force_login(user=user)

        response = self.client.post(f"/path/delete/{path.pk}/")
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 2)

        response = self.client.post(f"/path/delete/{draft_path.pk}/")
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 1)

    def test_permission_view_delete_path_without_draft_permission(self):
        """
        Check user can delete a normal path and can not delete a draft path if user has :
        only delete_path permission
        """
        user = UserFactory.create()
        self.client.force_login(user=user)

        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        draft_path = PathFactory(
            name="PATH_BC", geom=LineString((0, 2), (4, 2)), draft=True
        )

        response = self.client.post(f"/path/delete/{path.pk}/")
        self.assertEqual(response.status_code, 302)

        response = self.client.post(f"/path/delete/{draft_path.pk}/")
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 2)

        user.user_permissions.add(Permission.objects.get(codename="delete_path"))
        self.client.force_login(user=user)

        response = self.client.post(f"/path/delete/{draft_path.pk}/")
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 2)

        response = self.client.post(f"/path/delete/{path.pk}/")
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 1)

    def test_permission_view_delete_path_with_2_permissions(self):
        """
        Check user can delete a normal path and draft path if user has :
        delete_draft_path permission and delete_path
        """
        user = UserFactory.create()
        self.client.force_login(user=user)

        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        draft_path = PathFactory(
            name="PATH_BC", geom=LineString((0, 2), (4, 2)), draft=True
        )

        response = self.client.post(f"/path/delete/{path.pk}/")
        self.assertEqual(response.status_code, 302)

        response = self.client.post(f"/path/delete/{draft_path.pk}/")
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 2)

        user.user_permissions.add(Permission.objects.get(codename="delete_path"))
        user.user_permissions.add(Permission.objects.get(codename="delete_draft_path"))

        self.client.force_login(user=user)

        response = self.client.post(f"/path/delete/{path.pk}/")
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 1)

        response = self.client.post(f"/path/delete/{draft_path.pk}/")
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 0)

    def test_delete_multiple_path_draft_withtout_perm(self):
        user = UserFactory.create()
        self.client.force_login(user=user)
        path = PathFactory.create(name="path_1", geom=LineString((0, 0), (4, 0)))
        draft_path = PathFactory.create(
            name="path_2", geom=LineString((2, 2), (2, -2)), draft=True
        )

        response = self.client.post(
            reverse("core:multiple_path_delete", args=[f"{path.pk},{draft_path.pk}"])
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 2)

        user.user_permissions.add(Permission.objects.get(codename="delete_path"))

        response = self.client.post(
            reverse("core:multiple_path_delete", args=[f"{path.pk},{draft_path.pk}"])
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 2)

        user.user_permissions.add(Permission.objects.get(codename="delete_draft_path"))
        self.client.force_login(user=user)

        response = self.client.post(
            reverse("core:multiple_path_delete", args=[f"{path.pk},{draft_path.pk}"])
        )
        self.assertEqual(response.status_code, 302)

        self.assertEqual(Path.objects.count(), 0)

    def test_save_path_with_only_add_draft_path(self):
        """Check save path without permission add_path save with draft=True"""
        user = UserFactory.create()
        user.user_permissions.add(Permission.objects.get(codename="add_draft_path"))

        self.client.force_login(user=user)

        response = self.client.post("/path/add/", self.get_good_data())

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Path.objects.first().draft)

    def test_save_path_with_only_edit_draft_path(self):
        """
        Check save path without permission change_path save with draft=True
        """
        draft_path = PathFactory(
            name="draft", geom=LineString((0, 2), (4, 2)), draft=True
        )
        path = PathFactory(name="normal", geom=LineString((0, 2), (4, 2)))
        user = UserFactory.create()
        user.user_permissions.add(Permission.objects.get(codename="change_draft_path"))

        self.client.force_login(user=user)

        data = self.get_good_data()
        response = self.client.post(f"/path/edit/{draft_path.pk}/", data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Path.objects.get(pk=draft_path.pk).draft)

        response = self.client.post(f"/path/edit/{path.pk}/", data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Path.objects.get(pk=path.pk).draft)

    def test_save_path_with_only_add_path(self):
        """
        Check save path without permission add_draft_path save with draft=False
        """
        user = UserFactory.create()
        user.user_permissions.add(Permission.objects.get(codename="add_path"))

        self.client.force_login(user=user)

        response = self.client.post("/path/add/", self.get_good_data())
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Path.objects.first().draft)

    def test_save_path_with_only_edit_path(self):
        """
        Check save path without permission change_draft_path save with draft=False
        """
        path = PathFactory(name="path", geom=LineString((0, 2), (4, 2)))
        draft_path = PathFactory(
            name="draft", geom=LineString((0, 2), (4, 2)), draft=True
        )
        user = UserFactory.create()
        user.user_permissions.add(Permission.objects.get(codename="change_path"))
        self.client.force_login(user=user)

        data = self.get_good_data()
        response = self.client.post(f"/path/edit/{path.pk}/", data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Path.objects.first().draft)

        response = self.client.post(f"/path/edit/{draft_path.pk}/", data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Path.objects.get(pk=draft_path.pk).draft)

    def test_save_path_with_edit_draft_path_and_edit_path(self):
        """
        Check save path without permission change_path save with draft=True
        """
        draft_path = PathFactory(
            name="draft", geom=LineString((0, 2), (4, 2)), draft=True
        )
        user = UserFactory.create()
        user.user_permissions.add(Permission.objects.get(codename="change_path"))
        user.user_permissions.add(Permission.objects.get(codename="change_draft_path"))
        self.client.force_login(user=user)

        data = self.get_good_data()
        data["draft"] = True
        response = self.client.post(f"/path/edit/{draft_path.pk}/", data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Path.objects.get(pk=draft_path.pk).draft)

        # You can change a draft path to a normal path.
        data["draft"] = False
        response = self.client.post(f"/path/edit/{draft_path.pk}/", data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Path.objects.get(pk=draft_path.pk).draft)

        # You can't change a normal path back to a draft path.
        data["draft"] = True
        response = self.client.post(f"/path/edit/{draft_path.pk}/", data)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Path.objects.get(pk=draft_path.pk).draft)
