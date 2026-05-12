from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import F
from django.db.models.query import Prefetch
from django.utils import translation

from geotrek.api.v2 import filters as api_filters
from geotrek.api.v2 import serializers as api_serializers
from geotrek.api.v2 import viewsets as api_viewsets
from geotrek.common.models import Attachment, HDViewPoint
from geotrek.outdoor import models as outdoor_models


class SiteViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = (
        *api_viewsets.GeotrekGeometricViewset.filter_backends,
        api_filters.GeotrekSiteFilter,
        api_filters.NearbyContentFilter,
        api_filters.UpdateOrCreateDateFilter,
        api_filters.GeotrekRatingsFilter,
    )
    serializer_class = api_serializers.SiteSerializer

    def get_queryset(self):
        with translation.override(self.request.GET.get("language"), deactivate=True):
            return (
                outdoor_models.Site.objects.annotate(
                    geom_transformed=Transform(F("geom"), settings.API_SRID)
                )
                .select_related("parent", "practice", "type")
                .prefetch_related(
                    Prefetch(
                        "attachments",
                        queryset=Attachment.objects.select_related(
                            "license", "filetype", "filetype__structure"
                        ),
                    ),
                    Prefetch(
                        "view_points",
                        queryset=HDViewPoint.objects.select_related(
                            "content_type", "license"
                        ).annotate(
                            geom_transformed=Transform(F("geom"), settings.API_SRID)
                        ),
                    ),
                    "information_desks",
                    "labels",
                    "managers",
                    "pois_excluded",
                    "portal",
                    "ratings",
                    "source",
                    "themes",
                    "web_links",
                )
                .order_by("name")
            )  # Required for reliable pagination


class OutdoorPracticeViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = (
        *api_viewsets.GeotrekGeometricViewset.filter_backends,
        api_filters.SiteRelatedPortalFilter,
    )
    serializer_class = api_serializers.OutdoorPracticeSerializer
    queryset = outdoor_models.Practice.objects.order_by(
        "pk"
    )  # Required for reliable pagination


class SectorViewSet(api_viewsets.GeotrekGeometricViewset):
    serializer_class = api_serializers.SectorSerializer
    queryset = outdoor_models.Sector.objects.order_by(
        "pk"
    )  # Required for reliable pagination


class SiteTypeViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = (
        *api_viewsets.GeotrekGeometricViewset.filter_backends,
        api_filters.SiteRelatedPortalFilter,
    )
    serializer_class = api_serializers.SiteTypeSerializer
    queryset = outdoor_models.SiteType.objects.order_by(
        "pk"
    )  # Required for reliable pagination


class CourseTypeViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = (
        *api_viewsets.GeotrekGeometricViewset.filter_backends,
        api_filters.CourseRelatedFilter,
    )
    serializer_class = api_serializers.CourseTypeSerializer
    queryset = outdoor_models.CourseType.objects.order_by(
        "pk"
    )  # Required for reliable pagination


class OutdoorRatingScaleViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = (
        *api_viewsets.GeotrekViewSet.filter_backends,
        api_filters.GeotrekRatingScaleFilter,
    )
    serializer_class = api_serializers.OutdoorRatingScaleSerializer
    queryset = outdoor_models.RatingScale.objects.order_by(
        "pk"
    )  # Required for reliable pagination


class OutdoorRatingViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = (
        *api_viewsets.GeotrekViewSet.filter_backends,
        api_filters.GeotrekRatingFilter,
        api_filters.SitesRelatedPortalAndCourseRelatedFilter,
    )
    serializer_class = api_serializers.OutdoorRatingSerializer
    queryset = outdoor_models.Rating.objects.order_by(
        "order", "name", "pk"
    )  # Required for reliable pagination


class CourseViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = (
        *api_viewsets.GeotrekGeometricViewset.filter_backends,
        api_filters.GeotrekCourseFilter,
        api_filters.NearbyContentFilter,
        api_filters.UpdateOrCreateDateFilter,
        api_filters.GeotrekRatingsFilter,
    )
    serializer_class = api_serializers.CourseSerializer

    def get_queryset(self):
        with translation.override(self.request.GET.get("language"), deactivate=True):
            return (
                outdoor_models.Course.objects.annotate(
                    geom_transformed=Transform(F("geom"), settings.API_SRID)
                )
                .select_related("type")
                .prefetch_related(
                    Prefetch(
                        "attachments",
                        queryset=Attachment.objects.select_related(
                            "license", "filetype", "filetype__structure"
                        ),
                    ),
                    Prefetch(
                        "course_children",
                        queryset=outdoor_models.OrderedCourseChild.objects.select_related(
                            "parent", "child"
                        ),
                    ),
                    Prefetch(
                        "course_parents",
                        queryset=outdoor_models.OrderedCourseChild.objects.select_related(
                            "parent", "child"
                        ),
                    ),
                    "parent_sites",
                    "pois_excluded",
                    "ratings",
                )
                .order_by("name")
            )  # Required for reliable pagination
