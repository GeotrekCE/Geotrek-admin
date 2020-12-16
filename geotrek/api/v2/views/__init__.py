from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import response, permissions
from rest_framework.views import APIView

from django.conf import settings
from django.contrib.gis.geos import Polygon
from .authent import StructureViewSet  # noqa
from .common import TargetPortalViewSet, ThemeViewSet, SourceViewSet, ReservationSystemViewSet, LabelViewSet  # noqa
if 'geotrek.core' in settings.INSTALLED_APPS:
    from .core import PathViewSet  # noqa
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from .trekking import TrekViewSet, TourViewSet, POIViewSet, POITypeViewSet, AccessibilityViewSet, RouteViewSet, DifficultyViewSet, NetworksViewSet, PracticeViewSet  # noqa
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from .sensitivity import SensitiveAreaViewSet  # noqa
    from .sensitivity import SportPracticeViewSet  # noqa
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from .tourism import TouristicContentViewSet, InformationDeskViewSet  # noqa
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    from .zoning import CityViewSet, DistrictViewSet  # noqa
if 'geotrek.outdoor' in settings.INSTALLED_APPS:
    from .outdoor import SiteViewSet  # noqa


schema_view = get_schema_view(
    openapi.Info(
        title="Geotrek API v2",
        default_version='v2',
        description="New Geotrek API.",
    ),
    urlconf='geotrek.api.v2.urls',
    public=True,
    permission_classes=(permissions.AllowAny,),
)


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
