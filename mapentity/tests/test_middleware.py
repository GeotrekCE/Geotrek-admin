from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.http import HttpResponse
from django.test.client import RequestFactory
from django.test.utils import override_settings

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from mapentity import middleware
from mapentity.middleware import AutoLoginMiddleware, get_internal_user
from unittest import mock

from .test_views import AttachmentFactory
from geotrek.tourism.factories import TouristicEventFactory

User = get_user_model()


def fake_view(request):
    return HttpResponse()


@override_settings(TEST=False)
class AutoLoginTest(TestCase):
    def setUp(self):
        middleware.clear_internal_user_cache()
        self.middleware = AutoLoginMiddleware(fake_view)
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
        middleware.AUTOLOGIN_IPS = ['1.2.3.4']
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
        self.middleware(self.request)
        self.assertEqual(self.request.user, user)

    def test_auto_login_do_not_log_whoever(self):
        self.middleware(self.request)
        self.assertTrue(self.request.user.is_anonymous)

    def test_auto_login(self):
        middleware.AUTOLOGIN_IPS = ['1.2.3.4']
        self.request.META['REMOTE_ADDR'] = '1.2.3.4'

        self.assertTrue(self.request.user.is_anonymous)
        self.middleware(self.request)
        self.assertFalse(self.request.user.is_anonymous)
        self.assertEqual(self.request.user, self.internal_user)

    def test_auto_login_proxy(self):
        middleware.AUTOLOGIN_IPS = ['1.2.3.4']
        self.request.META['HTTP_X_FORWARDED_FOR'] = '1.2.3.4,2.2.2.2'

        self.assertTrue(self.request.user.is_anonymous)
        self.middleware(self.request)
        self.assertFalse(self.request.user.is_anonymous)
        self.assertEqual(self.request.user, self.internal_user)
