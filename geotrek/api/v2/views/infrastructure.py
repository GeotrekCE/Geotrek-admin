from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import F
from django.db.models.query import Prefetch
from geotrek.api.v2 import serializers as api_serializers, \
    viewsets as api_viewsets, filters as api_filters
from geotrek.common.models import Attachment
from geotrek.infrastructure import models as infra_models


class InfrastructureViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = api_viewsets.GeotrekGeometricViewset.filter_backends + (
        api_filters.NearbyContentFilter,
        api_filters.UpdateOrCreateDateFilter,
    )
    serializer_class = api_serializers.InfrastructureSerializer
    queryset = infra_models.Infrastructure.objects.existing() \
        .select_related('topo_object', 'type', ) \
        .annotate(geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID)) \
        .prefetch_related('topo_object__aggregations',
                          Prefetch('attachments',
                                   queryset=Attachment.objects.select_related('license', 'filetype', 'filetype__structure')),
                          'conditions').order_by('pk')


class InfrastructureTypeViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = api_viewsets.GeotrekViewSet.filter_backends + (api_filters.InfrastructureRelatedPortalFilter, )
    serializer_class = api_serializers.InfrastructureTypeSerializer
    queryset = infra_models.InfrastructureType.objects.all().order_by('pk')


class InfrastructureUsageDifficultyLevelViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.InfrastructureUsageDifficultyLevelSerializer
    queryset = infra_models.InfrastructureUsageDifficultyLevel.objects.all().order_by('pk')


class InfrastructureConditionViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.InfrastructureConditionSerializer
    queryset = infra_models.InfrastructureCondition.objects.all().order_by('pk')


class InfrastructureMaintenanceDifficultyLevelViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.InfrastructureMaintenanceDifficultyLevelSerializer
    queryset = infra_models.InfrastructureMaintenanceDifficultyLevel.objects.all().order_by('pk')
