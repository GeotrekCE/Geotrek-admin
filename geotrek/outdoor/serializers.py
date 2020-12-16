from rest_framework.serializers import ModelSerializer
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import PublishableSerializerMixin, TranslatedModelSerializer
from geotrek.outdoor.models import Practice, Site
from geotrek.zoning.serializers import ZoningSerializerMixin


class PracticeSerializer(ModelSerializer):
    class Meta:
        model = Practice
        fields = ('id', 'name')


class SiteSerializer(PublishableSerializerMixin, ZoningSerializerMixin, TranslatedModelSerializer):
    practice = PracticeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = Site
        fields = ('id', 'structure', 'name', 'practice', 'description', 'description_teaser',
                  'ambiance', 'advice', 'period', 'eid') + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields


class SiteGeojsonSerializer(GeoFeatureModelSerializer, SiteSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(SiteSerializer.Meta):
        geo_field = 'api_geom'
        fields = SiteSerializer.Meta.fields + ('api_geom', )
