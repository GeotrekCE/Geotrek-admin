from django.conf.urls import patterns, url

from .views import map_screenshot, history_delete


urlpatterns = patterns('',
    url(r'^map_screenshot/$', map_screenshot, name='map_screenshot'),
    url(r'^history/delete/$', history_delete, name='history_delete'),
)
