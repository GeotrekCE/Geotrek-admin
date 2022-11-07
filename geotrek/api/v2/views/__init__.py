from rest_framework import response, permissions
from rest_framework.views import APIView

from django.conf import settings
from django.contrib.gis.geos import Polygon

from geotrek import __version__
from .authent import StructureViewSet  # noqa
from .common import TargetPortalViewSet, ThemeViewSet, SourceViewSet, ReservationSystemViewSet, LabelViewSet, OrganismViewSet, FileTypeViewSet, HDViewPointViewSet  # noqa
if 'geotrek.core' in settings.INSTALLED_APPS:
    from .core import PathViewSet  # noqa
if 'geotrek.feedback' in settings.INSTALLED_APPS:
    from .feedback import ReportStatusViewSet, ReportActivityViewSet, ReportCategoryViewSet, ReportProblemMagnitudeViewSet  # noqa
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from .trekking import (TrekViewSet, TourViewSet, POIViewSet, POITypeViewSet, AccessibilityViewSet, RouteViewSet,  # noqa
                           DifficultyViewSet, NetworkViewSet, PracticeViewSet, AccessibilityLevelViewSet,  # noqa
                           WebLinkCategoryViewSet, ServiceTypeViewSet, ServiceViewSet, TrekRatingScaleViewSet, TrekRatingViewSet) # noqa
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from .sensitivity import SensitiveAreaViewSet  # noqa
    from .sensitivity import SportPracticeViewSet  # noqa
    from .sensitivity import SpeciesViewSet  # noqa
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from .tourism import TouristicContentViewSet, TouristicEventViewSet, TouristicEventTypeViewSet, InformationDeskViewSet, InformationDeskTypeViewSet, TouristicContentCategoryViewSet, LabelAccessibilityViewSet, TouristicEventPlaceViewSet  # noqa
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    from .zoning import CityViewSet, DistrictViewSet  # noqa
if 'geotrek.outdoor' in settings.INSTALLED_APPS:
    from .outdoor import (SiteViewSet, OutdoorPracticeViewSet, SiteTypeViewSet, CourseTypeViewSet,  # noqa
                          OutdoorRatingScaleViewSet, OutdoorRatingViewSet, CourseViewSet, SectorViewSet)  # noqa
if 'geotrek.flatpages' in settings.INSTALLED_APPS:
    from .flatpages import FlatPageViewSet  # noqa
if 'geotrek.infrastructure' in settings.INSTALLED_APPS:
    from .infrastructure import InfrastructureTypeViewSet, InfrastructureViewSet, InfrastructureUsageDifficultyLevelViewSet, InfrastructureConditionViewSet, InfrastructureMaintenanceDifficultyLevelViewSet  # noqa
if 'geotrek.signage' in settings.INSTALLED_APPS:
    from .signage import SignageViewSet, SignageTypeViewSet, SealingViewSet, ColorViewSet, DirectionViewSet, BladeTypeViewSet  # noqa
if 'drf_yasg' in settings.INSTALLED_APPS:
    from .swagger import schema_view  # noqa


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


class GeotrekVersionAPIView(APIView):
    permission_classes = [permissions.AllowAny, ]

    def get(self, request, *args, **kwargs):
        return response.Response({'version': __version__})
