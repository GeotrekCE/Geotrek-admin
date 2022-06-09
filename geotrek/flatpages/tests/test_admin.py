from django.test import TestCase

from geotrek.flatpages.tests.factories import FlatPageFactory
from mapentity.tests.factories import SuperUserFactory


class AdminSiteTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = SuperUserFactory.create()

    def setUp(self):
        self.client.force_login(self.user)

    def test_flatpages_are_registered(self):
        response = self.client.get('/admin/flatpages/flatpage/')
        self.assertEqual(response.status_code, 200)

    def test_flatpages_are_translatable(self):
        response = self.client.get('/admin/flatpages/flatpage/add/')
        self.assertContains(response, 'published_en')

    def test_flatpages_are_updatable(self):
        page = FlatPageFactory(content="One looove")
        response = self.client.get('/admin/flatpages/flatpage/{0}/change/'.format(page.pk))
        self.assertContains(response, "One looove")
