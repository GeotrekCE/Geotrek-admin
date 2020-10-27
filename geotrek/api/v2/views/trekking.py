from django.conf import settings
from django.db.models import F
from django.db.models.aggregates import Count
from django.http import HttpResponseRedirect
from django.urls import reverse
from rest_framework import response, decorators
from django_filters.rest_framework.backends import DjangoFilterBackend

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

    @decorators.action(detail=False, methods=['get'])
    def practices(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('apiv2:practice-list', args=args))

    @decorators.action(detail=False, methods=['get'])
    def networks(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('apiv2:network-list', args=args))

    @decorators.action(detail=False, methods=['get'])
    def difficulties(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse('apiv2:difficulty-list', args=args))


class TourViewSet(TrekViewSet):
    serializer_class = api_serializers.TourListSerializer
    serializer_detail_class = api_serializers.TourDetailSerializer
    queryset = TrekViewSet.queryset.annotate(count_children=Count('trek_children')) \
        .filter(count_children__gt=0)


class PracticeViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekPracticeSerializer
    serializer_detail_class = api_serializers.TrekPracticeInTrekSerializer
    queryset = trekking_models.Practice.objects.all()


class NetworksViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekNetworkSerializer
    serializer_detail_class = api_serializers.TrekNetworkSerializer
    queryset = trekking_models.TrekNetwork.objects.all()


class DifficultyViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekDifficultySerializer
    serializer_detail_class = api_serializers.TrekDifficultySerializer
    queryset = trekking_models.DifficultyLevel.objects.all()


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

    @decorators.action(detail=False, methods=['get'])
    def all_types(self, request, *args, **kwargs):
        """
        Get all POI types
        """
        data = api_serializers.POITypeSerializer(trekking_models.POIType.objects.all(),
                                                 many=True,
                                                 context={'request': request}).data
        return response.Response(data)

    @decorators.action(detail=False, methods=['get'])
    def used_types(self, request, *args, **kwargs):
        """
        Get POI types used by POI instances
        """
        data = api_serializers.POITypeSerializer(
            trekking_models.POIType.objects.filter(pk__in=trekking_models.POI.objects.existing()
                                                   .values_list('type_id', flat=True)),
            many=True,
            context={'request': request}).data
        return response.Response(data)


class AccessibilityViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.AccessibilitySerializer
    serializer_detail_class = api_serializers.AccessibilitySerializer
    queryset = trekking_models.Accessibility.objects.all()


class RouteViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.RouteSerializer
    serializer_detail_class = api_serializers.RouteSerializer
    queryset = trekking_models.Route.objects.all()
