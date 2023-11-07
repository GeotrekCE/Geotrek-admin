from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import F
from django.db.models.query import Prefetch
from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets, filters as api_filters
from geotrek.common.models import Attachment
from geotrek.signage import models as signage_models


class SignageViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (api_filters.NearbyContentFilter, api_filters.UpdateOrCreateDateFilter)
    serializer_class = api_serializers.SignageSerializer
    queryset = signage_models.Signage.objects.existing() \
        .select_related('topo_object', 'type', ) \
        .annotate(geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID)) \
        .prefetch_related('topo_object__aggregations',
                          Prefetch('attachments',
                                   queryset=Attachment.objects.select_related('license', 'filetype', 'filetype__structure'))) \
        .order_by('pk')


class SignageTypeViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.SignageRelatedPortalFilter, )
    serializer_class = api_serializers.SignageTypeSerializer
    queryset = signage_models.SignageType.objects.all().order_by('pk')


class SignageConditionViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.SignageConditionSerializer
    queryset = signage_models.SignageCondition.objects.all().order_by('pk')


class DirectionViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.DirectionSerializer
    queryset = signage_models.Direction.objects.all().order_by('pk')


class SealingViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.SealingSerializer
    queryset = signage_models.Sealing.objects.all().order_by('pk')


class ColorViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.ColorSerializer
    queryset = signage_models.Color.objects.all().order_by('pk')


class BladeTypeViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.BladeTypeSerializer
    queryset = signage_models.BladeType.objects.all().order_by('pk')
