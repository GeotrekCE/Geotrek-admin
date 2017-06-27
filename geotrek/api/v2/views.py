from __future__ import unicode_literals

from django.conf import settings
from django.db.models.aggregates import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, response
from rest_framework.decorators import detail_route
from rest_framework.generics import get_object_or_404
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework_gis.filters import InBBOXFilter, DistanceToPointFilter

from geotrek.api.v2 import serializers as api_serializers, viewsets as api_viewsets
from geotrek.tourism import models as tourism_models
from geotrek.trekking import models as trekking_models


class TouristicContentViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing accounts.
    """
    queryset = tourism_models.TouristicContent.objects.filter(deleted=False, published=True) \
        .select_related('category') \
        .transform(settings.API_SRID, field_name='geom')
    filter_backends = (DjangoFilterBackend, InBBOXFilter, DistanceToPointFilter)
    filter_fields = ('category', 'published')

    distance_filter_field = 'geom'

    def get_serializer_class(self):
        """
        Obtain serializer switch List/Detail or GeoJSON / Simple JSON
        :return:
        """
        format = self.request.query_params.get('format', None)

        if self._is_request_to_detail_endpoint():
            if format == 'geojson':
                return api_serializers.TouristicContentGeoDetailSerializer

            else:
                return api_serializers.TouristicContentDetailSerializer
        else:
            if format == 'geojson':
                return api_serializers.TouristicContentGeoSerializer

            else:
                return api_serializers.TouristicContentSerializer


class TrekViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekListSerializer
    serializer_detail_class = api_serializers.TrekDetailSerializer
    queryset = trekking_models.Trek.objects.filter(deleted=False) \
        .select_related('topo_object', 'difficulty') \
        .prefetch_related('topo_object__aggregations', 'themes', 'networks', 'attachments') \
        .transform(settings.API_SRID, field_name='geom')
    filter_fields = ('difficulty', 'published', 'themes', 'networks')

    @detail_route(methods=['get'])
    def touristiccontent(self, request, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=kwargs.get('pk'))
        qs = instance.touristic_contents
        qs = qs.prefetch_related('themes', )
        data = api_serializers.TouristicContentDetailSerializer(instance.touristic_contents, many=True).data
        return response.Response(data)


class RoamingViewSet(TrekViewSet):
    serializer_class = api_serializers.RoamingListSerializer
    serializer_detail_class = api_serializers.RoamingDetailSerializer
    filter_fields = ('themes', 'networks', 'accessibilities', 'published', 'practice', 'difficulty')

    def get_queryset(self, *args, **kwargs):
        qs = super(RoamingViewSet, self).get_queryset(*args, **kwargs)
        # keep only treks with child
        qs = qs.annotate(count_childs=Count('trek_children')) \
            .filter(count_childs__gt=0)
        # prefetch m2m
        qs = qs.prefetch_related('themes', 'networks', 'accessibilities', )
        # prefetch FK
        qs = qs.select_related('practice', 'difficulty')
        # transform
        qs = qs.transform(settings.API_SRID, field_name='geom')
        return qs


class POIViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.POIListSerializer
    serializer_detail_class = api_serializers.POIDetailSerializer
    queryset = trekking_models.POI.objects.filter(deleted=False) \
        .select_related('topo_object', 'type', )
    queryset_detail = queryset.transform(settings.API_SRID, field_name='geom')
    filter_fields = ('type', 'published')

