from django.conf import settings
from django.urls import path, re_path, include

from .settings import app_settings
from .registry import registry
from .views import (map_screenshot, history_delete,
                    serve_attachment, JSSettings, Convert)
if app_settings['ACTION_HISTORY_ENABLED']:
    from .models import LogEntry


_MEDIA_URL = settings.MEDIA_URL.replace(app_settings['ROOT_URL'], '')
if _MEDIA_URL.startswith('/'):
    _MEDIA_URL = _MEDIA_URL[1:]
if _MEDIA_URL.endswith('/'):
    _MEDIA_URL = _MEDIA_URL[:-1]


app_name = 'mapentity'
urlpatterns = [
    path('map_screenshot/', map_screenshot, name='map_screenshot'),
    path('convert/', Convert.as_view(), name='convert'),
    path('history/delete/', history_delete, name='history_delete'),
    path('api/auth/', include('rest_framework.urls')),
    # See default value in app_settings.JS_SETTINGS.
    # Will be overriden, most probably.
    path('api/settings.json', JSSettings.as_view(), name='js_settings'),
]


if settings.DEBUG or app_settings['SENDFILE_HTTP_HEADER']:
    urlpatterns += [
        re_path(r'^%s/(?P<path>paperclip/.*)$' % _MEDIA_URL, serve_attachment),
    ]


if app_settings['ACTION_HISTORY_ENABLED']:
    from mapentity.registry import MapEntityOptions

    class LogEntryOptions(MapEntityOptions):
        menu = False
        dynamic_views = ['List', 'JsonList', 'Layer']

    urlpatterns += registry.register(LogEntry, LogEntryOptions)
