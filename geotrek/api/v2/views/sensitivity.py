from django.conf import settings
from django.db.models import F, Case, When
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets
from geotrek.api.v2.functions import Transform, Buffer, GeometryType, Area
from geotrek.sensitivity import models as sensitivity_models
from ..filters import GeotrekQueryParamsFilter, GeotrekInBBoxFilter, GeotrekSensitiveAreaFilter


class SensitiveAreaViewSet(api_viewsets.GeotrekViewset):
    filter_backends = (
        DjangoFilterBackend,
        GeotrekQueryParamsFilter,
        GeotrekInBBoxFilter,
        GeotrekSensitiveAreaFilter,
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = []
    bbox_filter_field = 'geom2d_transformed'
    bbox_filter_include_overlapping = True

    def get_serializer_class(self):
        if 'bubble' in self.request.GET:
            base_serializer_class = api_serializers.BubbleSensitiveAreaListSerializer
        else:
            base_serializer_class = api_serializers.SensitiveAreaListSerializer
        format_output = self.request.query_params.get('format', 'json')
        dimension = self.request.query_params.get('dim', '2')
        return api_serializers.override_serializer(format_output, dimension, base_serializer_class)

    def get_queryset(self):
        queryset = sensitivity_models.SensitiveArea.objects.existing() \
            .filter(published=True) \
            .select_related('species', 'structure') \
            .prefetch_related('species__practices') \
            .annotate(geom_type=GeometryType(F('geom'))) \
            .order_by('pk')  # Required for reliable pagination
        if 'bubble' in self.request.GET:
            queryset = queryset.annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID))
        else:
            queryset = queryset.annotate(geom2d_transformed=Case(
                When(geom_type='POINT', then=Transform(Buffer(F('geom'), F('species__radius'), 4), settings.API_SRID)),
                When(geom_type='POLYGON', then=Transform(F('geom'), settings.API_SRID))
            ))
        # Ensure smaller areas are at the end of the list, ie above bigger areas on the map
        # to ensure we can select every area in case of overlapping
        queryset = queryset.annotate(area=Area('geom2d_transformed')).order_by('-area')
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(SensitiveAreaViewSet, self).list(request, *args, **kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        return response


class SportPracticeViewSet(api_viewsets.GeotrekViewset):
    filter_backends = (
        DjangoFilterBackend,
        GeotrekQueryParamsFilter,
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = api_serializers.SportPracticeListSerializer
    serializer_detail_class = api_serializers.SportPracticeListSerializer
    authentication_classes = []

    def get_queryset(self):
        queryset = sensitivity_models.SportPractice.objects.all()
        queryset = queryset.order_by('pk')  # Required for reliable pagination
        return queryset

    def list(self, request, *args, **kwargs):
        response = super(SportPracticeViewSet, self).list(request, *args, **kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        return response
