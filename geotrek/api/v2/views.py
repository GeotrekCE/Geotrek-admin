from django.db.models.aggregates import Count

from geotrek.tourism import models as tourism_models
from geotrek.trekking import models as trekking_models
from rest_framework import viewsets
from geotrek.api.v2 import serializers as api_serializers
from rest_framework_extensions.mixins import DetailSerializerMixin
from django.conf import settings


class TouristicContentViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing accounts.
    """
    queryset = tourism_models.TouristicContent.objects.filter(deleted=False).select_related('category').transform(settings.API_SRID, field_name='geom')
    queryset_detail = queryset.prefetch_related('groups__permissions')
    serializer_class = api_serializers.TouristicContentSerializer
    serializer_detail_class = api_serializers.TouristicContentDetailSerializer


class TrekViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = trekking_models.Trek.objects.filter(deleted=False)\
                                           .select_related('topo_object', 'difficulty')
    queryset_detail = queryset.prefetch_related('themes', 'networks').transform(settings.API_SRID, field_name='geom')
    serializer_class = api_serializers.TrekListSerializer
    serializer_detail_class = api_serializers.TrekDetailSerializer


class RoamingViewSet(TrekViewSet):
    serializer_class = api_serializers.TrekListSerializer
    serializer_detail_class = api_serializers.ItineranceDetailSerializer

    def get_queryset(self, *args, **kwargs):
        qs = super(RoamingViewSet, self).get_queryset(*args, **kwargs)
        return qs.annotate(count_childs=Count('trek_children')) \
                 .filter(count_childs__gt=0)


class POIViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    queryset = trekking_models.POI.objects.filter(deleted=False)\
                                          .select_related('topo_object',)
    queryset_detail = queryset.transform(settings.API_SRID, field_name='geom')
    serializer_class = api_serializers.POIListSerializer
    serializer_detail_class = api_serializers.POIListSerializer