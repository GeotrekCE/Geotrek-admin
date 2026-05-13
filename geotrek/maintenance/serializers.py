from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField

from ..common.serializers import AccessMeanGTAMSerializer, StructureGTAMSerializer
from ..core.models import Stake
from .models import (
    Contractor,
    Intervention,
    InterventionDisorder,
    InterventionJob,
    InterventionStatus,
    InterventionType,
    ManDay,
    Project,
)


class InterventionContractorGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="contractor")

    class Meta:
        model = Contractor
        fields = ("id", "name")


class InterventionStakeGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="stake")

    class Meta:
        model = Stake
        fields = ("id", "name")


class InterventionStatusGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="status")

    class Meta:
        model = InterventionStatus
        fields = ("id", "name")


class InterventionTypeGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="type")

    class Meta:
        model = InterventionType
        fields = ("id", "name")


class InterventionDisordersGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="disorder")

    class Meta:
        model = InterventionDisorder
        fields = ("id", "name")


class InterventionJobsGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="job")

    class Meta:
        model = InterventionJob
        fields = ("id", "name")


class InterventionManDayGTAMSerializer(serializers.ModelSerializer):
    job = InterventionJobsGTAMSerializer()

    class Meta:
        model = ManDay
        fields = ("id", "nb_days", "job")


class InterventionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(source="name_display")
    stake = serializers.SlugRelatedField(slug_field="stake", read_only=True)
    status = serializers.SlugRelatedField(slug_field="status", read_only=True)
    type = serializers.SlugRelatedField(slug_field="type", read_only=True)
    target = serializers.CharField(source="target_display")

    class Meta:
        model = Intervention
        fields = "__all__"


class InterventionGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = Intervention
        fields = ["id", "name"]


class InterventionGTAMSerializer(serializers.ModelSerializer):
    api_geom = GeometryField(read_only=True, precision=7)
    structure = StructureGTAMSerializer()
    contractors = InterventionContractorGTAMSerializer(many=True)
    stake = InterventionStakeGTAMSerializer()
    status = InterventionStatusGTAMSerializer()
    type = InterventionTypeGTAMSerializer()
    disorders = InterventionDisordersGTAMSerializer(many=True)
    man_day = InterventionManDayGTAMSerializer(many=True, source="manday_set")
    access = AccessMeanGTAMSerializer()

    class Meta:
        model = Intervention
        fields = [
            "id",
            "structure",
            "api_geom",
            "name",
            "date_insert",
            "date_update",
            "begin_date",
            "end_date",
            "subcontracting",
            "width",
            "height",
            "material_cost",
            "heliport_cost",
            "contractor_cost",
            "contractors",
            "length",
            "stake",
            "status",
            "type",
            "disorders",
            "man_day",
            "description",
            "access",
        ]


class ProjectSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(source="name_display")
    period = serializers.CharField(source="period_display")
    type = serializers.SlugRelatedField(slug_field="type", read_only=True)
    domain = serializers.SlugRelatedField(slug_field="domain", read_only=True)

    class Meta:
        model = Project
        fields = "__all__"


class ProjectGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = Project
        fields = ["id", "name"]
