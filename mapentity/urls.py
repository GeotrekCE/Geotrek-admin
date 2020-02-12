from django.conf import settings
from django.conf.urls import url, include

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


urlpatterns = [
    url(r'^map_screenshot/$', map_screenshot, name='map_screenshot'),
    url(r'^convert/$', Convert.as_view(), name='convert'),
    url(r'^history/delete/$', history_delete, name='history_delete'),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    # See default value in app_settings.JS_SETTINGS.
    # Will be overriden, most probably.
    url(r'^api/settings.json$', JSSettings.as_view(), name='js_settings'),
]


if settings.DEBUG or app_settings['SENDFILE_HTTP_HEADER']:
    urlpatterns += [
        url(r'^%s/(?P<path>paperclip/.*)$' % _MEDIA_URL,
            serve_attachment),
    ]


if app_settings['ACTION_HISTORY_ENABLED']:
    from mapentity.registry import MapEntityOptions

    class LogEntryOptions(MapEntityOptions):
        menu = False
        dynamic_views = ['List', 'JsonList', 'Layer']

    urlpatterns += registry.register(LogEntry, LogEntryOptions)
