import csv

from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from mapentity.serializers.commasv import CSVSerializer
from mapentity.serializers.shapefile import ZipShapeSerializer
from rest_framework import serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.fields import GeometryField, GeometrySerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import (
    AccessMeanGTAMSerializer,
    BasePublishableSerializerMixin,
    OrganismGTAMSerializer,
    PictogramSerializerMixin,
    StructureGTAMSerializer,
)

from ..authent.models import Structure
from ..common.mixins.serializers import LimitStructurePermission
from ..common.models import AccessMean, Organism
from ..core.models import Topology
from . import models as signage_models
from .models import Sealing, SignageCondition, SignageType


class SignageTypeSerializer(PictogramSerializerMixin):
    class Meta:
        model = signage_models.SignageType
        fields = ("id", "pictogram", "label")


class SignageTypeGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")

    class Meta:
        model = signage_models.SignageType
        fields = ("id", "name")


class SignageConditionGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")

    class Meta:
        model = signage_models.SignageCondition
        fields = ("id", "name")


class SignageSealingGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")

    class Meta:
        model = signage_models.Sealing
        fields = ("id", "name")


class DirectionGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")

    class Meta:
        model = signage_models.Direction
        fields = ("id", "name")


class BladeTypeGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")

    class Meta:
        model = signage_models.BladeType
        fields = ("id", "name")


class BladeConditionGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")

    class Meta:
        model = signage_models.BladeCondition
        fields = ("id", "name")


class BladeColorGTAMSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="label")

    class Meta:
        model = signage_models.Color
        fields = ("id", "name")


class LineGTAMSerializer(serializers.ModelSerializer):
    class Meta:
        model = signage_models.Line
        fields = ["id", "number", "text", "distance", "time"]


class BladesGTAMSerializer(serializers.ModelSerializer):
    lines = LineGTAMSerializer(many=True)

    # read-only
    direction = DirectionGTAMSerializer(read_only=True)
    type = BladeTypeGTAMSerializer(read_only=True)
    color = BladeColorGTAMSerializer(read_only=True)
    conditions = BladeConditionGTAMSerializer(many=True, read_only=True)

    # write-only
    direction_id = serializers.PrimaryKeyRelatedField(
        source="direction",
        write_only=True,
        allow_null=True,
        queryset=signage_models.Direction.objects.all(),
    )
    type_id = serializers.PrimaryKeyRelatedField(
        source="type",
        write_only=True,
        allow_null=True,
        queryset=signage_models.BladeType.objects.all(),
    )
    color_id = serializers.PrimaryKeyRelatedField(
        source="color",
        write_only=True,
        allow_null=True,
        queryset=signage_models.Color.objects.all(),
    )
    conditions_id = serializers.PrimaryKeyRelatedField(
        source="conditions",
        many=True,
        write_only=True,
        allow_null=True,
        queryset=signage_models.BladeCondition.objects.all(),
    )

    class Meta:
        model = signage_models.Blade
        fields = [
            "id",
            "number",
            "lines",
            # read-only
            "direction",
            "type",
            "color",
            "conditions",
            # write-only
            "direction_id",
            "type_id",
            "color_id",
            "conditions_id",
        ]


class SignageSerializer(
    DynamicFieldsMixin, BasePublishableSerializerMixin, serializers.ModelSerializer
):
    name = serializers.CharField(source="name_display")
    structure = serializers.SlugRelatedField("name", read_only=True)
    type = serializers.CharField(source="type_display")
    conditions = serializers.CharField(source="conditions_display")
    manager = serializers.SlugRelatedField("organism", read_only=True)
    sealing = serializers.SlugRelatedField("label", read_only=True)

    class Meta:
        model = signage_models.Signage
        fields = "__all__"


class SignageGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = signage_models.Signage
        fields = ("id", "name", "published")


class SignageGTAMSerializer(LimitStructurePermission, serializers.ModelSerializer):
    geom = GeometryField(precision=7, transform=settings.API_SRID)
    blades = BladesGTAMSerializer(
        many=True, read_only=True
    )  # blades are not supported in v0

    # read-only
    structure = StructureGTAMSerializer(read_only=True)
    access = AccessMeanGTAMSerializer(read_only=True)
    conditions = SignageConditionGTAMSerializer(many=True, read_only=True)
    type = SignageTypeGTAMSerializer(read_only=True)
    sealing = SignageSealingGTAMSerializer(read_only=True)
    manager = OrganismGTAMSerializer(read_only=True)

    # write-only
    structure_id = serializers.PrimaryKeyRelatedField(
        source="structure",
        write_only=True,
        queryset=Structure.objects.all(),
    )
    access_id = serializers.PrimaryKeyRelatedField(
        source="access",
        write_only=True,
        allow_null=True,
        required=False,
        queryset=AccessMean.objects.all(),
    )
    conditions_id = serializers.PrimaryKeyRelatedField(
        source="conditions",
        many=True,
        write_only=True,
        allow_null=True,
        required=False,
        queryset=SignageCondition.objects.all(),
    )
    type_id = serializers.PrimaryKeyRelatedField(
        source="type",
        write_only=True,
        queryset=SignageType.objects.all(),
    )
    sealing_id = serializers.PrimaryKeyRelatedField(
        source="sealing",
        write_only=True,
        allow_null=True,
        required=False,
        queryset=Sealing.objects.all(),
    )
    manager_id = serializers.PrimaryKeyRelatedField(
        source="manager",
        write_only=True,
        allow_null=True,
        required=False,
        queryset=Organism.objects.all(),
    )

    class Meta:
        model = signage_models.Signage
        fields = [
            "id",
            "geom",
            "date_insert",
            "date_update",
            "published",
            "name",
            "description",
            "implantation_year",
            "code",
            "printed_elevation",
            "blades",
            # read-only
            "structure",
            "access",
            "manager",
            "sealing",
            "type",
            "conditions",
            # write-only
            "structure_id",
            "access_id",
            "manager_id",
            "sealing_id",
            "type_id",
            "conditions_id",
        ]
        geom = "geom"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context["request"]
        user = request.user
        structure = user.profile.structure

        signage_limitated_fields = [
            ("sealing_id", signage_models.Sealing, False),
            ("type_id", signage_models.SignageType, False),
            ("conditions_id", signage_models.SignageCondition, True),
        ]
        blade_limitated_fields = [
            ("type_id", signage_models.BladeType, False),
            ("conditions_id", signage_models.BladeCondition, True),
        ]

        if not (user.is_superuser or user.has_perm("authent.can_bypass_structure")):
            self._apply_structure_limitation(
                self.fields, signage_limitated_fields, structure
            )
            self._apply_structure_limitation(
                self.fields["blades"].child.fields, blade_limitated_fields, structure
            )

    def validate_geom(self, value):
        if not isinstance(value, Point):
            msg = _("New signage geometry must be points")
            raise serializers.ValidationError(msg)
        return value

    def create(self, validated_data):
        validated_data = self._check_assigned_structure(validated_data)
        # blades_data = validated_data.pop("blades", [])
        geom = validated_data.pop("geom", None)

        with transaction.atomic():
            signage = super().create(validated_data)

            self._sync_topology(signage, geom)
            # self._sync_blades(signage, blades_data)
        return signage

    def update(self, instance, validated_data):
        validated_data = self._check_assigned_structure(validated_data)
        # blades_data = validated_data.pop("blades", [])
        geom = validated_data.pop("geom", None)

        with transaction.atomic():
            signage = super().update(instance, validated_data)

            if geom:
                self._sync_topology(signage, geom)

            # self._sync_blades(signage, blades_data)
        return signage

    def _sync_topology(self, obj, geom):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            serialized = f'{{"lng": {geom.x}, "lat": {geom.y}}}'
            topology = Topology.deserialize(serialized)
            obj.topo_object.mutate(topology)
        else:
            geom.transform(settings.SRID)
            obj.geom = geom
            obj.save()

    # def _sync_blades(self, signage, blades_data):
    #     qs = signage.blades.all()
    #     qs.delete()
    #
    #     for blade_data in blades_data:
    #         self._create_blade(signage, blade_data)
    #
    # def _create_blade(self, signage, blade_data):
    #     lines_data = blade_data.pop("lines", [])
    #     conditions = blade_data.pop("conditions", [])
    #
    #     blade = signage_models.Blade.objects.create(signage=signage, **blade_data)
    #     blade.conditions.set(conditions)
    #
    #     self._sync_lines(blade, lines_data)
    #
    #     return blade
    #
    # def _sync_lines(self, blade, lines_data):
    #     blade.lines.all().delete()
    #
    #     for line_data in lines_data:
    #         signage_models.Line.objects.create(blade=blade, **line_data)


class SignageAPISerializer(BasePublishableSerializerMixin):
    type = SignageTypeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = signage_models.Signage
        id_field = "id"  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = (
            "id",
            "structure",
            "name",
            "type",
            "code",
            "printed_elevation",
            "conditions",
            "manager",
            "sealing",
            *BasePublishableSerializerMixin.Meta.fields,
        )


class SignageAPIGeojsonSerializer(GeoFeatureModelSerializer, SignageAPISerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(SignageAPISerializer.Meta):
        geo_field = "api_geom"
        fields = (*SignageAPISerializer.Meta.fields, "api_geom")


class BladeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = signage_models.BladeType
        fields = ("label",)


class BladeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    type = serializers.SlugRelatedField("label", read_only=True)
    structure = serializers.SlugRelatedField("name", read_only=True)
    direction = serializers.SlugRelatedField("label", read_only=True)
    color = serializers.SlugRelatedField("label", read_only=True)
    conditions = serializers.CharField(source="conditions_display")
    number = serializers.CharField(source="number_display")

    class Meta:
        model = signage_models.Blade
        fields = "__all__"


class BladeGeojsonSerializer(MapentityGeojsonModelSerializer):
    api_geom = GeometrySerializerMethodField()

    def get_api_geom(self, obj):
        return obj.geom.transform(4326, clone=True)

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = signage_models.Blade
        fields = ("id", "number")


class CSVBladeSerializer(CSVSerializer):
    def serialize(self, queryset, **options):
        """
        Uses self.columns, containing fieldnames to produce the CSV.
        The header of the csv is made of the verbose name of each field.
        """
        model_blade = signage_models.Blade
        columns = options.pop("fields")
        columns_lines = options.pop("line_fields")
        model_line = signage_models.Line
        stream = options.pop("stream")
        ascii = options.get("ensure_ascii", True)
        max_lines = max([value.lines.count() for value in queryset])

        header = self.get_csv_header(columns, model_blade)

        header_line = self.get_csv_header(columns_lines, model_line)

        for i in range(max_lines):
            numbered_header_lines = [f"{header} {i + 1}" for header in header_line]
            header.extend(numbered_header_lines)

        getters = self.getters_csv(columns, model_blade, ascii)

        getters_lines = self.getters_csv(columns_lines, model_line, ascii)

        def get_lines():
            yield header
            for blade in queryset.order_by("signage__code", "number"):
                column_getter = [getters[field](blade, field) for field in columns]
                for obj in blade.lines.order_by("number"):
                    column_getter.extend(
                        getters_lines[field](obj, field) for field in columns_lines
                    )
                yield column_getter

        writer = csv.writer(stream)
        writer.writerows(get_lines())


class ZipBladeShapeSerializer(ZipShapeSerializer):
    def split_bygeom(self, iterable, geom_getter=lambda x: x.geom):
        lines = [blade for blade in iterable]
        return super().split_bygeom(lines, geom_getter)
