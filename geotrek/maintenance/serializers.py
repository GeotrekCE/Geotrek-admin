from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers

from .models import Intervention, Project


class InterventionSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(source="name_display")
    stake = serializers.SlugRelatedField(slug_field="stake", read_only=True)
    status = serializers.SlugRelatedField(slug_field="status", read_only=True)
    type = serializers.SlugRelatedField(slug_field="type", read_only=True)
    target = serializers.CharField(source="target_display")

    class Meta:
        model = Intervention
        fields = "__all__"


class InterventionGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = Intervention
        fields = ["id", "name"]


class ProjectSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(source="name_display")
    period = serializers.CharField(source="period_display")
    type = serializers.SlugRelatedField(slug_field="type", read_only=True)
    domain = serializers.SlugRelatedField(slug_field="domain", read_only=True)

    class Meta:
        model = Project
        fields = "__all__"


class ProjectGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = Project
        fields = ["id", "name"]
