from django.conf import settings
from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers

from geotrek.zoning import models as zoning_models


class LandLayerSerializerMixin(geo_serializers.GeoFeatureModelSerializer):
    api_geom = geo_serializers.GeometryField(precision=settings.LAYER_PRECISION_LAND)

    class Meta:
        geo_field = "api_geom"
        id_field = False
        fields = ["api_geom"]


class CitySerializer(LandLayerSerializerMixin):
    class Meta(LandLayerSerializerMixin.Meta):
        model = zoning_models.City
        fields = [*LandLayerSerializerMixin.Meta.fields, "name"]


class CityAutoCompleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk")
    text = serializers.SerializerMethodField()

    def get_text(self, obj):
        return obj.name if not obj.code else f"{obj.name} ({obj.code})"

    class Meta:
        model = zoning_models.City
        fields = ["id", "text"]


class CityAutoCompleteBBoxSerializer(CityAutoCompleteSerializer):
    id = serializers.SerializerMethodField()

    def get_id(self, obj):
        return ",".join([str(x) for x in obj.bbox])

    class Meta(CityAutoCompleteSerializer.Meta):
        pass


class DistrictSerializer(LandLayerSerializerMixin):
    class Meta(LandLayerSerializerMixin.Meta):
        model = zoning_models.District


class DistrictAutoCompleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk")
    text = serializers.CharField(source="name")

    class Meta:
        model = zoning_models.District
        fields = ["id", "text"]


class DistrictAutoCompleteBBoxSerializer(DistrictAutoCompleteSerializer):
    id = serializers.SerializerMethodField()

    def get_id(self, obj):
        return ",".join([str(x) for x in obj.bbox])

    class Meta(DistrictAutoCompleteSerializer.Meta):
        pass


class RestrictedAreaSerializer(LandLayerSerializerMixin):
    class Meta(LandLayerSerializerMixin.Meta):
        model = zoning_models.RestrictedArea


class RestrictedAreaAutoCompleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="pk")
    text = serializers.CharField(source="name")

    class Meta:
        model = zoning_models.RestrictedArea
        fields = ["id", "text"]


class RestrictedAreaAutoCompleteBBoxSerializer(RestrictedAreaAutoCompleteSerializer):
    id = serializers.SerializerMethodField()

    def get_id(self, obj):
        return ",".join([str(x) for x in obj.bbox])

    class Meta(RestrictedAreaAutoCompleteSerializer.Meta):
        pass
