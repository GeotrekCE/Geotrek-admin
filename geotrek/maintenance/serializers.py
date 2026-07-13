from django.conf import settings
from django.contrib.gis.geos import Point
from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import exceptions, serializers
from rest_framework_gis.fields import GeometryField

from ..authent.models import Structure
from ..common.mixins.serializers import LimitStructurePermission
from ..common.models import AccessMean
from ..common.serializers import AccessMeanGTAMSerializer, StructureGTAMSerializer
from ..core.models import Stake, Topology
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
    nb_days = serializers.DecimalField(
        max_digits=6, decimal_places=2, coerce_to_string=False
    )

    # read-only
    job = InterventionJobsGTAMSerializer(read_only=True)

    # write-only
    job_id = serializers.PrimaryKeyRelatedField(
        source="job",
        write_only=True,
        queryset=InterventionJob.objects.all(),
    )

    class Meta:
        model = ManDay
        fields = ("id", "nb_days", "job", "job_id")


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


class InterventionRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        model = type(value)._meta.model_name
        return {"model": model, "id": getattr(value, "id", "")}


class InterventionGTAMSerializer(LimitStructurePermission, serializers.ModelSerializer):
    geom = GeometryField(precision=7, transform=settings.API_SRID)
    target = InterventionRelatedField(read_only=True)
    man_day = InterventionManDayGTAMSerializer(many=True, source="manday_set")

    # read-only
    structure = StructureGTAMSerializer(read_only=True)
    contractors = InterventionContractorGTAMSerializer(many=True, read_only=True)
    stake = InterventionStakeGTAMSerializer(read_only=True)
    status = InterventionStatusGTAMSerializer(read_only=True)
    type = InterventionTypeGTAMSerializer(read_only=True)
    disorders = InterventionDisordersGTAMSerializer(many=True, read_only=True)
    access = AccessMeanGTAMSerializer(read_only=True)

    # write-only
    structure_id = serializers.PrimaryKeyRelatedField(
        source="structure",
        write_only=True,
        queryset=Structure.objects.all(),
    )
    contractors_id = serializers.PrimaryKeyRelatedField(
        source="contractors",
        many=True,
        write_only=True,
        required=False,
        queryset=Contractor.objects.all(),
    )
    stake_id = serializers.PrimaryKeyRelatedField(
        source="stake",
        write_only=True,
        allow_null=True,
        required=False,
        queryset=Stake.objects.all(),
    )
    status_id = serializers.PrimaryKeyRelatedField(
        source="status",
        write_only=True,
        allow_null=True,
        required=False,
        queryset=InterventionStatus.objects.all(),
    )
    type_id = serializers.PrimaryKeyRelatedField(
        source="type",
        write_only=True,
        allow_null=True,
        required=False,
        queryset=InterventionType.objects.all(),
    )
    disorders_id = serializers.PrimaryKeyRelatedField(
        source="disorders",
        many=True,
        write_only=True,
        required=False,
        queryset=InterventionDisorder.objects.all(),
    )
    access_id = serializers.PrimaryKeyRelatedField(
        source="access",
        write_only=True,
        allow_null=True,
        required=False,
        queryset=AccessMean.objects.all(),
    )

    class Meta:
        model = Intervention
        fields = [
            "id",
            "geom",
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
            "length",
            "target",
            "description",
            "man_day",
            # read-only
            "structure",
            "contractors",
            "stake",
            "status",
            "type",
            "disorders",
            "access",
            # write-only
            "structure_id",
            "contractors_id",
            "stake_id",
            "status_id",
            "type_id",
            "disorders_id",
            "access_id",
        ]
        geo_field = "geom"

    def validate(self, data):
        begin_date = data.get("begin_date", None)
        end_date = data.get("end_date", None)
        if begin_date and end_date and data["begin_date"] > data["end_date"]:
            msg = {"end_date": "End date must occur after start date"}
            raise serializers.ValidationError(msg)
        return data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context["request"]
        user = request.user
        structure = user.profile.structure

        intervention_limitated_fields = [
            ("contractors_id", Contractor, True),
            ("stake_id", Stake, False),
            ("status_id", InterventionStatus, False),
            ("type_id", InterventionType, False),
            ("disorders_id", InterventionDisorder, True),
        ]
        manday_limitated_fields = [
            ("job_id", InterventionJob, False),
        ]

        if not (user.is_superuser or user.has_perm("authent.can_bypass_structure")):
            self._apply_structure_limitation(
                self.fields, intervention_limitated_fields, structure
            )
            self._apply_structure_limitation(
                self.fields["man_day"].child.fields, manday_limitated_fields, structure
            )

    def create(self, validated_data):
        validated_data = self._check_assigned_structure(validated_data)
        mandays_data = validated_data.pop("manday_set", [])
        geom = validated_data.pop("geom", None)

        intervention = super().create(validated_data)

        self._sync_manday(intervention, mandays_data)
        self._sync_target(intervention, geom)
        return intervention

    def update(self, instance, validated_data):
        validated_data = self._check_assigned_structure(validated_data)
        mandays_data = validated_data.pop("manday_set", [])
        geom = validated_data.pop("geom", None)
        target = instance.target

        intervention = super().update(instance, validated_data)

        self._sync_manday(intervention, mandays_data)

        if isinstance(target, Topology) and geom:
            self._sync_target(intervention, geom)

        return intervention

    def _sync_manday(self, intervention, mandays_data):
        intervention.manday_set.all().delete()

        for manday in mandays_data:
            ManDay.objects.create(intervention=intervention, **manday)

    def _sync_target(self, intervention, geom):
        if not isinstance(geom, Point):
            msg = {"geom": "New intervention geometry must be points"}
            raise exceptions.ValidationError(msg)

        serialized = f'{{"lng": {geom.x}, "lat": {geom.y}}}'
        topology = Topology.deserialize(serialized)
        topology.save()
        intervention.target = topology
        intervention.save()


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
