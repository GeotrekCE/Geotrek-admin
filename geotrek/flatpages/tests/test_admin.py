from django.test import TestCase

from mapentity.tests.factories import SuperUserFactory

from geotrek.flatpages.factories import FlatPageFactory


class AdminSiteTest(TestCase):
    def login(self):
        user = SuperUserFactory(password='booh')
        success = self.client.login(username=user.username, password='booh')
        self.assertTrue(success)

    def test_flatpages_are_registered(self):
        self.login()
        response = self.client.get('/admin/flatpages/flatpage/')
        self.assertEqual(response.status_code, 200)

    def test_flatpages_are_translatable(self):
        self.login()
        response = self.client.get('/admin/flatpages/flatpage/add/')
        self.assertContains(response, 'published_en')

    def test_flatpages_are_updatable(self):
        self.login()
        page = FlatPageFactory(content="One looove")
        response = self.client.get('/admin/flatpages/flatpage/{0}/change/'.format(page.pk))
        self.assertContains(response, "One looove")
