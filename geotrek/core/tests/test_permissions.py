from django.test import TestCase
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import LineString

from mapentity.factories import UserFactory
from geotrek.core.factories import PathFactory
from geotrek.core.models import Path


class PermissionDraftPath(TestCase):

    def setUp(self):
        self.user = UserFactory.create(password='booh')

    def test_permission_view_add_path_with_draft_permission(self):
        self.client.login(username=self.user.username, password='booh')
        response = self.client.get('/path/add/')
        self.assertEqual(response.status_code, 302)
        self.user.user_permissions.add(Permission.objects.get(codename='add_draft_path'))
        self.client.login(username=self.user.username, password='booh')
        response = self.client.get('/path/add/')
        self.assertEqual(response.status_code, 200)

    def test_permission_view_add_path_without_draft_permission(self):
        self.client.login(username=self.user.username, password='booh')
        response = self.client.get('/path/add/')
        self.assertEqual(response.status_code, 302)
        self.user.user_permissions.add(Permission.objects.get(codename='add_path'))
        self.client.login(username=self.user.username, password='booh')
        response = self.client.get('/path/add/')
        self.assertEqual(response.status_code, 200)

    def test_permission_view_change_path_with_draft_permission(self):
        self.client.login(username=self.user.username, password='booh')
        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        response = self.client.get('/path/%s/' % path.pk)
        self.assertEqual(response.status_code, 302)
        self.user.user_permissions.add(Permission.objects.get(codename='change_draft_path'))
        self.client.login(username=self.user.username, password='booh')
        response = self.client.get('/path/edit/%s/' % path.pk)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('name="draft"', response.content)

    def test_permission_view_change_path_without_draft_permission(self):
        self.client.login(username=self.user.username, password='booh')
        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        response = self.client.get('/path/%s/' % path.pk)
        self.assertEqual(response.status_code, 302)
        self.user.user_permissions.add(Permission.objects.get(codename='change_path'))
        self.client.login(username=self.user.username, password='booh')
        response = self.client.get('/path/edit/%s/' % path.pk)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('name="draft"', response.content)

    def test_permission_view_change_path_with_2_permissions(self):
        self.client.login(username=self.user.username, password='booh')
        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        response = self.client.get('/path/%s/' % path.pk)
        self.assertEqual(response.status_code, 302)
        self.user.user_permissions.add(Permission.objects.get(codename='change_path'))
        self.user.user_permissions.add(Permission.objects.get(codename='change_draft_path'))
        self.client.login(username=self.user.username, password='booh')
        response = self.client.get('/path/edit/%s/' % path.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn('name="draft"', response.content)

    def test_permission_view_delete_path_with_draft_permission(self):
        self.client.login(username=self.user.username, password='booh')
        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        response = self.client.get('/path/delete/%s/' % path.pk)
        self.assertEqual(response.status_code, 302)
        self.user.user_permissions.add(Permission.objects.get(codename='delete_draft_path'))
        self.client.login(username=self.user.username, password='booh')
        response = self.client.get('/path/delete/%s/' % path.pk)
        self.assertEqual(response.status_code, 200)

    def test_permission_view_delete_path_without_draft_permission(self):
        self.client.login(username=self.user.username, password='booh')
        path = PathFactory(name="PATH_AB", geom=LineString((0, 0), (4, 0)))
        response = self.client.get('/path/delete/%s/' % path.pk)
        self.assertEqual(response.status_code, 302)
        self.user.user_permissions.add(Permission.objects.get(codename='delete_path'))
        self.user.user_permissions.add(Permission.objects.get(codename='delete_draft_path'))
        self.client.login(username=self.user.username, password='booh')
        response = self.client.post('/path/delete/%s/' % path.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Path.objects.count(), 0)
