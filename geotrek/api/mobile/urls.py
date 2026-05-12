from django.conf import settings
from django.urls import include, path
from rest_framework import routers

from geotrek.api.mobile import views as api_mobile
from geotrek.api.mobile.views_sync import (
    SyncMobileRedirect,
    sync_mobile_update_json,
    sync_mobile_view,
)

router = routers.DefaultRouter()
if "geotrek.flatpages" in settings.INSTALLED_APPS:
    router.register("flatpages", api_mobile.FlatPageViewSet, basename="flatpage")
if "geotrek.trekking" in settings.INSTALLED_APPS:
    router.register("treks", api_mobile.TrekViewSet, basename="treks")
app_name = "apimobile"
_urlpatterns = []
if "drf_yasg" in settings.INSTALLED_APPS:
    _urlpatterns.append(
        path(
            "",
            api_mobile.schema_view.with_ui("swagger", cache_timeout=0),
            name="schema",
        )
    )
_urlpatterns += [
    path("", include(router.urls)),
    path("settings/", api_mobile.SettingsView.as_view(), name="settings"),
    path("commands/sync", SyncMobileRedirect.as_view(), name="sync_mobiles"),
    path("commands/syncview", sync_mobile_view, name="sync_mobiles_view"),
    path("commands/statesync/", sync_mobile_update_json, name="sync_mobiles_state"),
]
urlpatterns = [path("api/mobile/", include(_urlpatterns))]
