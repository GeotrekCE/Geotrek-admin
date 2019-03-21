from __future__ import unicode_literals

from django.conf import settings
from django.db.models import F, Q
from django_filters.rest_framework.backends import DjangoFilterBackend

from geotrek.api.mobile.serializers import trekking as api_serializers_trekking
from geotrek.api.mobile.serializers import tourism as api_serializers_tourism

from geotrek.api.v2.functions import Transform, Length, StartPoint, EndPoint
from geotrek.trekking import models as trekking_models

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import response
from rest_framework import viewsets
from rest_framework import decorators


class TrekViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    serializer_class = api_serializers_trekking.TrekListSerializer
    serializer_detail_class = api_serializers_trekking.TrekDetailSerializer
    filter_fields = ('difficulty', 'themes', 'networks', 'practice')
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]

    def get_queryset(self, *args, **kwargs):
        queryset = trekking_models.Trek.objects.existing()\
            .select_related('topo_object') \
            .prefetch_related('topo_object__aggregations', 'attachments') \
            .order_by('pk').annotate(length_2d_m=Length('geom'))
        if not self.action == 'list':
            queryset = queryset.annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID))
        return queryset.annotate(start_point=Transform(StartPoint('geom'), settings.API_SRID),
                                 end_point=Transform(EndPoint('geom'), settings.API_SRID)).\
            filter(Q(**{'published': True}) | Q(**{'trek_parents__parent__published': True,
                                                   'trek_parents__parent__deleted': False})).distinct()

    @decorators.detail_route(methods=['get'])
    def pois(self, request, *args, **kwargs):
        trek = self.get_object()
        qs = trek.pois.filter(published=True).select_related('topo_object', 'type', )\
            .prefetch_related('topo_object__aggregations', 'attachments') \
            .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID)) \
            .order_by('pk')
        data = api_serializers_trekking.POIListSerializer(qs, many=True, context={'trek_pk': trek.pk}).data
        return response.Response(data)

    @decorators.detail_route(methods=['get'])
    def touristic_contents(self, request, *args, **kwargs):
        trek = self.get_object()
        qs = trek.touristic_contents.filter(published=True).prefetch_related('attachments') \
            .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID)) \
            .order_by('pk')
        data = api_serializers_tourism.TouristicContentListSerializer(qs, many=True, context={'trek_pk': trek.pk}).data
        return response.Response(data)

    @decorators.detail_route(methods=['get'])
    def touristic_events(self, request, *args, **kwargs):
        trek = self.get_object()
        qs = trek.trek.touristic_events.filter(published=True).prefetch_related('attachments') \
            .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID)) \
            .order_by('pk')
        data = api_serializers_tourism.TouristicEventListSerializer(qs,  many=True, context={'trek_pk': trek.pk}).data
        return response.Response(data)
