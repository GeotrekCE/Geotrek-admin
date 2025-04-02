from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings
from django.urls import reverse
from mapentity.tests.factories import SuperUserFactory, UserFactory

from geotrek.api.mobile.tasks import launch_sync_mobile


class SyncMobileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super_user = SuperUserFactory()
        cls.simple_user = UserFactory()

    def test_get_sync_mobile_superuser(self):
        self.client.force_login(self.super_user)
        response = self.client.get(reverse("apimobile:sync_mobiles_view"))
        self.assertEqual(response.status_code, 200)

    def test_get_sync_mobile_simpleuser(self):
        self.client.login(username="homer", password="doooh")
        response = self.client.get(reverse("apimobile:sync_mobiles_view"))
        self.assertRedirects(response, "/login/?next=/api/mobile/commands/syncview")

    def test_post_sync_mobile_superuser(self):
        """
        test if sync can be launched by superuser post
        """
        self.client.force_login(self.super_user)
        response = self.client.post(reverse("apimobile:sync_mobiles"), data={})
        self.assertRedirects(response, "/api/mobile/commands/syncview")

    def test_post_sync_mobile_simpleuser(self):
        """
        test if sync can be launched by simple user post
        """
        self.client.login(username="homer", password="doooh")
        response = self.client.post(reverse("apimobile:sync_mobiles"), data={})
        self.assertRedirects(response, "/login/?next=/api/mobile/commands/sync")

    def test_get_sync_mobile_states_superuser(self):
        self.client.force_login(self.super_user)
        response = self.client.post(reverse("apimobile:sync_mobiles_state"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"[]")

    def test_get_sync_mobile_states_simpleuser(self):
        self.client.login(username="homer", password="doooh")
        response = self.client.post(reverse("apimobile:sync_mobiles_state"), data={})
        self.assertRedirects(response, "/login/?next=/api/mobile/commands/statesync/")

    @patch("sys.stdout", new_callable=StringIO)
    @override_settings(
        CELERY_ALWAYS_EAGER=False,
        SYNC_MOBILE_ROOT=TemporaryDirectory(dir=settings.TMP_DIR).name,
        SYNC_MOBILE_OPTIONS={"url": "http://localhost:8000", "skip_tiles": True},
    )
    def test_get_sync_mobile_states_superuser_with_sync_mobile(self, mocked_stdout):
        self.client.force_login(self.super_user)
        launch_sync_mobile.apply()
        response = self.client.post(reverse("apimobile:sync_mobiles_state"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"infos": "Sync mobile ended"', response.content)

    @patch("sys.stdout", new_callable=StringIO)
    @patch(
        "geotrek.api.management.commands.sync_mobile.Command.handle",
        return_value=None,
        side_effect=Exception("This is a test"),
    )
    @override_settings(
        SYNC_MOBILE_ROOT=TemporaryDirectory(dir=settings.TMP_DIR).name,
        SYNC_MOBILE_OPTIONS={"url": "http://localhost:8000", "skip_tiles": True},
    )
    def test_get_sync_mobile_states_superuser_with_sync_mobile_fail(
        self, mocked_stdout, command
    ):
        self.client.force_login(self.super_user)
        launch_sync_mobile.apply()
        response = self.client.post(reverse("apimobile:sync_mobiles_state"), data={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"exc_message": "This is a test"', response.content)

    @patch("sys.stdout", new_callable=StringIO)
    @override_settings(
        SYNC_MOBILE_ROOT=TemporaryDirectory(dir=settings.TMP_DIR).name,
        SYNC_MOBILE_OPTIONS={"url": "http://localhost:8000", "skip_tiles": True},
    )
    def test_launch_sync_mobile(self, mocked_stdout):
        task = launch_sync_mobile.apply()
        log = mocked_stdout.getvalue()
        self.assertIn("Done", log)
        self.assertIn("Sync mobile ended", log)
        self.assertEqual(task.status, "SUCCESS")

    @patch(
        "geotrek.api.management.commands.sync_mobile.Command.handle",
        return_value=None,
        side_effect=Exception("This is a test"),
    )
    @patch("sys.stdout", new_callable=StringIO)
    def test_launch_sync_mobile_fail(self, mocked_stdout, command):
        task = launch_sync_mobile.apply()
        log = mocked_stdout.getvalue()
        self.assertNotIn("Done", log)
        self.assertNotIn("Sync mobile ended", log)
        self.assertEqual(task.status, "FAILURE")

    @override_settings(SYNC_MOBILE_ROOT=TemporaryDirectory(dir=settings.TMP_DIR).name)
    @patch(
        "geotrek.api.management.commands.sync_mobile.Command.handle",
        return_value=None,
        side_effect=Exception("This is a test"),
    )
    @patch("sys.stdout", new_callable=StringIO)
    def test_launch_sync_mobile_no_root(self, mocked_stdout, command):
        task = launch_sync_mobile.apply()
        log = mocked_stdout.getvalue()
        self.assertNotIn("Done", log)
        self.assertNotIn("Sync mobile ended", log)
        self.assertEqual(task.status, "FAILURE")
