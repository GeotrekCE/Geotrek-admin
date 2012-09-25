from django.conf.urls import patterns, url

from .views import map_screenshot


urlpatterns = patterns('',
    url(r'^map_screenshot/$', map_screenshot, name='map_screenshot'),
)
