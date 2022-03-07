from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers

from geotrek.outdoor.models import Course, Site


class SiteSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    super_practices = serializers.CharField()
    structure = serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = Site
        fields = ('id', 'structure', 'name', 'super_practices', 'date_update', 'date_insert')


class CourseSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    structure = serializers.SlugRelatedField('name', read_only=True)
    parent_sites = serializers.CharField(source='parent_sites_display')

    class Meta:
        model = Course
        fields = (
            'id', 'structure', 'name', 'parent_sites', 'description', 'duration', 'advice', 'date_insert',
            'date_update', 'equipment', 'accessibility', 'height', 'eid', 'ratings', 'ratings_description',
            'gear', 'type'
        )
