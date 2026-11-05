from django.conf import settings
from drf_spectacular.views import SpectacularAPIView


class APIMobileSchemaView(SpectacularAPIView):
    urlconf = "geotrek.api.mobile.urls"
    custom_settings = {"TITLE": f"{settings.TITLE} - API Mobile"}
