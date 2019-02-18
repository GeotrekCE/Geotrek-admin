from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers

from geotrek.api.mobile import views as api_mobile

router = routers.DefaultRouter()
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    router.register(r'trek', api_mobile.TrekViewSet, base_name='trek')
    router.register(r'poi', api_mobile.POIViewSet, base_name='poi')

urlpatterns = [
    url(r'^$', api_mobile.SwaggerSchemaView.as_view(), name="schema"),
    url(r'^', include(router.urls)),
    url(r'^settings/$', api_mobile.SettingsView.as_view(), name='settings')
]
