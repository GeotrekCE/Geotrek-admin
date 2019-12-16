import re
import socket
from netifaces import interfaces, ifaddresses, AF_INET

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.utils import DatabaseError
from django.utils import translation
from django.utils.six.moves.urllib.parse import urlparse
from django.utils.translation.trans_real import get_supported_language_variant
from mapentity.middleware import AutoLoginMiddleware, get_internal_user

language_code_prefix_re = re.compile(r'^/api/([\w-]+)(/|$)')


def get_language_from_path(path):
    regex_match = language_code_prefix_re.match(path)
    if not regex_match:
        return None
    lang_code = regex_match.group(1)
    try:
        return get_supported_language_variant(lang_code)
    except LookupError:
        return None


class APILocaleMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        language = get_language_from_path(request.path_info)
        if language:
            translation.activate(language)
            request.LANGUAGE_CODE = translation.get_language()


CONVERSION_SERVER_HOST = urlparse(settings.MAPENTITY_CONFIG['CONVERSION_SERVER']).hostname
CAPTURE_SERVER_HOST = urlparse(settings.MAPENTITY_CONFIG['CAPTURE_SERVER']).hostname
AUTOLOGIN_IPS = [
    socket.gethostbyname(CONVERSION_SERVER_HOST),
    socket.gethostbyname(CAPTURE_SERVER_HOST),
]
for interface in interfaces():
    for link in ifaddresses(interface)[AF_INET]:
        AUTOLOGIN_IPS.append(link['addr'])


class FixedAutoLoginMiddleware(AutoLoginMiddleware):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        if "HTTP_X_FORWARDED_FOR" in request.META:
            request.META["HTTP_X_PROXY_REMOTE_ADDR"] = request.META["REMOTE_ADDR"]
            parts = request.META["HTTP_X_FORWARDED_FOR"].split(",", 1)
            request.META["REMOTE_ADDR"] = parts[0]

        useragent = request.META.get('HTTP_USER_AGENT', '')
        if useragent:
            request.META['HTTP_USER_AGENT'] = useragent.replace('FrontendTest', '')
        is_running_tests = ('FrontendTest' in useragent or getattr(settings, 'TEST', False))

        user = getattr(request, 'user', None)

        if user and user.is_anonymous() and not is_running_tests:
            remoteip = request.META.get('REMOTE_ADDR')

            if remoteip in AUTOLOGIN_IPS:
                user = get_internal_user()
                try:
                    user_logged_in.send(self, user=user, request=request)
                except DatabaseError as exc:
                    print(exc)
                request.user = user

        return None
