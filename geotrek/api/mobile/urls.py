from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers

from geotrek.api.mobile import views as api_mobile
from geotrek.api.mobile.views_sync import SyncMobileRedirect, sync_mobile_view, sync_mobile_update_json

router = routers.DefaultRouter()
if 'geotrek.flatpages' in settings.INSTALLED_APPS:
    router.register(r'flatpages', api_mobile.FlatPageViewSet, base_name='flatpage')
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    router.register(r'treks', api_mobile.TrekViewSet, base_name='treks')
urlpatterns = [
    url(r'^$', api_mobile.SwaggerSchemaView.as_view(), name="schema"),
    url(r'^', include(router.urls)),
    url(r'^settings/$', api_mobile.SettingsView.as_view(), name='settings'),
    url(r'^commands/sync$', SyncMobileRedirect.as_view(), name='sync_mobiles'),
    url(r'^commands/syncview$', sync_mobile_view, name='sync_mobiles_view'),
    url(r'^commands/statesync/$', sync_mobile_update_json, name='sync_mobiles_state'),
]
