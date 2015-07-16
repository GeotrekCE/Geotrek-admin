# -*- encoding: utf-8 -*-

from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase
from django.core.urlresolvers import reverse

from mapentity.factories import UserFactory


class ViewsTest(TestCase):

    def setUp(self):
        self.user = UserFactory.create(username='homer', password='dooh')
        success = self.client.login(
            username=self.user.username, password='dooh')
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

    def test_import_form_access(self):
        url = reverse('common:import_dataset')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_import_update_access(self):
        url = reverse('common:import_update_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_import_form_file_content_type_handling(self):
        self.user.is_superuser = True
        self.user.save()

        good_archive = SimpleUploadedFile(
            "file.zip", "file_content", content_type="application/zip")
        bad_archive = SimpleUploadedFile(
            "file.doc", "file_content", content_type="application/msword")

        url = reverse('common:import_dataset')

        response = self.client.post(url, {'parser': 'CityParser', 'zipfile': good_archive})
        self.assertEqual(response.status_code, 200)

        response = self.client.post(url, {'parser': 'CityParser', 'zipfile': bad_archive})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'zipfile', ["File must be of ZIP type.", ])
        