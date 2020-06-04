import os
from io import StringIO
import shutil

from unittest import mock


from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test.utils import override_settings

from mapentity.factories import SuperUserFactory

from geotrek.flatpages.factories import FlatPageFactory
from geotrek.trekking.tasks import launch_sync_rando


class RESTViewsTest(TestCase):
    def setUp(self):
        FlatPageFactory.create_batch(10, published=True)
        FlatPageFactory.create(published=False)

    def test_records_list(self):
        response = self.client.get('/api/en/flatpages.json')
        self.assertEqual(response.status_code, 200)
        records = response.json()
        self.assertEqual(len(records), 10)

    def test_serialized_attributes(self):
        response = self.client.get('/api/en/flatpages.json')
        records = response.json()
        record = records[0]
        self.assertEqual(
            sorted(record.keys()),
            sorted(['content', 'external_url', 'id', 'last_modified',
                    'media', 'portal', 'publication_date', 'published',
                    'published_status', 'slug', 'source', 'target',
                    'title']))


class SyncRandoViewTest(TestCase):
    def setUp(self):
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        if os.path.exists(os.path.join('var', 'tmp')):
            shutil.rmtree(os.path.join('var', 'tmp'))
        self.super_user = SuperUserFactory.create(username='admin', password='super')
        self.simple_user = User.objects.create_user(username='homer', password='doooh')

    def test_get_sync_superuser(self):
        self.client.login(username='admin', password='super')
        response = self.client.get(reverse('common:sync_randos_view'))
        self.assertEqual(response.status_code, 200)

    def test_post_sync_superuser(self):
        """
        test if sync can be launched by superuser post
        """
        self.client.login(username='admin', password='super')
        response = self.client.post(reverse('trekking:sync_randos'), data={})
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
        response = self.client.post(reverse('trekking:sync_randos'), data={})
        self.assertRedirects(response, '/login/?next=/commands/sync')

    def test_get_sync_states_superuser(self):
        self.client.login(username='admin', password='super')
        response = self.client.post(reverse('trekking:sync_randos_state'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')

    def test_get_sync_states_simpleuser(self):
        self.client.login(username='homer', password='doooh')
        response = self.client.post(reverse('trekking:sync_randos_state'), data={})
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
        response = self.client.post(reverse('trekking:sync_randos_state'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"infos": "Sync ended"', response.content)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @mock.patch('geotrek.common.management.commands.sync_rando.Command.handle', return_value=None,
                side_effect=Exception('This is a test'))
    @override_settings(CELERY_ALWAYS_EAGER=False,
                       SYNC_RANDO_ROOT='tmp', SYNC_RANDO_OPTIONS={'url': 'http://localhost:8000',
                                                                  'skip_tiles': True, 'skip_pdf': True,
                                                                  'skip_dem': True, 'skip_profile_png': True})
    def test_get_sync_mobile_states_superuser_with_sync_mobile_fail(self, mocked_stdout, command):
        self.client.login(username='admin', password='super')
        if os.path.exists(os.path.join('var', 'tmp_sync_rando')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_rando'))
        launch_sync_rando.apply()
        response = self.client.post(reverse('trekking:sync_randos_state'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"exc_message": "This is a test"', response.content)

    @mock.patch('sys.stdout', new_callable=StringIO)
    @override_settings(SYNC_RANDO_ROOT='var/tmp', SYNC_RANDO_OPTIONS={'url': 'http://localhost:8000', 'skip_tiles': True,
                                                                      'skip_pdf': True,
                                                                      'skip_dem': True, 'skip_profile_png': True})
    def test_launch_sync_rando(self, mocked_stdout):
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
