from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.gis.geos import Polygon
from rest_framework import permissions, response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from geotrek import __version__
from geotrek.authent.models import UserProfile

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

    models = {
        "signage": [
            ("signage", "signage"),
            ("signage", "direction"),
            ("signage", "sealing"),
            ("signage", "signagecondition"),
            ("signage", "signagetype"),
            ("signage", "blade"),
            ("signage", "bladecondition"),
            ("signage", "bladetype"),
            ("signage", "color"),
            ("signage", "line"),
            ("signage", "linepictogram"),
        ],
        "infrastructure": [
            ("infrastructure", "infrastructure"),
            ("infrastructure", "infrastructurecondition"),
            ("infrastructure", "infrastructuretype"),
            ("infrastructure", "infrastructureaccessmean"),
            ("infrastructure", "infrastructuremaintenancedifficultylevel"),
            ("infrastructure", "infrastructureusagedifficultylevel"),
        ],
        "intervention": [
            ("maintenance", "intervention"),
            ("maintenance", "interventiondisorder"),
            ("maintenance", "interventionjob"),
            ("maintenance", "interventionstatus"),
            ("maintenance", "interventiontype"),
            ("maintenance", "manday"),
            ("maintenance", "contractor"),
            ("maintenance", "funding"),
        ],
        "report": [
            ("feedback", "report"),
            ("feedback", "attachedmessage"),
            ("feedback", "pendingemail"),
            ("feedback", "predefinedemail"),
            ("feedback", "reportactivity"),
            ("feedback", "reportcategory"),
            ("feedback", "reportproblemmagnitude"),
            ("feedback", "reportstatus"),
            ("feedback", "selectableuser"),
            ("feedback", "timerevent"),
            ("feedback", "workflowdistrict"),
            ("feedback", "workflowmanager"),
        ],
    }

    def get_model_permissions(self, user, model):
        app_label, model_name = model

        return {
            perm.codename.replace(f"_{model_name}", ""): user.has_perm(
                f"{app_label}.{perm.codename}"
            )
            for perm in Permission.objects.filter(
                content_type__app_label=app_label, content_type__model=model_name
            )
        }

    def get_all_permissions(self, user):
        permissions = {}
        for module, models in self.models.items():
            module_permissions = {}
            for model in models:
                module_permissions[model[1]] = self.get_model_permissions(user, model)
            permissions[module] = module_permissions
        return permissions

    def get(self, request, *args, **kwargs):
        user = request.user
        user_profile = UserProfile.objects.get(user=user)

        # convert SPATIAL_EXTENT projection to 4326
        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID
        bbox.transform(settings.API_SRID)
        west, south, east, north = bbox.extent

        max_bounds = [[west, south], [east, north]]
        center = [(west + east) / 2, (south + north) / 2]
        data = {
            "settings": {
                "language": "fr",
                "intervalSyncInHours": {
                    "references": 24 * 7,  # move settings in database
                },
                "maps": {
                    "layers": [
                        {
                            "pmtiles_url": "https://fake.urls.com/pmtiles",
                            "json_style_url": "https://fake.urls.com/json_style",
                            "name": "Scan IGN VT",
                            "options": {
                                "attribution": "© IGN - GeoPortail",
                                "center": center,
                                "maxBounds": max_bounds,
                                "maxZoom": 15,  # use pmtiles metadata: https://github.com/protomaps/PMTiles/blob/0cebcaeade40034b86facb6e7da4ec726b9053fb/python/pmtiles/pmtiles/reader.py#L37-L42
                                "minZoom": 0,  # use pmtiles metadata: https://github.com/protomaps/PMTiles/blob/0cebcaeade40034b86facb6e7da4ec726b9053fb/python/pmtiles/pmtiles/reader.py#L37-L42
                                "zoom": 0,
                            },
                        }
                    ]
                },
            },
            "user": {
                "rights": self.get_all_permissions(user),
                "structure": {
                    "id": user_profile.structure.id,
                    "label": user_profile.structure.name,
                },
            },
        }
        return response.Response(data)


class GeotrekVersionAPIView(APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request, *args, **kwargs):
        return response.Response({"version": __version__})
