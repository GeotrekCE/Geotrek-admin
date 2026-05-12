from django.conf import settings


class LocaleForcedMiddleware:
    """
    This will force session language for authenticated API calls.

    Since Django gives priority to session language, and since for API
    calls, we use ``Accept-language`` header to obtain translations, we
    override it.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_agent = request.headers.get("user-agent")
        is_api_call = user_agent is None or "geotrek" in user_agent
        forced_language = request.headers.get("accept-language")
        if is_api_call and forced_language and hasattr(request, "session"):
            request.session["django_language"] = forced_language
        return self.get_response(request)


class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if settings.DEBUG:
            response["Access-Control-Allow-Origin"] = "*"
        return response
