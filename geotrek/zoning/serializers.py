from rest_framework import serializers as rest_serializers

from geotrek.zoning import models as zoning_models


class CitySerializer(rest_serializers.ModelSerializer):

    class Meta:
        model = zoning_models.City
        fields = ('code', 'name')


class DistrictSerializer(rest_serializers.ModelSerializer):

    class Meta:
        model = zoning_models.District
        fields = ('id', 'name')


class RestrictedAreaSerializer(rest_serializers.ModelSerializer):
    type = rest_serializers.ReadOnlyField(source='area_type.name')

    class Meta:
        model = zoning_models.RestrictedArea
        fields = ('id', 'name', 'type')


class ZoningSerializerMixin(rest_serializers.ModelSerializer):
    cities = CitySerializer(many=True, source='published_cities')
    districts = DistrictSerializer(many=True, source='published_districts')
    areas = RestrictedAreaSerializer(many=True, source='published_areas')

    class Meta:
        fields = ('cities', 'districts', 'areas')
