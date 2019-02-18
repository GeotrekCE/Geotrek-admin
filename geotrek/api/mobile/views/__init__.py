from __future__ import unicode_literals

from rest_framework import response, permissions
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers

from django.conf import settings
from .common import SettingsView  # noqa
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from .trekking import TrekViewSet, MinimalTrekViewSet, POIViewSet  # noqa


class SwaggerSchemaView(APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer,
    ]

    def get(self, request):
        generator = SchemaGenerator(
            title='Geotrek API mobile',
            urlconf='geotrek.api.mobile.urls',
            url='/api/mobile',
            description="Mobile Geotrek API."
        )
        schema = generator.get_schema(request=request)

        return response.Response(schema)
