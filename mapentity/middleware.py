import logging
from subprocess import check_output

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db import DatabaseError
from django.utils.six.moves.urllib.parse import urlparse

from .settings import app_settings

logger = logging.getLogger(__name__)

CONVERSION_SERVER_HOST = urlparse(app_settings['CONVERSION_SERVER']).hostname
CAPTURE_SERVER_HOST = urlparse(app_settings['CAPTURE_SERVER']).hostname
LOCALHOST = check_output(['hostname', '-I']).decode().split() + ['127.0.0.1']


def get_internal_user():
    if not hasattr(get_internal_user, 'instance'):
        username = app_settings['INTERNAL_USER']
        User = get_user_model()

        internal_user, created = User.objects.get_or_create(
            username=username,
            defaults={'password': settings.SECRET_KEY,
                      'is_active': True,
                      'is_staff': False}
        )

        get_internal_user.instance = internal_user
    return get_internal_user.instance


def clear_internal_user_cache():
    if hasattr(get_internal_user, 'instance'):
        del get_internal_user.instance


class AutoLoginMiddleware(object):
    """
    This middleware enables auto-login for Conversion and Capture servers.

    We could have deployed implemented authentication in ConvertIt and
    django-screamshot, or deployed OpenId, or whatever. But this was a lot easier.
    """
    def process_request(self, request):
        if "HTTP_X_FORWARDED_FOR" in request.META:
            request.META["HTTP_X_PROXY_REMOTE_ADDR"] = request.META["REMOTE_ADDR"]
            parts = request.META["HTTP_X_FORWARDED_FOR"].split(",", 1)
            request.META["REMOTE_ADDR"] = parts[0]

        useragent = request.META.get('HTTP_USER_AGENT', '')
        if useragent:
            request.META['HTTP_USER_AGENT'] = useragent.replace('FrontendTest', '')
        is_running_tests = ('FrontendTest' in useragent or
                            getattr(settings, 'TEST', False))

        user = getattr(request, 'user', None)
        if user and user.is_anonymous() and not is_running_tests:
            remoteip = request.META.get('REMOTE_ADDR')
            remotehost = request.META.get('REMOTE_HOST')

            is_auto_allowed = (
                (remoteip in LOCALHOST or remotehost == 'localhost') or
                (remoteip and remoteip in (CONVERSION_SERVER_HOST, CAPTURE_SERVER_HOST)) or
                (remotehost and remotehost in (CONVERSION_SERVER_HOST, CAPTURE_SERVER_HOST))
            )

            if is_auto_allowed:
                logger.info("Auto-login for %s/%s" % (remoteip, remotehost))
                user = get_internal_user()
                try:
                    user_logged_in.send(self, user=user, request=request)
                except DatabaseError:
                    logger.error("Could not update last-login field of internal user")
                request.user = user
        return None
