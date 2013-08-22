from django.conf.urls import patterns, url
from .views import settings_json, admin_check_extents


urlpatterns = patterns('',
    url(r'^api/settings.json', settings_json, name='settings_json'),
    url(r'^tools/extents/', admin_check_extents, name='check_extents'),
)
