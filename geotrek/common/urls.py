from django.conf.urls import patterns, url
from .views import JSSettings, admin_check_extents


urlpatterns = patterns('',
    url(r'^api/settings.json', JSSettings.as_view(), name='settings_json'),
    url(r'^tools/extents/', admin_check_extents, name='check_extents'),
)
