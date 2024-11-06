import re

from django.utils import translation
from django.utils.translation.trans_real import get_supported_language_variant

language_code_prefix_re = re.compile(r'^/api/([\w-]+)(/|$)')


def get_language_from_path(path):
    regex_match = language_code_prefix_re.match(path)
    if not regex_match:
        return None
    return regex_match.group(1)


def get_language_from_request(request):
    return request.GET.get('lang')


def get_language_from_url(request):
    lang = get_language_from_path(request.path_info) or get_language_from_request(request)
    try:
        return get_supported_language_variant(lang)
    except LookupError:
        return None


class APILocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language = get_language_from_url(request) or translation.get_language()
        with translation.override(language, deactivate=True):
            request.LANGUAGE_CODE = language
            return self.get_response(request)
