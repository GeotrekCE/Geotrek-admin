from django.conf.urls import patterns, url
from .views import settings_json


urlpatterns = patterns('',
    url(r'^api/settings.json', settings_json, name='settings_json'),
)
