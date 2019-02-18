from __future__ import unicode_literals

from django.conf import settings
from django.db.models import F

from geotrek.api.mobile.serializers import trekking as api_serializers
from geotrek.api.mobile import viewsets as api_viewsets
from geotrek.api.v2.functions import Transform, Length, StartPoint
from geotrek.trekking import models as trekking_models


class TrekViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.TrekListSerializer
    serializer_detail_class = api_serializers.TrekDetailSerializer
    filter_fields = ('difficulty', 'themes', 'networks', 'practice')

    def get_queryset(self, *args, **kwargs):
        queryset = trekking_models.Trek.objects.existing()\
            .select_related('topo_object', 'difficulty', 'practice') \
            .prefetch_related('topo_object__aggregations', 'themes', 'networks', 'attachments', 'information_desks') \
            .order_by('pk').annotate(length_2d_m=Length('geom'))
        if self.action == 'list':
            queryset = queryset.annotate(start_point=Transform(StartPoint('geom'), settings.API_SRID))
        else:
            queryset = queryset.annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID))
        return queryset


class POIViewSet(api_viewsets.GeotrekViewset):
    serializer_class = api_serializers.POIListSerializer
    serializer_detail_class = api_serializers.POIListSerializer
    queryset = trekking_models.POI.objects.existing() \
        .select_related('topo_object', 'type', ) \
        .prefetch_related('topo_object__aggregations', 'attachments') \
        .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID),
                  geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID)) \
        .order_by('pk')  # Required for reliable pagination
    filter_fields = ('type',)
