from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import Count, F, Q
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework import response, viewsets, decorators
from rest_framework.permissions import AllowAny
from rest_framework_extensions.mixins import DetailSerializerMixin

from geotrek.api.mobile.serializers import trekking as api_serializers_trekking, tourism as api_serializers_tourism
from geotrek.common.functions import StartPoint, EndPoint
from geotrek.trekking import models as trekking_models

if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from geotrek.api.mobile.serializers import sensitivity as api_serializers_sensitivity


class TrekViewSet(DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    serializer_class = api_serializers_trekking.TrekListSerializer
    serializer_detail_class = api_serializers_trekking.TrekDetailSerializer
    filterset_fields = ('difficulty', 'themes', 'networks', 'practice')
    permission_classes = [AllowAny, ]

    def get_queryset(self, *args, **kwargs):
        lang = self.request.LANGUAGE_CODE
        queryset = trekking_models.Trek.objects.existing()\
            .select_related('topo_object') \
            .prefetch_related('topo_object__aggregations', 'attachments') \
            .order_by('pk')
        if self.action != 'list':
            queryset = queryset.annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID))
        else:
            queryset = queryset.annotate(count_parents=Count('trek_parents')).\
                exclude(Q(count_parents__gt=0) & Q(published=False))
        if 'portal' in self.request.GET:
            queryset = queryset.filter(Q(portal__name=self.request.GET['portal']) | Q(portal=None))
        return queryset.annotate(start_point=Transform(StartPoint('geom'), settings.API_SRID),
                                 end_point=Transform(EndPoint('geom'), settings.API_SRID)). \
            filter(Q(**{'published_{lang}'.format(lang=lang): True})
                   | Q(**{'trek_parents__parent__published_{lang}'.format(lang=lang): True,
                          'trek_parents__parent__deleted': False})).distinct()

    def get_serializer_context(self):
        return {'root_pk': self.request.GET.get('root_pk')}

    @decorators.action(detail=True, methods=['get'])
    def pois(self, request, *args, **kwargs):
        trek = self.get_object()
        root_pk = self.request.GET.get('root_pk') or trek.pk
        qs = trek.pois.filter(published=True).select_related('topo_object', 'type', )\
            .prefetch_related('topo_object__aggregations', 'attachments') \
            .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID)).order_by('pk')
        data = api_serializers_trekking.POIListSerializer(qs, many=True, context={'root_pk': root_pk}).data
        return response.Response(data)

    @decorators.action(detail=True, methods=['get'])
    def touristic_contents(self, request, *args, **kwargs):
        trek = self.get_object()
        root_pk = self.request.GET.get('root_pk') or trek.pk
        qs = trek.touristic_contents.filter(published=True)
        if 'portal' in self.request.GET:
            qs = qs.filter(Q(portal__name__in=self.request.GET['portal'].split(',')) | Q(portal=None))
        qs = qs.prefetch_related('attachments').annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID))
        data = api_serializers_tourism.TouristicContentListSerializer(qs, many=True, context={'root_pk': root_pk}).data
        return response.Response(data)

    @decorators.action(detail=True, methods=['get'])
    def touristic_events(self, request, *args, **kwargs):
        trek = self.get_object()
        root_pk = self.request.GET.get('root_pk') or trek.pk
        qs = trek.trek.touristic_events.filter(published=True)
        if 'portal' in self.request.GET:
            qs = qs.filter(Q(portal__name__in=self.request.GET['portal'].split(',')) | Q(portal=None))
        qs = qs.prefetch_related('attachments').annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID))
        data = api_serializers_tourism.TouristicEventListSerializer(qs, many=True, context={'root_pk': root_pk}).data
        return response.Response(data)

    if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
        @decorators.action(detail=True, methods=['get'])
        def sensitive_areas(self, request, *args, **kwargs):
            trek = self.get_object()
            root_pk = self.request.GET.get('root_pk') or trek.pk
            qs = trek.sensitive_areas.filter(published=True) \
                .prefetch_related('species') \
                .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID)).order_by('pk')
            data = api_serializers_sensitivity.SensitiveAreaListSerializer(qs, many=True, context={'root_pk': root_pk}).data
            return response.Response(data)
