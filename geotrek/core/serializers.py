from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.core.models import Path, Trail


class PathSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    checkbox = serializers.CharField(source='checkbox_display')
    length_2d = serializers.SerializerMethodField()
    length = serializers.FloatField(source='length_display')
    name = serializers.CharField(source='name_display')
    usages = serializers.CharField(source='usages_display')
    networks = serializers.CharField(source='networks_display')
    trails = serializers.CharField(source='trails_display')
    structure = serializers.SlugRelatedField('name', read_only=True)
    comfort = serializers.SlugRelatedField('comfort', read_only=True)
    source = serializers.SlugRelatedField('source', read_only=True)
    stake = serializers.SlugRelatedField('stake', read_only=True)

    def get_length_2d(self, obj):
        return round(obj.length_2d, 1)

    class Meta:
        model = Path
        fields = "__all__"


class PathGeojsonSerializer(GeoFeatureModelSerializer, PathSerializer):
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(PathSerializer.Meta):
        geo_field = 'api_geom'
        id_field = 'id'
        fields = "__all__"


class TrailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = Trail
        fields = "__all__"


class TrailGeojsonSerializer(GeoFeatureModelSerializer, TrailSerializer):
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(TrailSerializer.Meta):
        geo_field = 'api_geom'
        id_field = 'id'
        fields = "__all__"
