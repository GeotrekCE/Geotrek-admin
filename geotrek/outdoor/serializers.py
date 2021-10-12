from rest_framework.serializers import ModelSerializer, ReadOnlyField
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import (PublishableSerializerMixin, TranslatedModelSerializer,
                                        LabelSerializer, ThemeSerializer, TargetPortalSerializer,
                                        RecordSourceSerializer)
from geotrek.outdoor.models import Practice, Site, Course
from geotrek.tourism.serializers import InformationDeskSerializer
from geotrek.trekking.serializers import WebLinkSerializer
from geotrek.zoning.serializers import ZoningSerializerMixin


class PracticeSerializer(ModelSerializer):
    class Meta:
        model = Practice
        fields = ('id', 'name')


class SiteTypeSerializer(ModelSerializer):
    class Meta:
        model = Practice
        fields = ('id', 'name')


class SiteSerializer(PublishableSerializerMixin, ZoningSerializerMixin, TranslatedModelSerializer):
    practice = PracticeSerializer()
    structure = StructureSerializer()
    labels = LabelSerializer(many=True)
    themes = ThemeSerializer(many=True)
    portal = TargetPortalSerializer(many=True)
    source = RecordSourceSerializer(many=True)
    information_desks = InformationDeskSerializer(many=True)
    web_links = WebLinkSerializer(many=True)
    type = SiteTypeSerializer()
    children = ReadOnlyField(source='published_children')

    class Meta:
        model = Site
        fields = ('id', 'structure', 'name', 'practice', 'description', 'description_teaser',
                  'ambiance', 'advice', 'period', 'labels', 'themes', 'portal', 'source',
                  'information_desks', 'web_links', 'type', 'parent', 'children', 'eid',
                  'orientation', 'wind', 'ratings') + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields


class SiteGeojsonSerializer(GeoFeatureModelSerializer, SiteSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(SiteSerializer.Meta):
        geo_field = 'api_geom'
        fields = SiteSerializer.Meta.fields + ('api_geom', )


class CourseSerializer(PublishableSerializerMixin, ZoningSerializerMixin, TranslatedModelSerializer):
    structure = StructureSerializer()

    class Meta:
        model = Course
        fields = ('id', 'structure', 'name', 'parent_sites', 'description', 'duration', 'advice',
                  'equipment', 'height', 'eid', 'ratings', 'ratings_description', 'gear', 'type') + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields


class CourseGeojsonSerializer(GeoFeatureModelSerializer, CourseSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    class Meta(CourseSerializer.Meta):
        geo_field = 'api_geom'
        fields = CourseSerializer.Meta.fields + ('api_geom', )
