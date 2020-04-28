from rest_framework.serializers import ModelSerializer
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.core.models import Path, Trail


class PathSerializer(ModelSerializer):
    class Meta:
        model = Path
        id_field = 'id'
        fields = (
            'id', 'arrival', 'ascent', 'departure', 'descent', 'draft', 'eid', 'length',
            'max_elevation', 'min_elevation', 'name', 'slope', 'valid', 'visible',
        )


class PathGeojsonSerializer(GeoFeatureModelSerializer, PathSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(PathSerializer.Meta):
        geo_field = 'api_geom'
        fields = PathSerializer.Meta.fields + ('api_geom', )


class TrailSerializer(ModelSerializer):
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
