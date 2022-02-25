from mapentity.serializers.fields import MapentityBooleanField
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.common.api.mixins.serializers import TimeStampedModelSerializerMixin
from geotrek.core.models import Path, Trail


class PathSerializer(TimeStampedModelSerializerMixin, serializers.ModelSerializer):
    checkbox = serializers.CharField()
    length_2d = serializers.SerializerMethodField()
    length = serializers.FloatField(source='length_display')
    name = serializers.CharField(source='name_display')
    valid = MapentityBooleanField()
    draft = MapentityBooleanField()
    visible = MapentityBooleanField()
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
        fields = (
            'id', 'checkbox', 'arrival', 'ascent', 'departure', 'descent', 'draft', 'eid', 'length', 'length_2d',
            'max_elevation', 'min_elevation', 'name', 'slope', 'valid', 'visible', 'structure',
            'stake', 'networks', 'comments', "comfort", "source", "usages", "draft", "trails", "uuid",
        ) + TimeStampedModelSerializerMixin.Meta.fields


class PathGeojsonSerializer(GeoFeatureModelSerializer, PathSerializer):
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(PathSerializer.Meta):
        geo_field = 'api_geom'
        id_field = 'id'
        fields = PathSerializer.Meta.fields + ('api_geom', )


class TrailSerializer(TimeStampedModelSerializerMixin, serializers.ModelSerializer):
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = Trail
        fields = (
            'id', 'arrival', 'departure', 'comments', 'name', 'length', 'uuid',
            'length_2d', 'structure', 'min_elevation', 'max_elevation') + TimeStampedModelSerializerMixin.Meta.fields


class TrailGeojsonSerializer(GeoFeatureModelSerializer, TrailSerializer):
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(TrailSerializer.Meta):
        geo_field = 'api_geom'
        id_field = 'id'
        fields = TrailSerializer.Meta.fields + ('api_geom', )
