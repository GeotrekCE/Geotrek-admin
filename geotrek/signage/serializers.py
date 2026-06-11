import csv

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

from . import models as signage_models


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
    lines = LineGTAMSerializer(many=True, source="lines_list")
    direction = DirectionGTAMSerializer()
    type = BladeTypeGTAMSerializer()
    color = BladeColorGTAMSerializer()
    conditions = BladeConditionGTAMSerializer(many=True, source="conditions_list")

    class Meta:
        model = signage_models.Blade
        fields = [
            "id",
            "number",
            "direction",
            "type",
            "color",
            "conditions",
            "lines",
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


class SignageGTAMSerializer(serializers.ModelSerializer):
    api_geom = GeometryField(read_only=True, precision=7)
    structure = StructureGTAMSerializer()
    access = AccessMeanGTAMSerializer()
    conditions = SignageConditionGTAMSerializer(many=True, source="conditions_list")
    type = SignageTypeGTAMSerializer()
    sealing = SignageSealingGTAMSerializer()
    manager = OrganismGTAMSerializer()
    blades = BladesGTAMSerializer(many=True, source="blades_list")

    class Meta:
        model = signage_models.Signage
        fields = [
            "id",
            "api_geom",
            "structure",
            "date_insert",
            "date_update",
            "published",
            "name",
            "description",
            "implantation_year",
            "code",
            "printed_elevation",
            "access",
            "manager",
            "sealing",
            "type",
            "conditions",
            "blades",
        ]
        geom = "api_geom"


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
