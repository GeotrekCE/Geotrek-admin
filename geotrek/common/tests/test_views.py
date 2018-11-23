# -*- encoding: utf-8 -*-

from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase
from django.core.urlresolvers import reverse

from mapentity.factories import UserFactory
from geotrek.common.parsers import Parser


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


class ViewsImportTest(TestCase):

    def setUp(self):
        self.user = UserFactory.create(username='homer', password='dooh')
        success = self.client.login(username=self.user.username, password='dooh')
        self.assertTrue(success)

    def test_import_form_access(self):
        url = reverse('common:import_dataset')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_import_update_access(self):
        url = reverse('common:import_update_json')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_import_from_file_good_file(self):
        self.user.is_superuser = True
        self.user.save()

        real_archive = open('geotrek/common/tests/data/test.zip', 'rb+')
        url = reverse('common:import_dataset')

        response_real = self.client.post(
            url, {
                'upload-file': 'Upload',
                'with-file-parser': '1',
                'with-file-zipfile': real_archive,
                'with-file-encoding': 'UTF-8'
            }
        )
        self.assertEqual(response_real.status_code, 200)
        self.assertNotContains(response_real, "File must be of ZIP type.")

    def test_import_from_file_bad_file(self):
        self.user.is_superuser = True
        self.user.save()

        Parser.label = "Test"

        fake_archive = SimpleUploadedFile(
            "file.doc", b"file_content", content_type="application/msword")
        url = reverse('common:import_dataset')

        response_fake = self.client.post(
            url, {
                'upload-file': 'Upload',
                'with-file-parser': '1',
                'with-file-zipfile': fake_archive,
                'with-file-encoding': 'UTF-8'
            }
        )
        self.assertEqual(response_fake.status_code, 200)
        self.assertContains(response_fake, "File must be of ZIP type.", 1)

        Parser.label = None

    def test_import_form_no_parser_no_superuser(self):
        self.user.is_superuser = False
        self.user.save()

        real_archive = open('geotrek/common/tests/data/test.zip', 'rb')
        url = reverse('common:import_dataset')

        response_real = self.client.post(
            url, {
                'upload-file': 'Upload',
                'with-file-parser': '1',
                'with-file-zipfile': real_archive,
                'with-file-encoding': 'UTF-8'
            }
        )
        self.assertEqual(response_real.status_code, 200)
        self.assertNotContains(response_real, '<form  method="post"')

    def test_import_from_web(self):
        self.user.is_superuser = True
        self.user.save()

        url = reverse('common:import_dataset')

        response_real = self.client.post(
            url, {
                'import-web': 'Upload',
                'without-file-parser': '13',
            }
        )
        self.assertEqual(response_real.status_code, 200)
        # There is no parser available for user not superuser
