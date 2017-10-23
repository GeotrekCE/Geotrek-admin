from __future__ import unicode_literals

from rest_framework import response, decorators, permissions
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers

from django.conf import settings
if 'geotrek.core' in settings.INSTALLED_APPS:
    from .core import PathViewSet
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from .trekking import TrekViewSet, TourViewSet, POIViewSet
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from .sensitivity import SensitiveAreaViewSet


class SwaggerSchemaView(APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer,
    ]

    def get(self, request):
        generator = SchemaGenerator(
            title='Geotrek API v2 beta 1',
            urlconf='geotrek.api.v2.urls',
            url='/api/v2',
            description="New Geotrek OpenAPI. Please Authorize first."
        )
        schema = generator.get_schema(request=request)

        return response.Response(schema)
