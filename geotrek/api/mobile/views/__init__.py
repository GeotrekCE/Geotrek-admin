from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from django.conf import settings
from .common import SettingsView  # noqa
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from .trekking import TrekViewSet  # noqa
if 'geotrek.flatpages' in settings.INSTALLED_APPS:
    from .common import FlatPageViewSet  # noqa


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
