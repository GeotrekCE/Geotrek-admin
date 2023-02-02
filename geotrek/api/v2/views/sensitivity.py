from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import F, Case, When, Prefetch
from django_filters.rest_framework.backends import DjangoFilterBackend

from geotrek.common.models import Attachment
from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets
from geotrek.common.functions import GeometryType, Buffer, Area
from geotrek.sensitivity import models as sensitivity_models
from ..filters import GeotrekQueryParamsFilter, GeotrekQueryParamsDimensionFilter, GeotrekInBBoxFilter, GeotrekSensitiveAreaFilter, NearbyContentFilter, UpdateOrCreateDateFilter


class SensitiveAreaViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = (
        DjangoFilterBackend,
        GeotrekQueryParamsFilter,
        GeotrekQueryParamsDimensionFilter,
        GeotrekInBBoxFilter,
        GeotrekSensitiveAreaFilter,
        NearbyContentFilter,
        UpdateOrCreateDateFilter,
    )
    bbox_filter_field = 'geom_transformed'
    bbox_filter_include_overlapping = True

    def get_serializer_class(self):
        if 'bubble' in self.request.GET:
            base_serializer_class = api_serializers.BubbleSensitiveAreaSerializer
        else:
            base_serializer_class = api_serializers.SensitiveAreaSerializer
        format_output = self.request.query_params.get('format', 'json')
        return api_serializers.override_serializer(format_output, base_serializer_class)

    def get_queryset(self):
        queryset = (
            sensitivity_models.SensitiveArea.objects.existing()
            .filter(published=True)
            .select_related('species', 'structure')
            .prefetch_related(
                'species__practices',
                'labels',
                Prefetch('attachments', queryset=Attachment.objects.select_related('license', 'filetype', 'filetype__structure'))
            )
            .alias(geom_type=GeometryType(F('geom')))
        )
        if 'bubble' in self.request.GET:
            queryset = queryset.annotate(geom_transformed=Transform(F('geom'), settings.API_SRID))
        else:
            queryset = queryset.annotate(geom_transformed=Case(
                When(geom_type='POINT', then=Transform(Buffer(F('geom'), F('species__radius'), 4), settings.API_SRID)),
                default=Transform(F('geom'), settings.API_SRID)
            ))
        # Ensure smaller areas are at the end of the list, ie above bigger areas on the map
        # to ensure we can select every area in case of overlapping
        # Second sort key pk is required for reliable pagination
        queryset = queryset.order_by(Area('geom_transformed').desc(), 'pk')
        return queryset.defer('geom')


class SportPracticeViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.SportPracticeSerializer

    def get_queryset(self):
        queryset = sensitivity_models.SportPractice.objects.all()
        queryset = queryset.order_by('pk')  # Required for reliable pagination
        return queryset


class SpeciesViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.SpeciesSerializer

    def get_queryset(self):
        queryset = sensitivity_models.Species.objects.all()
        queryset = queryset.order_by('pk')  # Required for reliable pagination
        return queryset
