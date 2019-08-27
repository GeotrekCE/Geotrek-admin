from io import StringIO
from mock import patch
import os
import shutil

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from mapentity.factories import SuperUserFactory

from geotrek.api.mobile.tasks import launch_sync_mobile


class SyncMobileViewTest(TestCase):
    def setUp(self):
        self.super_user = SuperUserFactory.create(username='admin', password='super')
        self.simple_user = User.objects.create_user(username='homer', password='doooh')

    def test_get_sync_mobile_superuser(self):
        self.client.login(username='admin', password='super')
        response = self.client.get(reverse('apimobile:sync_mobiles_view'))
        self.assertEqual(response.status_code, 200)

    def test_get_sync_mobile_simpleuser(self):
        self.client.login(username='homer', password='doooh')
        response = self.client.get(reverse('apimobile:sync_mobiles_view'))
        self.assertRedirects(response, '/login/?next=/api/mobile/commands/syncview')

    def test_post_sync_mobile_superuser(self):
        """
        test if sync can be launched by superuser post
        """
        self.client.login(username='admin', password='super')
        response = self.client.post(reverse('apimobile:sync_mobiles'), data={})
        self.assertRedirects(response, '/api/mobile/commands/syncview')

    def test_post_sync_mobile_simpleuser(self):
        """
        test if sync can be launched by simple user post
        """
        self.client.login(username='homer', password='doooh')
        response = self.client.post(reverse('apimobile:sync_mobiles'), data={})
        self.assertRedirects(response, '/login/?next=/api/mobile/commands/sync')

    def test_get_sync_mobile_states_superuser(self):
        self.client.login(username='admin', password='super')
        response = self.client.post(reverse('apimobile:sync_mobiles_state'), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[]')

    def test_get_sync_mobile_states_simpleuser(self):
        self.client.login(username='homer', password='doooh')
        response = self.client.post(reverse('apimobile:sync_mobiles_state'), data={})
        self.assertRedirects(response, '/login/?next=/api/mobile/commands/statesync/')

    @patch('sys.stdout', new_callable=StringIO)
    def test_launch_sync_mobile(self, mocked_stdout):
        if os.path.exists(os.path.join('var', 'tmp_sync_mobile')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_mobile'))
        task = launch_sync_mobile.s(url="http://localhost:8000", skip_tiles=True, skip_pdf=True, ).apply()
        self.assertIn("Done", mocked_stdout.getvalue())

        self.assertEqual(task.status, "SUCCESS")
        if os.path.exists(os.path.join('var', 'tmp_sync_mobile')):
            shutil.rmtree(os.path.join('var', 'tmp_sync_mobile'))

    @patch('django.core.management.call_command')
    @patch('sys.stdout', new_callable=BytesIO)
    def test_launch_sync_rando(self, mocked_stdout, ccommand):
        ccommand.side_effect = Exception('This is a test')
        task = launch_sync_mobile.s(url="http://localhost:8000", skip_tiles=True, skip_pdf=True,
                                    skip_dem=True, skip_profile_png=True).apply()
        self.assertIn("Done", mocked_stdout.getvalue())
        self.assertEqual(task.status, "SUCCESS")
