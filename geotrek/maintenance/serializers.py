from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import Intervention, Project


class InterventionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Intervention
        fields = (
            'id', 'name', 'date', 'type', 'status', 'stake',
            'disorders', 'total_manday', 'subcontracting',
            'width', 'height', 'length', 'area', 'structure',
            'description', 'date_insert', 'date_update',
            'material_cost', 'heliport_cost', 'subcontract_cost',
            'total_cost_mandays', 'total_cost',
            'cities', 'districts', 'areas',
            'length', 'ascent', 'descent', 'min_elevation', 'max_elevation', 'slope',
        )


class InterventionGeojsonSerializer(GeoFeatureModelSerializer, InterventionSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(InterventionSerializer.Meta):
        geo_field = 'api_geom'
        fields = InterventionSerializer.Meta.fields + ('api_geom', )


class ProjectSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='name_display')

    class Meta:
        model = Project
        fields = (
            'id', 'name', 'period', 'type', 'domain', 'constraint', 'global_cost',
            'interventions', 'interventions_total_cost', 'comments', 'contractors',
            'project_owner', 'project_manager', 'founders',
            'structure', 'date_insert', 'date_update',
            'cities', 'districts', 'areas',
        )


class ProjectGeojsonSerializer(GeoFeatureModelSerializer, ProjectSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(ProjectSerializer.Meta):
        geo_field = 'api_geom'
        fields = ProjectSerializer.Meta.fields + ('api_geom', )
