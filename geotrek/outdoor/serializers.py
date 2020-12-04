from rest_framework.serializers import ModelSerializer
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.outdoor.models import Site


class SiteSerializer(ModelSerializer):
    class Meta:
        model = Site
        fields = ('id', 'name', 'description')


class SiteGeojsonSerializer(GeoFeatureModelSerializer, SiteSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(SiteSerializer.Meta):
        geo_field = 'api_geom'
        fields = SiteSerializer.Meta.fields + ('api_geom', )
