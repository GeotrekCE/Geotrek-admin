from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Polygon
from rest_framework import permissions, response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

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


class GTAMConfigView(APIView):
    """GTAM Configuration endpoint that gives information on: the user, default language, map, ..."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_model_permissions(self, user, model):
        app_label = model[0]
        model_name = model[1]

        all_permissions = Permission.objects.filter(
            content_type__app_label=app_label, content_type__model=model_name
        )
        permissions_name = [
            perm.codename.replace(f"_{model_name}", "") for perm in all_permissions
        ]

        return {
            perm_name: user.has_perm(perm.codename)
            for perm_name, perm in zip(permissions_name, all_permissions)
        }

    def get(self, request, *args, **kwargs):
        data = {
            "settings": {
                "language": "fr",
                "intervalSync": {
                    "references": 24 * 7,  # move settings in database
                },
                "maps": {
                    "layers": [
                        {
                            "pmtiles_url": "https://fake.urls.com/pmtiles",
                            "json_style_url": "https://fake.urls.com/json_style",
                            "name": "Scan IGN VT",
                            "options": {
                                "center": [6.2278745, 44.8030050],
                                "maxBounds": [
                                    [5.7236380, 44.3790430],
                                    [6.7321110, 45.2269670],
                                ],
                                "maxZoom": 15,
                                "minZoom": 0,
                                "zoom": 10,
                            },
                        }
                    ]
                },
                "rights": {
                    "signage": self.get_model_permissions(
                        request.user, ("signage", "signage")
                    ),
                    "infrastructure": self.get_model_permissions(
                        request.user, ("infrastructure", "infrastructure")
                    ),
                    "intervention": self.get_model_permissions(
                        request.user, ("maintenance", "intervention")
                    ),
                    "report": self.get_model_permissions(
                        request.user, ("feedback", "report")
                    ),
                },
            }
        }
        return response.Response(data)


class GeotrekVersionAPIView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request, *args, **kwargs):
        return response.Response({"version": __version__})
