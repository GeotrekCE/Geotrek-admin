from django.test import TestCase

from .. import factories


class AdminSiteTest(TestCase):
    def setUp(self):
        self.admin = factories.SuperUserFactory.create(password='booh')
        self.pathmanager = factories.PathManagerFactory.create(password='booh')
        self.trekmanager = factories.TrekkingManagerFactory.create(password='booh')
        self.user = factories.UserFactory.create(password='booh')

    def tearDown(self):
        self.admin.delete()
        self.pathmanager.delete()
        self.trekmanager.delete()
        self.user.delete()
        self.client.logout()

    def login(self, user):
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

    def test_user_cant_access(self):
        self.login(self.user)
        response = self.client.get('/admin/')
        self.assertContains(response, 'Log in | Django site admin')

    def test_admin_can_see_everything(self):
        self.login(self.admin)
        response = self.client.get('/admin/core/')
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/admin/trekking/')
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/admin/')
        self.assertContains(response, 'Core')
        self.assertContains(response, 'Land')
        self.assertContains(response, 'Trekking')

    def test_path_manager_cannot_see_trekking(self):
        self.login(self.pathmanager)
        response = self.client.get('/admin/core/')
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/admin/trekking/')
        self.assertEquals(response.status_code, 404)
        response = self.client.get('/admin/')
        self.assertContains(response, 'Core')
        self.assertContains(response, 'Maintenance')
        self.assertContains(response, 'Infrastructure')
        self.assertNotContains(response, 'Land')
        self.assertNotContains(response, 'Trekking')

    def test_trek_manager_cannot_see_core(self):
        self.login(self.trekmanager)
        response = self.client.get('/admin/core/')
        self.assertEquals(response.status_code, 404)
        response = self.client.get('/admin/trekking/')
        self.assertEquals(response.status_code, 200)
        response = self.client.get('/admin/')
        self.assertNotContains(response, 'Core')
        self.assertNotContains(response, 'Maintenance')
        self.assertNotContains(response, 'Infrastructure')
        self.assertNotContains(response, 'Land')
        self.assertContains(response, 'Trekking')
