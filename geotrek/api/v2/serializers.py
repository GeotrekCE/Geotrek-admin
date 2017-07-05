from __future__ import unicode_literals

from django.conf import settings
from django.utils.translation import ugettext_lazy as _, activate, deactivate
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_gis import serializers as geo_serializers

from geotrek.api.v2.utils import get_translation_or_dict
from geotrek.api.v2.functions import Transform
from geotrek.common import models as common_models
from geotrek.tourism import models as tourism_models
from geotrek.trekking import models as trekking_models
from geotrek.core import models as core_models


class Base3DSerializer(object):
    """
    Mixin use to replace geom with geom_3d field
    """
    geometry = geo_serializers.GeometryField(read_only=True)

    def get_geometry(self, obj):
        return obj.geom3d_transformed


class BaseGeoJSONSerializer(geo_serializers.GeoFeatureModelSerializer):
    """
    Mixin use to serialize in geojson
    """
    class Meta:
        geo_field = 'geometry'
        auto_bbox = True


def override_serializer(format_output, dimension, base_serializer_class):
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


class DifficultySerializer(serializers.ModelSerializer):
    label = serializers.SerializerMethodField(read_only=True)

    def get_label(self, obj):
        return get_translation_or_dict('difficulty', self, obj)

    class Meta:
        model = trekking_models.DifficultyLevel
        fields = ('id', 'label', 'cirkwi_level')


class FileTypeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = common_models.FileType
        fields = ('type')


class AttachmentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    file_type = FileTypeSerializer(read_only=True)

    class Meta:
        model = common_models.Attachment
        fields = ('file_type', 'attachment_file', 'creator', 'author', 'title', 'legend', 'starred',
                  'date_insert', 'date_update')


class TouristicContentCategorySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = tourism_models.TouristicContentCategory
        fields = ('id', 'label', 'pictogram', 'type1_label', 'type2_label', 'order')


class TouristicContentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:touristiccontent-detail')
    category = TouristicContentCategorySerializer()
    location = serializers.SerializerMethodField()

    def get_location(self, obj):
        location = obj.geom.transform(settings.API_SRID, clone=True)
        return {
            'latitude': location.y,
            'longitude': location.x
        }

    class Meta:
        model = tourism_models.TouristicContent
        fields = ('id', 'url', 'description_teaser', 'description', 'category', 'approved', 'location')


class TouristicContentGeoSerializer(TouristicContentSerializer, geo_serializers.GeoFeatureModelSerializer):
    class Meta(TouristicContentSerializer.Meta):
        geo_field = 'geom'


class TouristicContentDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    category = TouristicContentCategorySerializer()
    pictures = serializers.SerializerMethodField()

    def get_pictures(self, obj):
        return obj.serializable_pictures

    class Meta:
        model = tourism_models.TouristicContent
        fields = (
            'id', 'description_teaser', 'description', 'themes',
            'category', 'contact', 'email', 'website', 'practical_info',
            'source', 'portal', 'eid', 'reservation_id', 'approved',
            'pictures', 'geom'
        )


class TouristicContentGeoDetailSerializer(TouristicContentDetailSerializer, geo_serializers.GeoFeatureModelSerializer):
    class Meta(TouristicContentDetailSerializer.Meta):
        geo_field = 'geom'


class PathListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = core_models.Path
        fields = "__all__"


class TrekListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    create_datetime = serializers.SerializerMethodField(read_only=True)
    update_datetime = serializers.SerializerMethodField(read_only=True)
    url = HyperlinkedIdentityField(view_name='apiv2:trek-detail')
    geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)
    length = serializers.SerializerMethodField(read_only=True)
    length_3d = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    description_teaser = serializers.SerializerMethodField(read_only=True)
    difficulty = DifficultySerializer(read_only=True)
    departure = serializers.SerializerMethodField(read_only=True)
    arrival = serializers.SerializerMethodField(read_only=True)

    def get_update_datetime(self, obj):
        return obj.topo_object.date_update

    def get_create_datetime(self, obj):
        return obj.topo_object.date_insert

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

    def get_length(self, obj):
        return round(obj.geom.length, 1) if obj.geom else None

    def get_length_3d(self, obj):
        return round(obj.geom_3d.length, 1) if obj.geom_3d else None

    def get_difficulty(self, obj):
        return obj.difficulty.difficulty if obj.difficulty else None

    def get_geometry(self, obj):
        return obj.geom2d_transformed

    class Meta:
        model = trekking_models.Trek
        fields = (
            'id', 'name', 'description_teaser',
            'description', 'departure', 'arrival', 'duration', 'difficulty',
            'length', 'length_3d', 'ascent', 'descent',
            'min_elevation', 'max_elevation', 'url',
            'geometry', 'update_datetime', 'create_datetime'
        )


class TrekDetailSerializer(TrekListSerializer):
    pass

    class Meta(TrekListSerializer.Meta):
        fields = fields = (
            'id', 'name', 'description_teaser',
            'description', 'duration', 'difficulty',
            'length', 'length_3d', 'ascent', 'descent',
            'min_elevation', 'max_elevation',
            'geometry', 'update_datetime', 'create_datetime'
        )


class RoamingListSerializer(TrekListSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:roaming-detail')
    count_children = serializers.SerializerMethodField(read_only=True)

    def get_count_children(self, obj):
        return obj.count_children

    class Meta(TrekListSerializer.Meta):
        fields = TrekListSerializer.Meta.fields + ('count_children',)


class RoamingDetailSerializer(TrekDetailSerializer):
    steps = serializers.SerializerMethodField(read_only=True)

    def get_steps(self, obj):
        qs = obj.children.annotate(geom2d_transformed=Transform('geom', settings.API_SRID),
                                   geom3d_transformed=Transform('geom_3d', settings.API_SRID))
        FinalClass = override_serializer(self.context.get('request').query_params.get('format'),
                                         self.context.get('request').query_params.get('dim'),
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
    create_datetime = serializers.SerializerMethodField(read_only=True)
    update_datetime = serializers.SerializerMethodField(read_only=True)
    geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)
    type = POITypeSerializer(read_only=True)
    pictures = serializers.SerializerMethodField(read_only=True)

    def get_pictures(self, obj):
        return obj.serializable_pictures

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
            'id','url', 'name', 'type', 'description', 'external_id',
            'pictures',
            'geometry', 'update_datetime', 'create_datetime'
        )


class POIDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    pictures = serializers.SerializerMethodField(read_only=True)
    type = POITypeSerializer(read_only=True)

    def get_name(self, obj):
        return get_translation_or_dict('name', self, obj)

    def get_description(self, obj):
        descriptions = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            descriptions.update({language: getattr(obj, 'description_{}'.format(language))})

        return descriptions

    def get_pictures(self, obj):
        return obj.serializable_pictures

    class Meta:
        model = trekking_models.POI
        fields = "__all__"
