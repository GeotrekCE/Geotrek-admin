from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers

from geotrek.land.models import LandEdge, PhysicalEdge, CompetenceEdge, SignageManagementEdge, WorkManagementEdge


class LandEdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    land_type = serializers.CharField(source='land_type_display')
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = LandEdge
        fields = "__all__"


class PhysicalEdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    physical_type = serializers.CharField(source='physical_type_display')
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = PhysicalEdge
        fields = "__all__"


class CompetenceEdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    organization = serializers.CharField(source='organization_display')
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = CompetenceEdge
        fields = "__all__"


class SignageManagementEdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    organization = serializers.CharField(source='organization_display')
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = SignageManagementEdge
        fields = "__all__"


class WorkManagementEdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    organization = serializers.CharField(source='organization_display')
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = WorkManagementEdge
        fields = "__all__"
