from django.conf import settings
from django.core.management import call_command
from django.http import HttpResponse
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import LANGUAGE_SESSION_KEY

from mapentity import middleware
from mapentity.middleware import AutoLoginMiddleware, get_internal_user
from unittest import mock

from .test_views import AttachmentFactory
from geotrek.tourism.factories import TouristicEventFactory

User = get_user_model()


@override_settings(TEST=False)
class AutoLoginTest(TestCase):
    def setUp(self):
        middleware.clear_internal_user_cache()
        self.middleware = AutoLoginMiddleware()
        self.request = RequestFactory()

        self.request.user = AnonymousUser()  # usually set by other middleware
        self.request.session = {}
        self.request.META = {'REMOTE_ADDR': '6.6.6.6'}
        self.internal_user = get_internal_user()
        call_command('update_geotrek_permissions')

    def test_internal_user_cannot_login(self):
        success = self.client.login(
            username=self.internal_user.username,
            password=settings.SECRET_KEY)
        self.assertFalse(success)

    def test_auto_login_happens_by_remote_addr(self):
        obj = TouristicEventFactory.create(published=False)
        middleware.CONVERSION_SERVER_HOST = '1.2.3.4'
        attachment = AttachmentFactory.create(content_object=obj)
        response = self.client.get("/media/%s" % attachment.attachment_file,
                                   REMOTE_ADDR='1.2.3.5')
        self.assertEqual(response.status_code, 403)
        with mock.patch('django.contrib.auth.models._user_has_perm', return_value=True):
            response = self.client.get("/media/%s" % attachment.attachment_file,
                                       REMOTE_ADDR='1.2.3.4')
        self.assertEqual(response.status_code, 200)

    def test_auto_login_do_not_change_current_user(self):
        user = User.objects.create_user('aah', 'email@corp.com', 'booh')
        self.request.user = user
        self.middleware.process_request(self.request)
        self.assertEqual(self.request.user, user)

    def test_auto_login_do_not_log_whoever(self):
        self.middleware.process_request(self.request)
        self.assertTrue(self.request.user.is_anonymous)

    def test_auto_login_for_conversion(self):
        middleware.CONVERSION_SERVER_HOST = '1.2.3.4'
        self.request.META['REMOTE_ADDR'] = '1.2.3.4'

        self.assertTrue(self.request.user.is_anonymous)
        self.middleware.process_request(self.request)
        self.assertFalse(self.request.user.is_anonymous)
        self.assertEqual(self.request.user, self.internal_user)

    def test_auto_login_for_capture(self):
        middleware.CAPTURE_SERVER_HOST = '4.5.6.7'
        self.request.META['REMOTE_ADDR'] = '4.5.6.7'

        self.assertTrue(self.request.user.is_anonymous)
        self.middleware.process_request(self.request)
        self.assertFalse(self.request.user.is_anonymous)
        self.assertEqual(self.request.user, self.internal_user)

    def test_auto_login_for_conversion_host(self):
        middleware.CONVERSION_SERVER_HOST = 'convertit.makina.com'
        self.request.META['REMOTE_HOST'] = 'convertit.makina.com'

        self.assertTrue(self.request.user.is_anonymous)
        self.middleware.process_request(self.request)
        self.assertFalse(self.request.user.is_anonymous)
        self.assertEqual(self.request.user, self.internal_user)

    def test_auto_login_for_capture_host(self):
        middleware.CAPTURE_SERVER_HOST = 'capture.makina.com'
        self.request.META['REMOTE_HOST'] = 'capture.makina.com'

        self.assertTrue(self.request.user.is_anonymous)
        self.middleware.process_request(self.request)
        self.assertFalse(self.request.user.is_anonymous)
        self.assertEqual(self.request.user, self.internal_user)
