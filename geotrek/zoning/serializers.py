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
        fields = LandLayerSerializerMixin.Meta.fields + ["name"]


class CityAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = zoning_models.City
        fields = ("code", "name")


class DistrictSerializer(LandLayerSerializerMixin):
    class Meta(LandLayerSerializerMixin.Meta):
        model = zoning_models.District


class DistrictAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = zoning_models.District
        fields = ("id", "name")


class RestrictedAreaSerializer(LandLayerSerializerMixin):
    class Meta(LandLayerSerializerMixin.Meta):
        model = zoning_models.RestrictedArea


class RestrictedAreaAPISerializer(serializers.ModelSerializer):
    type = serializers.ReadOnlyField(source="area_type.name")

    class Meta:
        model = zoning_models.RestrictedArea
        fields = ("id", "name", "type")
