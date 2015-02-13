from django.conf import settings


class LocaleForcedMiddleware(object):
    """
    This will force session language for authenticated API calls.

    Since Django gives priority to session language, and since for API
    calls, we use ``Accept-language`` header to obtain translations, we
    override it.
    """
    def process_request(self, request):
        user_agent = request.META.get('HTTP_USER_AGENT')
        is_api_call = (user_agent is None or 'geotrek' in user_agent)
        forced_language = request.META.get('HTTP_ACCEPT_LANGUAGE')
        if is_api_call and forced_language and hasattr(request, 'session'):
            request.session['django_language'] = forced_language


class CorsMiddleware(object):
    def process_response(self, request, response):
        if settings.DEBUG:
            response['Access-Control-Allow-Origin'] = "*"
        return response
