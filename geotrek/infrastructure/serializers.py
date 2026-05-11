from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import (
    AccessMeanGTAMSerializer,
    BasePublishableSerializerMixin,
    PictogramSerializerMixin,
    ProviderGTAMSerializer,
    StructureGTAMSerializer,
)

from . import models as infrastructure_models
from .models import (
    InfrastructureCondition,
    InfrastructureMaintenanceDifficultyLevel,
    InfrastructureType,
    InfrastructureUsageDifficultyLevel,
)


class InfrastructureTypeSerializer(PictogramSerializerMixin):
    class Meta:
        model = infrastructure_models.InfrastructureType
        fields = ("id", "pictogram", "label")


class InfrastructureTypeGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='label')

    class Meta:
        model = InfrastructureType
        fields = ("id", "name")


class InfrastructureMaintenanceDifficultyGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='label')

    class Meta:
        model = InfrastructureMaintenanceDifficultyLevel
        fields = ("id", "name")


class InfrastructureUsageDifficultyGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='label')

    class Meta:
        model = InfrastructureUsageDifficultyLevel
        fields = ("id", "name")


class InfrastructureConditionsGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='label')

    class Meta:
        model = InfrastructureCondition
        fields = ("id", "name")


class InfrastructureSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(source="name_display")
    type = serializers.CharField(source="type_display")
    conditions = serializers.CharField(source="conditions_display")
    cities = serializers.CharField(source="cities_display")
    structure = serializers.SlugRelatedField("name", read_only=True)
    usage_difficulty = serializers.SlugRelatedField("label", read_only=True)
    maintenance_difficulty = serializers.SlugRelatedField("label", read_only=True)

    class Meta:
        model = infrastructure_models.Infrastructure
        fields = "__all__"


class InfrastructureGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = infrastructure_models.Infrastructure
        fields = ["id", "name", "published"]


class InfrastructureGTAMSerializer(serializers.ModelSerializer):
    api_geom = GeometryField(read_only=True, precision=7)
    provider = ProviderGTAMSerializer()
    structure = StructureGTAMSerializer()
    access = AccessMeanGTAMSerializer()
    type = InfrastructureTypeGTAMSerializer()
    maintenance_difficulty = InfrastructureMaintenanceDifficultyGTAMSerializer()
    usage_difficulty = InfrastructureUsageDifficultyGTAMSerializer()
    conditions = InfrastructureConditionsGTAMSerializer(many=True)

    class Meta:
        model = infrastructure_models.Infrastructure
        fields = [
            "id",
            "date_insert",
            "date_update",
            "api_geom",
            "uuid",
            "published",
            "publication_date",
            "eid",
            "name",
            "description",
            "implantation_year",
            "accessibility",
            "provider",
            "structure",
            "access",
            "type",
            "maintenance_difficulty",
            "usage_difficulty",
            "conditions",
        ]
        geom = "api_geom"


class InfrastructureAPISerializer(BasePublishableSerializerMixin):
    type = InfrastructureTypeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = infrastructure_models.Infrastructure
        id_field = "id"  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = (
            "id",
            "structure",
            "name",
            "type",
            "accessibility",
            *BasePublishableSerializerMixin.Meta.fields,
        )


class InfrastructureAPIGeojsonSerializer(
    GeoFeatureModelSerializer, InfrastructureAPISerializer
):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(InfrastructureAPISerializer.Meta):
        geo_field = "api_geom"
        fields = (*InfrastructureAPISerializer.Meta.fields, "api_geom")
