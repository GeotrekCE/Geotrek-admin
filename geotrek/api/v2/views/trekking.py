from django.conf import settings
from django.db.models import F
from django.db.models.aggregates import Count

from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets, filters as api_filters
from geotrek.api.v2.functions import Transform, Length, Length3D
from geotrek.trekking import models as trekking_models


class TrekViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = tuple((e for e in api_viewsets.GeotrekGeometricViewset.filter_backends)) + (api_filters.GeotrekTrekQueryParamsFilter,)
    serializer_class = api_serializers.TrekSerializer
    queryset = trekking_models.Trek.objects.existing() \
        .select_related('topo_object') \
        .prefetch_related('topo_object__aggregations', 'accessibilities', 'attachments') \
        .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID),
                  geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID),
                  length_2d_m=Length('geom'),
                  length_3d_m=Length3D('geom_3d')) \
        .order_by('pk')  # Required for reliable pagination


class TourViewSet(TrekViewSet):
    serializer_class = api_serializers.TourSerializer
    queryset = TrekViewSet.queryset.annotate(count_children=Count('trek_children')) \
        .filter(count_children__gt=0)


class PracticeViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekPracticeSerializer
    queryset = trekking_models.Practice.objects.all()


class NetworksViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekNetworkSerializer
    queryset = trekking_models.TrekNetwork.objects.all()


class DifficultyViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekDifficultySerializer
    queryset = trekking_models.DifficultyLevel.objects.all()


class POIViewSet(api_viewsets.GeotrekGeometricViewset):
    serializer_class = api_serializers.POISerializer
    queryset = trekking_models.POI.objects.existing() \
        .select_related('topo_object', 'type', ) \
        .prefetch_related('topo_object__aggregations', 'attachments') \
        .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID),
                  geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID)) \
        .order_by('pk')  # Required for reliable pagination
    filterset_fields = ('type',)


class POITypesViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.POITypeSerializer
    queryset = trekking_models.POIType.objects.all()


class AccessibilityViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.AccessibilitySerializer
    queryset = trekking_models.Accessibility.objects.all()


class RouteViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.RouteSerializer
    queryset = trekking_models.Route.objects.all()
