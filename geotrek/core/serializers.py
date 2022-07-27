from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers

from geotrek.core.models import Path, Trail


class PathSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    checkbox = serializers.CharField(source='checkbox_display')
    length_2d = serializers.FloatField(source='length_2d_display')
    length = serializers.FloatField(source='length_display')
    name = serializers.CharField(source='name_display')
    usages = serializers.CharField(source='usages_display')
    networks = serializers.CharField(source='networks_display')
    trails = serializers.CharField(source='trails_display')
    structure = serializers.SlugRelatedField('name', read_only=True)
    comfort = serializers.SlugRelatedField('comfort', read_only=True)
    source = serializers.SlugRelatedField('source', read_only=True)
    stake = serializers.SlugRelatedField('stake', read_only=True)

    class Meta:
        model = Path
        fields = "__all__"


class PathGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = Path
        fields = ["id", "name", "draft"]

class CertificationTrailListingField(serializers.RelatedField):
    def to_representation(self, value):
        return 'ouais'


class TrailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    length = serializers.FloatField(source='length_display')
    name = serializers.CharField(source='name_display')
    certifications = serializers.CharField(source='certifications_display')

    class Meta:
        model = Trail
        fields = "__all__"


class TrailGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = Trail
        fields = ["id", "name"]
