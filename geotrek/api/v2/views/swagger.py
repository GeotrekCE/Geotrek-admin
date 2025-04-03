from django.conf import settings
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Geotrek API v2",
        default_version="v2",
        description=settings.SWAGGER_SETTINGS["API_V2_DESCRIPTION"],
    ),
    urlconf="geotrek.api.v2.urls",
    public=True,
    permission_classes=(permissions.AllowAny,),
)
