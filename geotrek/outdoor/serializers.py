from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers

from .models import Course, Practice, Site


class PracticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Practice
        fields = ("id", "name")


class SiteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Practice
        fields = ("id", "name")


class SiteSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(source="name_display")
    super_practices = serializers.CharField(source="super_practices_display")
    structure = serializers.SlugRelatedField("name", read_only=True)

    class Meta:
        model = Site
        fields = "__all__"


class SiteGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = Site
        fields = ["id", "name"]


class CourseSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    structure = serializers.SlugRelatedField("name", read_only=True)
    parent_sites = serializers.CharField(source="parent_sites_display")
    name = serializers.CharField(source="name_display")

    class Meta:
        model = Course
        fields = "__all__"


class CourseGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = Course
        fields = ["id", "name"]
