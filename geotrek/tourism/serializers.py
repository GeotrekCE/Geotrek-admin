from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers as rest_serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.common.serializers import (
    PictogramSerializerMixin,
    TranslatedModelSerializer,
)

from . import models as tourism_models


class LabelAccessibilitySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = tourism_models.LabelAccessibility
        fields = ("id", "pictogram", "label")


class InformationDeskTypeSerializer(
    PictogramSerializerMixin, TranslatedModelSerializer
):
    class Meta:
        model = tourism_models.InformationDeskType
        fields = ("id", "pictogram", "label")


class TrekInformationDeskGeojsonSerializer(
    TranslatedModelSerializer, GeoFeatureModelSerializer
):
    type = InformationDeskTypeSerializer()
    label_accessibility = LabelAccessibilitySerializer()
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta:
        model = tourism_models.InformationDesk
        geo_field = "api_geom"
        fields = (
            "name",
            "description",
            "accessibility",
            "label_accessibility",
            "phone",
            "email",
            "website",
            "photo_url",
            "street",
            "postal_code",
            "municipality",
            "latitude",
            "longitude",
            "type",
            "api_geom",
        )


class TouristicContentSerializer(DynamicFieldsMixin, rest_serializers.ModelSerializer):
    name = rest_serializers.CharField(source="name_display")
    structure = rest_serializers.SlugRelatedField("name", read_only=True)
    themes = rest_serializers.CharField(source="themes_display")
    category = rest_serializers.SlugRelatedField("label", read_only=True)
    label_accessibility = rest_serializers.SlugRelatedField("label", read_only=True)
    reservation_system = rest_serializers.SlugRelatedField("name", read_only=True)

    class Meta:
        model = tourism_models.TouristicContent
        fields = "__all__"


class TouristicContentGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = tourism_models.TouristicContent
        fields = ("id", "name")


class TouristicEventSerializer(DynamicFieldsMixin, rest_serializers.ModelSerializer):
    name = rest_serializers.CharField(source="name_display")
    type = rest_serializers.SlugRelatedField("type", read_only=True)
    structure = rest_serializers.SlugRelatedField("name", read_only=True)

    class Meta:
        model = tourism_models.TouristicEvent
        fields = "__all__"


class TouristicEventGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = tourism_models.TouristicEvent
        fields = ("id", "name")
