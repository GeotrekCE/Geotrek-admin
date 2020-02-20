from unittest import mock
from django.test import TransactionTestCase, RequestFactory
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.test.utils import override_settings
from django.urls import reverse

from mapentity.registry import app_settings
from mapentity.decorators import view_permission_required


class ViewPermissionRequiredTestCase(TransactionTestCase):
    def setUp(self):
        # Fake request and its positional and keywords arguments.
        self.request = RequestFactory().get('/toto/')
        self.request._messages = mock.MagicMock()
        self.request.user = mock.MagicMock()
        self.request.user.is_anonymous = mock.MagicMock(return_value=False)
        self.request_args = ['fake_arg']
        self.request_kwargs = {'fake': 'kwarg'}
        self.mocked_view = mock.MagicMock()

    def run_decorated_view(self, raise_exception=None, login_url=None):
        """Setup, decorate and call view, then return response."""
        decorator = view_permission_required(raise_exception=raise_exception,
                                             login_url=login_url)
        decorated_view = decorator(self.mocked_view)
        # Return response.
        return decorated_view(self.mocked_view,
                              self.request,
                              *self.request_args,
                              **self.request_kwargs)

    @override_settings(LOGIN_URL='/admin/')
    def test_anonymous_are_redirected_to_login(self):
        self.request.user.is_anonymous.return_value = True
        self.request.user.has_perm.return_value = False
        response = self.run_decorated_view()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(settings.LOGIN_URL))

    def test_unauthorized_is_rendered_if_missing_perm(self):
        self.request.user.is_anonymous.return_value = False
        self.request.user.has_perm.return_value = False
        self.assertRaises(PermissionDenied, self.run_decorated_view)

    def test_unauthorized_is_not_rendered_if_login_url_is_provided(self):
        self.request.user.is_anonymous.return_value = False
        self.request.user.has_perm.return_value = False
        response = self.run_decorated_view(login_url='login')
        self.assertEqual(response.status_code, 302)

    def test_permission_is_taken_from_view(self):
        self.request.user.is_anonymous.return_value = False
        self.mocked_view.get_view_perm.return_value = 'view-perm'
        self.run_decorated_view()
        self.request.user.has_perm.assert_called_once_with('view-perm')

    def test_anonymous_may_be_authorized_from_settings(self):
        self.request.user.is_authenticated.return_value = False
        self.mocked_view.get_view_perm.return_value = 'view-perm'
        app_settings['ANONYMOUS_VIEWS_PERMS'] = ('view-perm',)
        response = self.run_decorated_view()
        self.assertNotEqual(response.status_code, 200)

    def test_a_message_is_show_when_user_is_redirected(self):
        self.request.user.has_perm.return_value = False
        with mock.patch('django.contrib.messages.warning') as patched:
            self.run_decorated_view(raise_exception=False)
            patched.assert_called_once_with(
                self.request, u'Access to the requested resource is restricted. You have been redirected.')

    def test_it_redirects_to_the_specified_view(self):
        self.request.user.has_perm.return_value = False
        response = self.run_decorated_view(raise_exception=False,
                                           login_url='tourism:touristicevent_list')
        self.assertEqual(response.status_code, 302)
        touristiceventlist_url = reverse('tourism:touristicevent_list')
        self.assertTrue(touristiceventlist_url in response['Location'])
