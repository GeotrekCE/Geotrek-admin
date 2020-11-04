from django.conf import settings
from django.db.models import F
from django.db.models.aggregates import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import decorators
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets, filters as api_filters
from geotrek.api.v2.functions import Transform, Length, Length3D
from geotrek.trekking import models as trekking_models


class TrekViewSet(api_viewsets.GeotrekViewset):
    filter_backends = (DjangoFilterBackend,
                       api_filters.GeotrekQueryParamsFilter,
                       api_filters.GeotrekInBBoxFilter,
                       api_filters.GeotrekDistanceToPointFilter,
                       api_filters.GeotrekPublishedFilter,
                       api_filters.GeotrekTrekQueryParamsFilter)
    serializer_class = api_serializers.TrekListSerializer
    serializer_detail_class = api_serializers.TrekDetailSerializer
    queryset = trekking_models.Trek.objects.existing() \
        .select_related('topo_object', 'difficulty', 'practice') \
        .prefetch_related('topo_object__aggregations', 'themes', 'accessibilities', 'networks', 'attachments') \
        .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID),
                  geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID),
                  length_2d_m=Length('geom'),
                  length_3d_m=Length3D('geom_3d')) \
        .order_by('pk')  # Required for reliable pagination
    filterset_fields = ('difficulty', 'themes', 'networks', 'practice')


class TourViewSet(TrekViewSet):
    serializer_class = api_serializers.TourListSerializer
    serializer_detail_class = api_serializers.TourDetailSerializer
    queryset = TrekViewSet.queryset.annotate(count_children=Count('trek_children')) \
        .filter(count_children__gt=0)


class PracticeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = api_serializers.TrekPracticeSerializer
    serializer_detail_class = api_serializers.TrekPracticeInTrekSerializer
    queryset = trekking_models.Practice.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class NetworksViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = api_serializers.TrekNetworkSerializer
    serializer_detail_class = api_serializers.TrekNetworkSerializer
    queryset = trekking_models.TrekNetwork.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class DifficultyViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = api_serializers.TrekDifficultySerializer
    serializer_detail_class = api_serializers.TrekDifficultySerializer
    queryset = trekking_models.DifficultyLevel.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class POIViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.POIListSerializer
    serializer_detail_class = api_serializers.POIDetailSerializer
    queryset = trekking_models.POI.objects.existing() \
        .select_related('topo_object', 'type', ) \
        .prefetch_related('topo_object__aggregations', 'attachments') \
        .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID),
                  geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID)) \
        .order_by('pk')  # Required for reliable pagination
    filterset_fields = ('type',)


class POITypesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = api_serializers.POITypeSerializer
    serializer_detail_class = api_serializers.POITypeSerializer
    queryset = trekking_models.POIType.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class AccessibilityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = api_serializers.AccessibilitySerializer
    serializer_detail_class = api_serializers.AccessibilitySerializer
    queryset = trekking_models.Accessibility.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]


class RouteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = api_serializers.RouteSerializer
    serializer_detail_class = api_serializers.RouteSerializer
    queryset = trekking_models.Route.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
