from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers

from geotrek.land.models import LandEdge, PhysicalEdge, CompetenceEdge, SignageManagementEdge, WorkManagementEdge


class LandEdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    land_type = serializers.CharField(source='land_type_display')
    length = serializers.FloatField(source='length_display')
    length_2d = serializers.FloatField(source='length_2d_display')

    class Meta:
        model = LandEdge
        fields = "__all__"


class LandEdgeGeojsonSerializer(MapentityGeojsonModelSerializer):
    color_index = serializers.IntegerField()
    name = serializers.CharField()

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = LandEdge
        fields = ["id", "name", "color_index"]


class PhysicalEdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    physical_type = serializers.CharField(source='physical_type_display')
    length = serializers.FloatField(source='length_display')
    length_2d = serializers.FloatField(source='length_2d_display')

    class Meta:
        model = PhysicalEdge
        fields = "__all__"


class PhysicalEdgeGeojsonSerializer(MapentityGeojsonModelSerializer):
    color_index = serializers.IntegerField()
    name = serializers.CharField()

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = PhysicalEdge
        fields = ["id", "name", "color_index"]


class CompetenceEdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    organization = serializers.CharField(source='organization_display')
    length = serializers.FloatField(source='length_display')
    length_2d = serializers.FloatField(source='length_2d_display')

    class Meta:
        model = CompetenceEdge
        fields = "__all__"


class CompetenceEdgeGeojsonSerializer(MapentityGeojsonModelSerializer):
    color_index = serializers.IntegerField()
    name = serializers.CharField()

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = CompetenceEdge
        fields = ["id", "name", "color_index"]


class SignageManagementEdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    organization = serializers.CharField(source='organization_display')
    length = serializers.FloatField(source='length_display')
    length_2d = serializers.FloatField(source='length_2d_display')

    class Meta:
        model = SignageManagementEdge
        fields = "__all__"


class SignageManagementEdgeGeojsonSerializer(MapentityGeojsonModelSerializer):
    color_index = serializers.IntegerField()
    name = serializers.CharField()

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = SignageManagementEdge
        fields = ["id", "name", "color_index"]


class WorkManagementEdgeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    organization = serializers.CharField(source='organization_display')
    length = serializers.FloatField(source='length_display')
    length_2d = serializers.FloatField(source='length_2d_display')

    class Meta:
        model = WorkManagementEdge
        fields = "__all__"


class WorkManagementEdgeGeojsonSerializer(MapentityGeojsonModelSerializer):
    color_index = serializers.IntegerField()
    name = serializers.CharField()

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = WorkManagementEdge
        fields = ["id", "name", "color_index"]
