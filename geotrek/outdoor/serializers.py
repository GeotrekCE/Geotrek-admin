from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityModelSerializer
from rest_framework import serializers

from geotrek.outdoor.models import Course, Site


class SiteSerializer(DynamicFieldsMixin, MapentityModelSerializer):
    super_practices = serializers.CharField()
    structure = serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = Site
        fields = ('id', 'structure', 'name', 'super_practices', 'date_update', 'date_insert')


class CourseSerializer(DynamicFieldsMixin, MapentityModelSerializer):
    structure = serializers.SlugRelatedField('name', read_only=True)
    parent_sites = serializers.CharField(source='parent_sites_display')

    class Meta:
        model = Course
        fields = (
            'id', 'structure', 'name', 'parent_sites', 'description', 'duration', 'advice', 'date_insert',
            'date_update', 'equipment', 'accessibility', 'height', 'eid', 'ratings', 'ratings_description',
            'gear', 'type'
        )
