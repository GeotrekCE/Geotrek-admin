# -*- encoding: utf-8 -*-

from django.test import TestCase
from django.core.urlresolvers import reverse

from mapentity.factories import UserFactory


class ViewsTest(TestCase):

    def setUp(self):
        self.user = UserFactory.create(username='homer', password='dooh')
        success = self.client.login(username=self.user.username, password='dooh')
        self.assertTrue(success)

    def test_settings_json(self):
        url = reverse('common:settings_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_admin_check_extents(self):
        url = reverse('common:check_extents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
