from django.conf import settings
from django.db import transaction
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
    StructureGTAMSerializer,
)

from ..authent.models import Structure
from ..common.mixins.serializers import LimitStructurePermission
from ..common.models import AccessMean
from ..core.models import Topology
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
    name = serializers.CharField(source="label")

    class Meta:
        model = InfrastructureType
        fields = ("id", "name")


class InfrastructureMaintenanceDifficultyGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")

    class Meta:
        model = InfrastructureMaintenanceDifficultyLevel
        fields = ("id", "name")


class InfrastructureUsageDifficultyGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")

    class Meta:
        model = InfrastructureUsageDifficultyLevel
        fields = ("id", "name")


class InfrastructureConditionsGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")

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


class InfrastructureGTAMSerializer(
    LimitStructurePermission, serializers.ModelSerializer
):
    geom = GeometryField(precision=7, transform=settings.API_SRID)

    # read-only
    structure = StructureGTAMSerializer(read_only=True)
    access = AccessMeanGTAMSerializer(read_only=True)
    type = InfrastructureTypeGTAMSerializer(read_only=True)
    maintenance_difficulty = InfrastructureMaintenanceDifficultyGTAMSerializer(
        read_only=True
    )
    usage_difficulty = InfrastructureUsageDifficultyGTAMSerializer(read_only=True)
    conditions = InfrastructureConditionsGTAMSerializer(many=True, read_only=True)

    # write-only
    structure_id = serializers.PrimaryKeyRelatedField(
        source="structure", write_only=True, queryset=Structure.objects.all()
    )
    access_id = serializers.PrimaryKeyRelatedField(
        source="access",
        write_only=True,
        allow_null=True,
        queryset=AccessMean.objects.all(),
    )
    type_id = serializers.PrimaryKeyRelatedField(
        source="type", write_only=True, queryset=InfrastructureType.objects.all()
    )
    maintenance_difficulty_id = serializers.PrimaryKeyRelatedField(
        source="maintenance_difficulty",
        write_only=True,
        allow_null=True,
        queryset=InfrastructureMaintenanceDifficultyLevel.objects.all(),
    )
    usage_difficulty_id = serializers.PrimaryKeyRelatedField(
        source="usage_difficulty",
        write_only=True,
        allow_null=True,
        queryset=InfrastructureUsageDifficultyLevel.objects.all(),
    )
    conditions_id = serializers.PrimaryKeyRelatedField(
        source="conditions",
        many=True,
        write_only=True,
        allow_null=True,
        queryset=InfrastructureCondition.objects.all(),
    )

    class Meta:
        model = infrastructure_models.Infrastructure
        fields = [
            "id",
            "date_insert",
            "date_update",
            "geom",
            "published",
            "name",
            "description",
            "implantation_year",
            "accessibility",
            # read-only
            "structure",
            "access",
            "type",
            "maintenance_difficulty",
            "usage_difficulty",
            "conditions",
            # write-only
            "structure_id",
            "access_id",
            "type_id",
            "maintenance_difficulty_id",
            "usage_difficulty_id",
            "conditions_id",
        ]
        geom = "geom"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = self.context["request"].user
        structure = user.profile.structure

        limitated_fields = [
            ("type_id", InfrastructureType, False),
            (
                "maintenance_difficulty_id",
                InfrastructureMaintenanceDifficultyLevel,
                False,
            ),
            ("usage_difficulty_id", InfrastructureUsageDifficultyLevel, False),
            ("conditions_id", InfrastructureCondition, True),
        ]

        if not (user.is_superuser or user.has_perm("authent.can_bypass_structure")):
            self.fields["structure_id"].queryset = Structure.objects.filter(
                pk=structure.pk
            )
            self._apply_structure_limitation(self.fields, limitated_fields, structure)

    def create(self, validated_data):
        geom = validated_data.pop("geom", None)

        with transaction.atomic():
            infrastructure = super().create(validated_data)
            infrastructure = self._sync_topology(infrastructure, geom)

        return infrastructure

    def update(self, instance, validated_data):
        geom = validated_data.pop("geom", None)

        with transaction.atomic():
            infrastructure = super().update(instance, validated_data)
            if geom:
                infrastructure = self._sync_topology(infrastructure, geom)

        return infrastructure

    def _sync_topology(self, obj, geom):
        serialized = f'{{"lng": {geom.x}, "lat": {geom.y}, "kind": "SIGNAGE"}}'
        topology = Topology.deserialize(serialized)
        obj.topo_object.mutate(topology)
        return obj


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
