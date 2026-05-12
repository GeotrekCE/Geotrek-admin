from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Geotrek API mobile",
        default_version="v1",
        description="Mobile Geotrek API.",
    ),
    urlconf="geotrek.api.mobile.urls",
    public=True,
    permission_classes=(permissions.AllowAny,),
)
