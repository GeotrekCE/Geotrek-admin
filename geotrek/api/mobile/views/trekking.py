from __future__ import unicode_literals

from django.conf import settings
from django.db.models import F
from django_filters.rest_framework.backends import DjangoFilterBackend
from django.http import Http404
from django.utils import translation

from geotrek.api.mobile.serializers import trekking as api_serializers

from geotrek.api.v2.functions import Transform, Length, StartPoint
from geotrek.trekking import models as trekking_models

from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets


class TrekViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    serializer_class = api_serializers.TrekListSerializer
    serializer_detail_class = api_serializers.TrekDetailSerializer
    filter_fields = ('difficulty', 'themes', 'networks', 'practice')
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]

    def dispatch(self, request, *args, **kwargs):
        language = kwargs.get(u'lang')
        translation.activate(language)
        return super(TrekViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        queryset = trekking_models.Trek.objects.existing()\
            .select_related('topo_object') \
            .prefetch_related('topo_object__aggregations', 'attachments') \
            .order_by('pk').annotate(length_2d_m=Length('geom'))
        if self.action == 'list':
            queryset = queryset.annotate(start_point=Transform(StartPoint('geom'), settings.API_SRID))
        else:
            queryset = queryset.annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID))
        return queryset.filter(published=True)


class POIViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    serializer_class = api_serializers.POIListSerializer
    serializer_detail_class = api_serializers.POIListSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    queryset = trekking_models.POI.objects.existing() \
        .select_related('topo_object', 'type', ) \
        .prefetch_related('topo_object__aggregations', 'attachments') \
        .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID),
                  geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID)) \
        .order_by('pk')  # Required for reliable pagination
    filter_fields = ('type',)

    def dispatch(self, request, *args, **kwargs):
        language = kwargs.get(u'lang')
        translation.activate(language)
        return super(POIViewSet, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        pk = self.kwargs['pk']
        try:
            trek = trekking_models.Trek.objects.existing().get(pk=pk)
        except trekking_models.Trek.DoesNotExist:
            raise Http404
        if not trek.is_public:
            raise Http404
        return trek.pois.filter(published=True).select_related('topo_object', 'type', )\
            .prefetch_related('topo_object__aggregations', 'attachments') \
            .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID),
                      geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID)) \
            .order_by('pk')\
            .filter(published=True)
