import json

from django.conf import settings
from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import (LabelSerializer,
                                        PublishableSerializerMixin,
                                        RecordSourceSerializer,
                                        TargetPortalSerializer,
                                        ThemeSerializer,
                                        TranslatedModelSerializer)
from geotrek.tourism.serializers import InformationDeskSerializer
from geotrek.trekking.serializers import WebLinkSerializer
from geotrek.zoning.serializers import ZoningAPISerializerMixin
from .models import Course, Site, Practice


class PracticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Practice
        fields = ('id', 'name')


class SiteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Practice
        fields = ('id', 'name')


class SiteSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    checkbox = serializers.CharField(source='checkbox_display')
    name = serializers.CharField(source='name_display')
    super_practices = serializers.CharField(source='super_practices_display')
    structure = serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = Site
        fields = "__all__"


class SiteGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = Site
        fields = ["id", "name"]


class SiteAPISerializer(PublishableSerializerMixin, ZoningAPISerializerMixin, TranslatedModelSerializer):
    practice = PracticeSerializer()
    structure = StructureSerializer()
    labels = LabelSerializer(many=True)
    themes = ThemeSerializer(many=True)
    portal = TargetPortalSerializer(many=True)
    source = RecordSourceSerializer(many=True)
    information_desks = InformationDeskSerializer(many=True)
    web_links = WebLinkSerializer(many=True)
    type = SiteTypeSerializer()
    children = serializers.ReadOnlyField(source='published_children')

    class Meta:
        model = Site
        fields = (
            'id', 'structure', 'name', 'practice', 'accessibility', 'description', 'description_teaser',
            'ambiance', 'advice', 'period', 'labels', 'themes', 'portal', 'source',
            'information_desks', 'web_links', 'type', 'parent', 'children', 'eid',
            'orientation', 'wind', 'ratings'
        ) + ZoningAPISerializerMixin.Meta.fields + PublishableSerializerMixin.Meta.fields


class SiteAPIGeojsonSerializer(GeoFeatureModelSerializer, SiteAPISerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(SiteAPISerializer.Meta):
        geo_field = 'api_geom'
        fields = SiteAPISerializer.Meta.fields + ('api_geom', )


class CourseSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    checkbox = serializers.CharField(source='checkbox_display')
    structure = serializers.SlugRelatedField('name', read_only=True)
    parent_sites = serializers.CharField(source='parent_sites_display')
    name = serializers.CharField(source='name_display')

    class Meta:
        model = Course
        fields = "__all__"


class CourseGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = Course
        fields = ["id", "name"]


class CourseAPISerializer(PublishableSerializerMixin, ZoningAPISerializerMixin, TranslatedModelSerializer):
    structure = StructureSerializer()
    points_reference = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id', 'structure', 'name', 'parent_sites', 'description', 'duration', 'advice', 'points_reference',
            'equipment', 'accessibility', 'height', 'eid', 'ratings', 'ratings_description', 'gear', 'type'
        ) + ZoningAPISerializerMixin.Meta.fields + PublishableSerializerMixin.Meta.fields

    def get_points_reference(self, obj):
        if not obj.points_reference:
            return None
        geojson = obj.points_reference.transform(settings.API_SRID, clone=True).geojson
        return json.loads(geojson)


class CourseAPIGeojsonSerializer(GeoFeatureModelSerializer, CourseAPISerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(CourseAPISerializer.Meta):
        geo_field = 'api_geom'
        fields = CourseAPISerializer.Meta.fields + ('api_geom', )
