from django.conf import settings
from django.urls import path, re_path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions, routers

from geotrek.api.mobile import views as api_mobile
from geotrek.api.mobile.views_sync import SyncMobileRedirect, sync_mobile_view, sync_mobile_update_json

router = routers.SimpleRouter()
if 'geotrek.flatpages' in settings.INSTALLED_APPS:
    router.register('flatpages', api_mobile.FlatPageViewSet, basename='flatpage')
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    router.register('treks', api_mobile.TrekViewSet, basename='treks')

schema_view = get_schema_view(
    openapi.Info(
        title="Geotrek API mobile",
        default_version='v1',
        description="Mobile Geotrek API.",
    ),
    urlconf='geotrek.api.mobile.urls',
    public=True,
    permission_classes=(permissions.AllowAny,),
)

app_name = 'apimobile'
urlpatterns = [
    re_path(r'^api/mobile.json$', schema_view.without_ui(cache_timeout=0), {'format': '.json'}, name='schema-json'),
    re_path(r'^api/mobile/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^api/mobile/doc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/mobile/', include(router.urls)),
    path('api/mobile/settings/', api_mobile.SettingsView.as_view(), name='settings'),
    path('api/mobile/commands/sync', SyncMobileRedirect.as_view(), name='sync_mobiles'),
    path('api/mobile/commands/syncview', sync_mobile_view, name='sync_mobiles_view'),
    path('api/mobile/commands/statesync/', sync_mobile_update_json, name='sync_mobiles_state'),
]
