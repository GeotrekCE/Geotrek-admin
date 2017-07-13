from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_gis import serializers as geo_serializers

from geotrek.api.v2.functions import Transform, Length, Length3D
from geotrek.api.v2.utils import get_translation_or_dict
from geotrek.common import models as common_models
from geotrek.core import models as core_models
from geotrek.tourism import models as tourism_models
from geotrek.trekking import models as trekking_models


class Base3DSerializer(object):
    """
    Mixin used to replace geom with geom_3d field
    """
    geometry = geo_serializers.GeometryField(read_only=True)

    def get_geometry(self, obj):
        return obj.geom3d_transformed


class BaseGeoJSONSerializer(geo_serializers.GeoFeatureModelSerializer):
    """
    Mixin used to serialize geojson
    """

    class Meta:
        geo_field = 'geometry'
        auto_bbox = True


def override_serializer(format_output, dimension, base_serializer_class):
    """
    Override Serializer switch output format and dimension data
    """
    if format_output == 'geojson':
        if dimension == '3':
            class GeneratedGeo3DSerializer(Base3DSerializer,
                                           BaseGeoJSONSerializer,
                                           base_serializer_class):
                class Meta(BaseGeoJSONSerializer.Meta,
                           base_serializer_class.Meta):
                    pass

            final_class = GeneratedGeo3DSerializer

        else:
            class GeneratedGeoSerializer(BaseGeoJSONSerializer,
                                         base_serializer_class):
                class Meta(BaseGeoJSONSerializer.Meta,
                           base_serializer_class.Meta):
                    pass

            final_class = GeneratedGeoSerializer
    else:
        if dimension == '3':
            class Generated3DSerializer(Base3DSerializer,
                                        base_serializer_class):
                class Meta(base_serializer_class.Meta):
                    pass

            final_class = Generated3DSerializer

        else:
            final_class = base_serializer_class

    return final_class


class TrekThemeSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField(read_only=True)

    def get_label(self, obj):
        return get_translation_or_dict('label', self, obj)

    class Meta:
        model = trekking_models.Theme
        fields = ('id', 'label', 'pictogram')


class TrekNetworkSerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField(read_only=True)

    def get_label(self, obj):
        return get_translation_or_dict('network', self, obj)

    class Meta:
        model = trekking_models.TrekNetwork
        fields = ('id', 'label', 'pictogram')


class TrekPracticeInTrekSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        return get_translation_or_dict('name', self, obj)

    class Meta:
        model = trekking_models.Practice
        fields = ('id', 'name', 'pictogram',)


class TrekPracticeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        return get_translation_or_dict('name', self, obj)

    class Meta:
        model = trekking_models.Practice
        fields = ('id', 'name', 'order', 'pictogram',)


class DifficultySerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField(read_only=True)

    def get_label(self, obj):
        return get_translation_or_dict('difficulty', self, obj)

    class Meta:
        model = trekking_models.DifficultyLevel
        fields = ('id', 'label', 'cirkwi_level', 'pictogram')


class AttachmentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = serializers.FileField(source='attachment_file')

    class Meta:
        model = common_models.Attachment
        fields = (
            'url', 'author', 'title', 'legend',
            'starred', 'date_insert', 'date_update'
        )


class TouristicContentCategorySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = tourism_models.TouristicContentCategory
        fields = ('id', 'label', 'pictogram', 'type1_label', 'type2_label', 'order')


class TouristicContentListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:touristiccontent-detail')
    category = TouristicContentCategorySerializer()
    geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)

    def get_geometry(self, obj):
        return obj.geom2d_transformed

    class Meta:
        model = tourism_models.TouristicContent
        fields = ('id', 'url', 'description_teaser', 'description', 'category', 'approved', 'geometry')


class TouristicContentDetailSerializer(TouristicContentListSerializer):
    pictures = serializers.SerializerMethodField()

    def get_pictures(self, obj):
        return obj.pictures

    class Meta(TouristicContentListSerializer.Meta):
        fields = tuple(field for field in TouristicContentListSerializer.Meta.fields if field != 'url') + ('pictures',)


class PathListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:trek-detail')
    geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)
    length_2d = serializers.SerializerMethodField(read_only=True)
    length_3d = serializers.SerializerMethodField(read_only=True)

    def get_length_2d(self, obj):
        return round(obj.length_2d_m, 1)

    def get_length_3d(self, obj):
        return round(obj.length_3d_m, 1)

    def get_geometry(self, obj):
        return obj.geom2d_transformed

    class Meta:
        model = core_models.Path
        fields = ('id', 'name', 'comments', 'url', 'length_2d', 'length_3d', 'geometry')


class TrekListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:trek-detail')
    published = serializers.SerializerMethodField(read_only=True)
    geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)
    length_2d = serializers.SerializerMethodField(read_only=True)
    length_3d = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    description_teaser = serializers.SerializerMethodField(read_only=True)
    difficulty = DifficultySerializer(read_only=True)
    departure = serializers.SerializerMethodField(read_only=True)
    arrival = serializers.SerializerMethodField(read_only=True)
    themes = TrekThemeSerializer(many=True, read_only=True)
    networks = TrekNetworkSerializer(many=True, read_only=True)
    practice = TrekPracticeInTrekSerializer(read_only=True)
    external_id = serializers.SerializerMethodField(read_only=True)
    create_datetime = serializers.SerializerMethodField(read_only=True)
    update_datetime = serializers.SerializerMethodField(read_only=True)

    def get_update_datetime(self, obj):
        return obj.topo_object.date_update

    def get_create_datetime(self, obj):
        return obj.topo_object.date_insert

    def get_published(self, obj):
        return get_translation_or_dict('published', self, obj)

    def get_name(self, obj):
        return get_translation_or_dict('name', self, obj)

    def get_description(self, obj):
        return get_translation_or_dict('description', self, obj)

    def get_departure(self, obj):
        return get_translation_or_dict('departure', self, obj)

    def get_arrival(self, obj):
        return get_translation_or_dict('arrival', self, obj)

    def get_description_teaser(self, obj):
        return get_translation_or_dict('description_teaser', self, obj)

    def get_length_2d(self, obj):
        return round(obj.length_2d_m, 1)

    def get_length_3d(self, obj):
        return round(obj.length_3d_m, 1)

    def get_external_id(self, obj):
        return obj.eid

    def get_geometry(self, obj):
        return obj.geom2d_transformed

    class Meta:
        model = trekking_models.Trek
        fields = (
            'id', 'url', 'name', 'description_teaser',
            'description', 'departure', 'arrival', 'duration',
            'difficulty', 'length_2d', 'length_3d', 'ascent', 'descent',
            'min_elevation', 'max_elevation', 'themes', 'networks', 'practice',
            'external_id', 'published',
            'geometry', 'update_datetime', 'create_datetime'
        )


class TrekDetailSerializer(TrekListSerializer):
    pictures = AttachmentSerializer(many=True, )

    class Meta(TrekListSerializer.Meta):
        fields = tuple((field for field in TrekListSerializer.Meta.fields if field != 'url')) + ('pictures',)


class TourListSerializer(TrekListSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:tour-detail')
    count_children = serializers.SerializerMethodField(read_only=True)

    def get_count_children(self, obj):
        return obj.count_children

    class Meta(TrekListSerializer.Meta):
        fields = TrekListSerializer.Meta.fields + ('count_children',)


class TourDetailSerializer(TrekDetailSerializer):
    steps = serializers.SerializerMethodField(read_only=True)

    def get_steps(self, obj):
        qs = obj.children \
            .select_related('topo_object', 'difficulty') \
            .prefetch_related('topo_object__aggregations', 'themes', 'networks', 'attachments') \
            .annotate(geom2d_transformed=Transform('geom', settings.API_SRID),
                      geom3d_transformed=Transform('geom_3d', settings.API_SRID),
                      length_2d_m=Length('geom'),
                      length_3d_m=Length3D('geom_3d'))
        FinalClass = override_serializer(self.context.get('request').GET.get('format'),
                                         self.context.get('request').GET.get('dim'),
                                         TrekDetailSerializer)
        return FinalClass(qs,
                          many=True).data

    class Meta(TrekDetailSerializer.Meta):
        fields = TrekDetailSerializer.Meta.fields + ('steps',)


class POITypeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    label = serializers.SerializerMethodField(read_only=True)

    def get_label(self, obj):
        return get_translation_or_dict('label', self, obj)

    class Meta:
        model = trekking_models.POIType
        fields = ('id', 'label', 'pictogram')


class POIListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:poi-detail')
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    external_id = serializers.SerializerMethodField(read_only=True, help_text=_("External ID"))
    published = serializers.SerializerMethodField(read_only=True)
    create_datetime = serializers.SerializerMethodField(read_only=True)
    update_datetime = serializers.SerializerMethodField(read_only=True)
    geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)
    type = POITypeSerializer(read_only=True)

    def get_published(self, obj):
        return get_translation_or_dict('published', self, obj)

    def get_external_id(self, obj):
        return obj.eid

    def get_name(self, obj):
        return get_translation_or_dict('name', self, obj)

    def get_update_datetime(self, obj):
        return obj.topo_object.date_update

    def get_create_datetime(self, obj):
        return obj.topo_object.date_insert

    def get_description(self, obj):
        return get_translation_or_dict('description', self, obj)

    def get_geometry(self, obj):
        return obj.geom2d_transformed

    class Meta:
        model = trekking_models.POI
        fields = (
            'id', 'url', 'name', 'type', 'description', 'external_id',
            'published',
            'geometry', 'update_datetime', 'create_datetime'
        )


class POIDetailSerializer(POIListSerializer):
    pictures = AttachmentSerializer(many=True, )

    class Meta(POIListSerializer.Meta):
        fields = tuple((field for field in POIListSerializer.Meta.fields if field != 'url')) + ('pictures',)
