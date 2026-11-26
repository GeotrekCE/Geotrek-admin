from django.db.models.query import Prefetch

from geotrek.api.v2 import filters as api_filters
from geotrek.api.v2 import serializers as api_serializers
from geotrek.api.v2 import viewsets as api_viewsets
from geotrek.api.v2.utils import annotate_geojson
from geotrek.common.models import Attachment
from geotrek.infrastructure import models as infra_models


class InfrastructureViewSet(api_viewsets.GeotrekGeometricViewset):
    filter_backends = (
        *api_viewsets.GeotrekGeometricViewset.filter_backends,
        api_filters.NearbyContentFilter,
        api_filters.UpdateOrCreateDateFilter,
    )
    serializer_class = api_serializers.InfrastructureSerializer
    queryset = annotate_geojson(
        infra_models.Infrastructure.objects.existing()
        .select_related(
            "topo_object",
            "type",
        )
        .prefetch_related(
            "topo_object__aggregations",
            Prefetch(
                "attachments",
                queryset=Attachment.objects.select_related(
                    "license", "filetype", "filetype__structure"
                ),
            ),
            "conditions",
        )
        .defer("geom", "geom_3d", "topo_object__geom", "topo_object__geom_3d")
        .order_by("pk"),
        field_name="geom_3d",
    )


class InfrastructureTypeViewSet(api_viewsets.GeotrekViewSet):
    filter_backends = (
        *api_viewsets.GeotrekViewSet.filter_backends,
        api_filters.InfrastructureRelatedPortalFilter,
    )
    serializer_class = api_serializers.InfrastructureTypeSerializer
    queryset = infra_models.InfrastructureType.objects.all().order_by("pk")


class InfrastructureUsageDifficultyLevelViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.InfrastructureUsageDifficultyLevelSerializer
    queryset = infra_models.InfrastructureUsageDifficultyLevel.objects.all().order_by(
        "pk"
    )


class InfrastructureConditionViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = api_serializers.InfrastructureConditionSerializer
    queryset = infra_models.InfrastructureCondition.objects.all().order_by("pk")


class InfrastructureMaintenanceDifficultyLevelViewSet(api_viewsets.GeotrekViewSet):
    serializer_class = (
        api_serializers.InfrastructureMaintenanceDifficultyLevelSerializer
    )
    queryset = (
        infra_models.InfrastructureMaintenanceDifficultyLevel.objects.all().order_by(
            "pk"
        )
    )
