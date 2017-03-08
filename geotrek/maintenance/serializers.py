from rest_framework.serializers import ModelSerializer
from .models import Intervention, Project


class InterventionSerializer(ModelSerializer):
    class Meta:
        model = Intervention
        geo_field = 'geom'
        fields = (
            'id', 'name', 'date', 'type', 'infrastructure', 'status', 'stake',
            'disorders', 'total_manday', 'project', 'subcontracting',
            'width', 'height', 'length', 'area', 'structure',
            'description', 'date_insert', 'date_update',
            'material_cost', 'heliport_cost', 'subcontract_cost',
            'total_cost_mandays', 'total_cost',
            'cities', 'districts', 'areas',
            'length', 'ascent', 'descent', 'min_elevation', 'max_elevation', 'slope',
        )


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        geo_field = 'geom'
        fields = (
            'id', 'name', 'period', 'type', 'domain', 'constraint', 'global_cost',
            'interventions', 'interventions_total_cost', 'comments', 'contractors',
            'project_owner', 'project_manager', 'founders',
            'structure', 'date_insert', 'date_update',
            'cities', 'districts', 'areas',
        )
