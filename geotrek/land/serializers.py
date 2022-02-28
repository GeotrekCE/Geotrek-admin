from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityModelSerializer
from rest_framework import serializers

from geotrek.land.models import LandEdge, PhysicalEdge, CompetenceEdge, SignageManagementEdge, WorkManagementEdge


class LandEdgeSerializer(DynamicFieldsMixin, MapentityModelSerializer):
    land_type = serializers.SlugRelatedField('name', read_only=True)
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = LandEdge
        fields = (
            'id', 'land_type', 'min_elevation', 'max_elevation', 'date_update', 'length_2d', 'date_insert',
            'owner', 'agreement', 'uuid', 'length'
        )


class PhysicalEdgeSerializer(DynamicFieldsMixin, MapentityModelSerializer):
    physical_type = serializers.SlugRelatedField('name', read_only=True)
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = PhysicalEdge
        fields = (
            'id', 'physical_type', 'min_elevation', 'max_elevation', 'date_update', 'length_2d', 'date_insert',
            'eid', 'uuid', 'length'
        )


class CompetenceEdgeSerializer(DynamicFieldsMixin, MapentityModelSerializer):
    organization = serializers.SlugRelatedField('organism', read_only=True)
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = CompetenceEdge
        fields = (
            'id', 'organization', 'min_elevation', 'max_elevation', 'date_update', 'length_2d', 'date_insert',
            'eid', 'uuid', 'length'
        )


class SignageManagementEdgeSerializer(DynamicFieldsMixin, MapentityModelSerializer):
    organization = serializers.SlugRelatedField('organism', read_only=True)
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = SignageManagementEdge
        fields = (
            'id', 'organization', 'min_elevation', 'max_elevation', 'date_update', 'length_2d', 'date_insert',
            'eid', 'uuid', 'length'
        )


class WorkManagementEdgeSerializer(DynamicFieldsMixin, MapentityModelSerializer):
    organization = serializers.SlugRelatedField('organism', read_only=True)
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = WorkManagementEdge
        fields = (
            'id', 'organization', 'min_elevation', 'max_elevation', 'date_update', 'length_2d', 'date_insert',
            'eid', 'uuid', 'length'
        )
