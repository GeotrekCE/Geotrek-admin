import os
from io import StringIO
import shutil
from unittest import mock

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse

from mapentity.tests.factories import UserFactory, SuperUserFactory
from mapentity.views.generic import MapEntityList
from geotrek.common.mixins import CustomColumnsMixin
from geotrek.common.parsers import Parser
from geotrek.common.tasks import launch_sync_rando
from geotrek.trekking.models import Path


class ViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(username='homer', password='dooh')

    def setUp(self):
        self.client.force_login(user=self.user)

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

    @override_settings(COLUMNS_LISTS={})
    @mock.patch('geotrek.common.mixins.logger')
    def test_custom_columns_mixin_error_log(self, mock_logger):
        # Create view where columns fields are omitted
        class MissingColumns(CustomColumnsMixin, MapEntityList):
            model = Path

        MissingColumns()
        # Assert logger raises error message
        message = "Cannot build columns for class MissingColumns.\nPlease define on this class either : \n  - a field 'columns'\nOR \n  - two fields 'mandatory_columns' AND 'default_extra_columns'"
        mock_logger.error.assert_called_with(message)


class ViewsImportTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory.create(username='homer', password='dooh')

    def setUp(self):
        self.client.force_login(user=self.user)

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

        with open('geotrek/common/tests/data/test.zip', 'rb') as real_archive:
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
        self.assertNotContains(response_real, '<form  method="post"')

    def test_import_from_web_bad_parser(self):
        self.user.is_superuser = True
        self.user.save()

        url = reverse('common:import_dataset')

        response_real = self.client.post(
            url, {
                'import-web': 'Upload',
                'without-file-parser': '99',
            }
        )
        self.assertEqual(response_real.status_code, 200)
        self.assertContains(response_real, "Select a valid choice. 99 is not one of the available choices.")
        # There is no parser available for user not superuser

    def test_import_from_web_good_parser(self):
        self.user.is_superuser = True
        self.user.save()

        url = reverse('common:import_dataset')
        real_key = self.client.get(url).context['form_without_file'].fields['parser'].choices[0][0]
        response_real = self.client.post(
            url, {
                'import-web': 'Upload',
                'without-file-parser': real_key,
            }
        )
        self.assertEqual(response_real.status_code, 200)
        self.assertNotContains(response_real, "Select a valid choice. {real_key} "
                                              "is not one of the available choices.".format(real_key=real_key))


class SyncRandoViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super_user = SuperUserFactory.create(username='admin', password='super')
        cls.simple_user = User.objects.create_user(username='homer', password='doooh')

    def setUp(self):
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        if os.path.exists(os.path.join('var', 'tmp')):
            shutil.rmtree(os.path.join('var', 'tmp'))

    def test_get_sync_superuser(self):
        self.client.login(username='admin', password='super')
        response = self.client.get(reverse('common:sync_randos_view'))
        self.assertEqual(response.status_code, 200)

    def test_post_sync_superuser(self):
        """
        test if sync can be launched by superuser post
        """
        self.client.login(username='admin', password='super')
        response = self.client.post(reverse('common:sync_randos'), data={})
        self.assertRedirects(response, '/commands/syncview')

    def test_get_sync_simpleuser(self):
        self.client.login(username='homer', password='doooh')
        response = self.client.get(reverse('common:sync_randos_view'))
        self.assertRedirects(response, '/login/?next=/commands/syncview')

    def test_post_sync_simpleuser(self):
        """
        test if sync can be launched by simple user post
        """
        self.client.login(username='homer', password='doooh')
        response = self.client.post(reverse('common:sync_randos'), data={})
        self.assertRedirects(response, '/login/?next=/commands/sync')

    def test_get_sync_states_superuser(self):
        self.client.login(username='admin', password='super')
        response = self.client.post(reverse('common:sync_randos_state'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')

    def test_get_sync_states_simpleuser(self):
        self.client.login(username='homer', password='doooh')
        response = self.client.post(reverse('common:sync_randos_state'), data={})
        self.assertRedirects(response, '/login/?next=/commands/statesync/')

    @mock.patch('sys.stdout', new_callable=StringIO)
    @override_settings(CELERY_ALWAYS_EAGER=False,
                       SYNC_RANDO_ROOT='var/tmp', SYNC_RANDO_OPTIONS={'url': 'http://localhost:8000',
                                                                      'skip_tiles': True, 'skip_pdf': True,
                                                                      'skip_dem': True, 'skip_profile_png': True})
    def test_get_sync_rando_states_superuser_with_sync_rando(self, mocked_stdout):
        self.client.login(username='admin', password='super')
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        launch_sync_rando.apply()
        response = self.client.post(reverse('common:sync_randos_state'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"infos": "Sync ended"', response.content)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('geotrek.common.management.commands.sync_rando.Command.handle', return_value=None,
                side_effect=Exception('This is a test'))
    @override_settings(CELERY_ALWAYS_EAGER=False,
                       SYNC_RANDO_ROOT='tmp', SYNC_RANDO_OPTIONS={'url': 'http://localhost:8000',
                                                                  'skip_tiles': True, 'skip_pdf': True,
                                                                  'skip_dem': True, 'skip_profile_png': True})
    def test_get_sync_rando_states_superuser_with_sync_mobile_fail(self, mocked_stdout, command):
        self.client.login(username='admin', password='super')
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        launch_sync_rando.apply()
        response = self.client.post(reverse('common:sync_randos_state'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"exc_message": "This is a test"', response.content)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('geotrek.trekking.models.Trek.prepare_map_image')
    @mock.patch('landez.TilesManager.tile', return_value=b'I am a png')
    @override_settings(SYNC_RANDO_ROOT='var/tmp', SYNC_RANDO_OPTIONS={'url': 'http://localhost:8000', 'skip_tiles': False,
                                                                      'skip_pdf': False,
                                                                      'skip_dem': False, 'skip_profile_png': False})
    def test_launch_sync_rando(self, mock_tile, mock_map_image, mocked_stdout):
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        task = launch_sync_rando.apply()
        log = mocked_stdout.getvalue()
        self.assertIn("Done", log)
        self.assertEqual(task.status, "SUCCESS")
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))

    @mock.patch('geotrek.common.management.commands.sync_rando.Command.handle', return_value=None,
                side_effect=Exception('This is a test'))
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_launch_sync_rando_fail(self, mocked_stdout, command):
        task = launch_sync_rando.apply()
        log = mocked_stdout.getvalue()
        self.assertNotIn("Done", log)
        self.assertNotIn('Sync ended', log)
        self.assertEqual(task.status, "FAILURE")

    @mock.patch('geotrek.common.management.commands.sync_rando.Command.handle', return_value=None,
                side_effect=Exception('This is a test'))
    @override_settings(SYNC_RANDO_ROOT='tmp')
    @mock.patch('sys.stdout', new_callable=StringIO)
    def test_launch_sync_rando_no_rando_root(self, mocked_stdout, command):
        if os.path.exists('tmp'):
            shutil.rmtree('tmp')
        task = launch_sync_rando.apply()
        log = mocked_stdout.getvalue()
        self.assertNotIn("Done", log)
        self.assertNotIn('Sync rando ended', log)
        self.assertEqual(task.status, "FAILURE")

    def tearDown(self):
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        if os.path.exists(os.path.join('var', 'tmp')):
            shutil.rmtree(os.path.join('var', 'tmp'))
