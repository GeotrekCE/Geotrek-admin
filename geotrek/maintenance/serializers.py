from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Intervention, Project


class InterventionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(source='name_display')
    stake = serializers.SlugRelatedField(slug_field='stake', read_only=True)
    status = serializers.SlugRelatedField(slug_field='status', read_only=True)
    type = serializers.SlugRelatedField(slug_field='type', read_only=True)
    target = serializers.CharField(source='target_display')

    class Meta:
        model = Intervention
        fields = "__all__"


class InterventionGeojsonSerializer(GeoFeatureModelSerializer, InterventionSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(InterventionSerializer.Meta):
        geo_field = 'api_geom'


class ProjectSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(source='name_display')

    class Meta:
        model = Project
        fields = "__all__"


class ProjectGeojsonSerializer(GeoFeatureModelSerializer, ProjectSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(ProjectSerializer.Meta):
        geo_field = 'api_geom'
