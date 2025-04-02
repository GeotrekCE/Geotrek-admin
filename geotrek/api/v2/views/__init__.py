from django.conf import settings
from django.contrib.gis.geos import Polygon
from rest_framework import permissions, response
from rest_framework.views import APIView

from geotrek import __version__

from .authent import StructureViewSet  # noqa
from .common import (
    AnnotationCategoryViewSet,  # noqa
    FileTypeViewSet,  # noqa
    HDViewPointViewSet,  # noqa
    LabelViewSet,  # noqa
    OrganismViewSet,  # noqa
    ReservationSystemViewSet,  # noqa
    SourceViewSet,  # noqa
    TargetPortalViewSet,  # noqa
    ThemeViewSet,  # noqa
)

if "geotrek.core" in settings.INSTALLED_APPS:
    from .core import PathViewSet  # noqa
if "geotrek.feedback" in settings.INSTALLED_APPS:
    from .feedback import (
        ReportActivityViewSet,  # noqa
        ReportCategoryViewSet,  # noqa
        ReportProblemMagnitudeViewSet,  # noqa
        ReportStatusViewSet,  # noqa
        ReportViewSet,  # noqa
    )
if "geotrek.trekking" in settings.INSTALLED_APPS:
    from .trekking import (
        AccessibilityLevelViewSet,  # noqa
        AccessibilityViewSet,  # noqa
        DifficultyViewSet,  # noqa
        NetworkViewSet,  # noqa
        POITypeViewSet,  # noqa
        POIViewSet,  # noqa
        PracticeViewSet,  # noqa
        RouteViewSet,  # noqa
        ServiceTypeViewSet,  # noqa
        ServiceViewSet,  # noqa
        TourViewSet,  # noqa
        TrekRatingScaleViewSet,  # noqa
        TrekRatingViewSet,  # noqa
        TrekViewSet,  # noqa
        WebLinkCategoryViewSet,  # noqa
    )
if "geotrek.sensitivity" in settings.INSTALLED_APPS:
    from .sensitivity import SensitiveAreaViewSet  # noqa
    from .sensitivity import SportPracticeViewSet  # noqa
    from .sensitivity import SpeciesViewSet  # noqa
if "geotrek.tourism" in settings.INSTALLED_APPS:
    from .tourism import (
        InformationDeskTypeViewSet,  # noqa
        InformationDeskViewSet,  # noqa
        LabelAccessibilityViewSet,  # noqa
        TouristicContentCategoryViewSet,  # noqa
        TouristicContentViewSet,  # noqa
        TouristicEventOrganizerViewSet,  # noqa
        TouristicEventPlaceViewSet,  # noqa
        TouristicEventTypeViewSet,  # noqa
        TouristicEventViewSet,  # noqa
    )
if "geotrek.zoning" in settings.INSTALLED_APPS:
    from .zoning import CityViewSet, DistrictViewSet  # noqa
if "geotrek.outdoor" in settings.INSTALLED_APPS:
    from .outdoor import (
        CourseTypeViewSet,  # noqa
        CourseViewSet,  # noqa
        OutdoorPracticeViewSet,  # noqa
        OutdoorRatingScaleViewSet,  # noqa
        OutdoorRatingViewSet,  # noqa
        SectorViewSet,  # noqa
        SiteTypeViewSet,  # noqa
        SiteViewSet,  # noqa
    )
if "geotrek.flatpages" in settings.INSTALLED_APPS:
    from .flatpages import MenuItemTreeView, FlatPageViewSet, MenuItemRetrieveView  # noqa
if "geotrek.infrastructure" in settings.INSTALLED_APPS:
    from .infrastructure import (
        InfrastructureConditionViewSet,  # noqa
        InfrastructureMaintenanceDifficultyLevelViewSet,  # noqa
        InfrastructureTypeViewSet,  # noqa
        InfrastructureUsageDifficultyLevelViewSet,  # noqa
        InfrastructureViewSet,  # noqa
    )
if "geotrek.signage" in settings.INSTALLED_APPS:
    from .signage import (
        BladeTypeViewSet,  # noqa
        ColorViewSet,  # noqa
        DirectionViewSet,  # noqa
        SealingViewSet,  # noqa
        SignageConditionViewSet,  # noqa
        SignageTypeViewSet,  # noqa
        SignageViewSet,  # noqa
    )
if "drf_yasg" in settings.INSTALLED_APPS:
    from .swagger import schema_view  # noqa


class ConfigView(APIView):
    """Configuration endpoint that gives the BBox used in the Geotrek configuration"""

    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request, *args, **kwargs):
        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID
        bbox.transform(settings.API_SRID)
        return response.Response({"bbox": bbox.extent})


class GeotrekVersionAPIView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request, *args, **kwargs):
        return response.Response({"version": __version__})
