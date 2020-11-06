from rest_framework import response, permissions
from rest_framework.schemas import SchemaGenerator
from rest_framework.views import APIView
from rest_framework_swagger import renderers

from django.conf import settings
from django.contrib.gis.geos import Polygon
from .authent import StructureViewSet  # noqa
from .common import TargetPortalViewSet, ThemeViewSet  # noqa
if 'geotrek.core' in settings.INSTALLED_APPS:
    from .core import PathViewSet  # noqa
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from .trekking import TrekViewSet, TourViewSet, POIViewSet, POITypeViewSet, AccessibilityViewSet, RouteViewSet, DifficultyViewSet, NetworksViewSet, PracticeViewSet, LabelTrekViewSet  # noqa
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from .sensitivity import SensitiveAreaViewSet  # noqa
    from .sensitivity import SportPracticeViewSet  # noqa
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from .tourism import TouristicContentViewSet, InformationDeskViewSet  # noqa
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    from .zoning import CityViewSet, DistrictViewSet  # noqa


class SwaggerSchemaView(APIView):
    permission_classes = (permissions.AllowAny,)
    renderer_classes = [
        renderers.OpenAPIRenderer,
        renderers.SwaggerUIRenderer,
    ]

    def get(self, request):
        generator = SchemaGenerator(
            title='Geotrek API v2',
            urlconf='geotrek.api.v2.urls',
            url='/api/v2',
            description="New Geotrek API."
        )
        schema = generator.get_schema(request=request)

        return response.Response(schema)


class ConfigView(APIView):
    """
    Configuration endpoint that gives the BBox used in the Geotrek configuration
    """
    permission_classes = [permissions.AllowAny, ]

    def get(self, request, *args, **kwargs):
        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID
        bbox.transform(settings.API_SRID)
        return response.Response({
            'bbox': bbox.extent
        })
