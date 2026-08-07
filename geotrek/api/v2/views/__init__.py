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
from .core import PathViewSet  # noqa
from .feedback import (
    ReportActivityViewSet,  # noqa
    ReportCategoryViewSet,  # noqa
    ReportProblemMagnitudeViewSet,  # noqa
    ReportStatusViewSet,  # noqa
    ReportViewSet,  # noqa
)
from .flatpages import FlatPageViewSet, MenuItemRetrieveView, MenuItemTreeView  # noqa
from .infrastructure import (
    InfrastructureConditionViewSet,  # noqa
    InfrastructureMaintenanceDifficultyLevelViewSet,  # noqa
    InfrastructureTypeViewSet,  # noqa
    InfrastructureUsageDifficultyLevelViewSet,  # noqa
    InfrastructureViewSet,  # noqa
)
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
from .sensitivity import (
    SensitiveAreaViewSet,  # noqa
    SpeciesViewSet,  # noqa
    SportPracticeViewSet,  # noqa
)
from .signage import (
    BladeTypeViewSet,  # noqa
    ColorViewSet,  # noqa
    DirectionViewSet,  # noqa
    SealingViewSet,  # noqa
    SignageConditionViewSet,  # noqa
    SignageTypeViewSet,  # noqa
    SignageViewSet,  # noqa
)
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
from .zoning import CityViewSet, DistrictViewSet  # noqa

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
