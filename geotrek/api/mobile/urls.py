from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers


if 'geotrek.flatpages' and 'geotrek.trekking' and 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.api.mobile import views as api_mobile
    router = routers.DefaultRouter()
    router.register(r'flatpages', api_mobile.FlatPageViewSet, base_name='flatpage')
    router.register(r'treks', api_mobile.TrekViewSet, base_name='treks')
    urlpatterns = [
        url(r'^$', api_mobile.SwaggerSchemaView.as_view(), name="schema"),
        url(r'^', include(router.urls)),
        url(r'^settings/$', api_mobile.SettingsView.as_view(), name='settings'),
    ]
