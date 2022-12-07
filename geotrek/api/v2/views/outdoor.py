from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import F
from django.db.models.query import Prefetch
from django.utils.translation import activate

from geotrek.api.v2 import serializers as api_serializers, \
    filters as api_filters, viewsets as api_viewsets
from geotrek.common.models import Attachment
from geotrek.outdoor import models as outdoor_models


class SiteViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (
        api_filters.GeotrekSiteFilter,
        api_filters.NearbyContentFilter,
        api_filters.UpdateOrCreateDateFilter,
        api_filters.GeotrekRatingsFilter
    )
    serializer_class = api_serializers.SiteSerializer

    def get_queryset(self):
        activate(self.request.GET.get('language'))
        return outdoor_models.Site.objects \
            .annotate(geom_transformed=Transform(F('geom'), settings.API_SRID)) \
            .prefetch_related(Prefetch('attachments',
                                       queryset=Attachment.objects.select_related('license', 'filetype', 'filetype__structure'))) \
            .order_by('name')  # Required for reliable pagination


class OutdoorPracticeViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (
        api_filters.SiteRelatedPortalFilter,
    )
    serializer_class = api_serializers.OutdoorPracticeSerializer
    queryset = outdoor_models.Practice.objects \
        .order_by('pk')  # Required for reliable pagination


class SectorViewSet(api_viewsets.GeotrekGeometricViewset):
    serializer_class = api_serializers.SectorSerializer
    queryset = outdoor_models.Sector.objects \
        .order_by('pk')  # Required for reliable pagination


class SiteTypeViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (
        api_filters.SiteRelatedPortalFilter,
    )
    serializer_class = api_serializers.SiteTypeSerializer
    queryset = outdoor_models.SiteType.objects \
        .order_by('pk')  # Required for reliable pagination


class CourseTypeViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (
        api_filters.CourseRelatedPortalFilter,
    )
    serializer_class = api_serializers.CourseTypeSerializer
    queryset = outdoor_models.CourseType.objects \
        .order_by('pk')  # Required for reliable pagination


class OutdoorRatingScaleViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.GeotrekRatingScaleFilter, )
    serializer_class = api_serializers.OutdoorRatingScaleSerializer
    queryset = outdoor_models.RatingScale.objects \
        .order_by('pk')  # Required for reliable pagination


class OutdoorRatingViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (
        api_filters.GeotrekRatingFilter,
        api_filters.SiteRelatedPortalFilter,
    )
    serializer_class = api_serializers.OutdoorRatingSerializer
    queryset = outdoor_models.Rating.objects \
        .order_by('order', 'name', 'pk')  # Required for reliable pagination


class CourseViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (
        api_filters.GeotrekCourseFilter,
        api_filters.NearbyContentFilter,
        api_filters.UpdateOrCreateDateFilter,
        api_filters.GeotrekRatingsFilter
    )
    serializer_class = api_serializers.CourseSerializer

    def get_queryset(self):
        activate(self.request.GET.get('language'))
        return outdoor_models.Course.objects \
            .annotate(geom_transformed=Transform(F('geom'), settings.API_SRID)) \
            .prefetch_related(Prefetch('attachments',
                                       queryset=Attachment.objects.select_related('license', 'filetype', 'filetype__structure'))) \
            .order_by('name')  # Required for reliable pagination
