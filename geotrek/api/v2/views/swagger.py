from django.conf import settings
from drf_spectacular.views import SpectacularAPIView


class APIV2SchemaView(SpectacularAPIView):
    urlconf = "geotrek.api.v2.urls"
    custom_settings = {"TITLE": f"{settings.TITLE} - API V2"}
