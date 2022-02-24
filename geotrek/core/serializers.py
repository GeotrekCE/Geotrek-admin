from mapentity.serializers.fields import MapentityBooleanField, MapentityDateTimeField
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.core.models import Path, Trail


class PathSerializer(serializers.ModelSerializer):
    checkbox = serializers.CharField()
    length_2d = serializers.SerializerMethodField()
    length = serializers.FloatField(source='length_display')
    name = serializers.CharField(source='name_display')
    valid = MapentityBooleanField()
    draft = MapentityBooleanField()
    visible = MapentityBooleanField()
    date_update = MapentityDateTimeField()
    date_insert = MapentityDateTimeField()
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
            'max_elevation', 'min_elevation', 'name', 'slope', 'valid', 'visible', 'structure', 'date_update',
            'date_insert', 'stake', 'networks', 'comments', "comfort", "source", "usages", "draft", "trails", "uuid",
        )


class PathGeojsonSerializer(GeoFeatureModelSerializer, PathSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(PathSerializer.Meta):
        geo_field = 'api_geom'
        id_field = 'id'
        fields = PathSerializer.Meta.fields + ('api_geom', )


class TrailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trail
        id_field = 'id'
        fields = ('id', 'arrival', 'departure', 'comments', 'name')


class TrailGeojsonSerializer(GeoFeatureModelSerializer, TrailSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(TrailSerializer.Meta):
        geo_field = 'api_geom'
        fields = TrailSerializer.Meta.fields + ('api_geom', )
