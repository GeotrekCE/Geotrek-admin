from __future__ import unicode_literals

from django.conf import settings
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_gis import serializers as geo_serializers

from geotrek.common import models as common_models
from geotrek.tourism import models as tourism_models
from geotrek.trekking import models as trekking_models


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


class TrekListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    last_modified = serializers.SerializerMethodField(read_only=True)
    url = HyperlinkedIdentityField(view_name='apiv2:trek-detail')
    geom = serializers.SerializerMethodField(read_only=True)
    length = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    description_teaser = serializers.SerializerMethodField(read_only=True)
    difficulty = serializers.SerializerMethodField(read_only=True)

    def get_geom(self, obj):
        if obj.geom:
            return obj.geom.ewkt

    def get_last_modified(self, obj):
        # return obj.last_author.logentry_set.last().action_time
        return obj.topo_object.date_update

    def get_name(self, obj):
        names = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            names.update({language: getattr(obj, 'name_{}'.format(language))})

        return names

    def get_description(self, obj):
        descriptions = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            descriptions.update({language: getattr(obj, 'description_{}'.format(language))})

        return descriptions

    def get_description_teaser(self, obj):
        teasers = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            teasers.update({language: getattr(obj, 'description_teaser_{}'.format(language))})

        return teasers

    def get_length(self, obj):
        return obj.topo_object.length_2d

    def get_difficulty(self, obj):
        return obj.difficulty.difficulty if obj.difficulty else None

    class Meta:
        model = trekking_models.Trek
        fields = (
            'id', 'name', 'description_teaser',
            'description', 'duration', 'difficulty',
            'length', 'ascent', 'descent',
            'min_elevation', 'max_elevation', 'url',
            'geom', 'last_modified'
        )


class TrekListGeoSerializer(TrekListSerializer, geo_serializers.GeoFeatureModelSerializer):
    class Meta(TrekListSerializer.Meta):
        geo_field = 'geom'


class RoamingListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:roaming-detail')
    last_modified = serializers.SerializerMethodField(read_only=True)
    difficulty = serializers.SlugRelatedField(slug_field='difficulty', read_only=True)

    def get_last_modified(self, obj):
        # return obj.last_author.logentry_set.last().action_time
        return obj.topo_object.date_update

    class Meta:
        model = trekking_models.Trek
        fields = (
            'id', 'name', 'url', 'last_modified', 'practice',
            'difficulty', 'themes', 'networks', 'accessibilities',
        )


class RoamingListGeoSerializer(RoamingListSerializer, geo_serializers.GeoFeatureModelSerializer):
    class Meta(RoamingListSerializer.Meta):
        geo_field = 'geom'


class TrekDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    length = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    description_teaser = serializers.SerializerMethodField(read_only=True)
    pictures = serializers.SerializerMethodField(read_only=True)
    difficulty = serializers.SerializerMethodField(read_only=True)
    geom = serializers.SerializerMethodField(read_only=True)

    def get_geom(self, obj):
        return obj.geom.ewkt if obj.geom else None

    def get_name(self, obj):
        names = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            names.update({language: getattr(obj, 'name_{}'.format(language))})

        return names

    def get_description(self, obj):
        descriptions = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            descriptions.update({language: getattr(obj, 'description_{}'.format(language))})

        return descriptions

    def get_description_teaser(self, obj):
        teasers = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            teasers.update({language: getattr(obj, 'description_teaser_{}'.format(language))})

        return teasers

    def get_length(self, obj):
        return obj.topo_object.length_2d

    def get_pictures(self, obj):
        return obj.serializable_pictures

    def get_difficulty(self, obj):
        return obj.difficulty.difficulty if obj.difficulty else None

    class Meta:
        model = trekking_models.Trek
        fields = (
            'id', 'name', 'description_teaser', 'description',
            'duration', 'difficulty', 'length', 'ascent', 'descent',
            'min_elevation', 'max_elevation', 'pictures', 'geom'
        )


class TrekDetail3DSerializer(TrekDetailSerializer):
    geom = serializers.SerializerMethodField(read_only=True)

    def get_geom(self, obj):
        return obj.geom_3d.ewkt if obj.geom_3d else None

    class Meta(TrekDetailSerializer.Meta):
        geo_field = 'geom_3d'
        fields = TrekDetailSerializer.Meta.fields


class TrekDetailGeoSerializer(TrekDetailSerializer, geo_serializers.GeoFeatureModelSerializer):
    class Meta(TrekDetailSerializer.Meta):
        geo_field = 'geom'
        # auto_bbox = True


class TrekDetailGeo3DSerializer(TrekDetailGeoSerializer):
    class Meta(TrekDetailGeoSerializer.Meta):
        geo_field = 'geom_3d'
        fields = TrekDetailGeoSerializer.Meta.fields + ('geom_3d',)


class RoamingDetailSerializer(TrekDetailSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    def get_children(self, obj):
        return TrekDetailSerializer(obj.children.transform(settings.API_SRID, field_name='geom'), many=True).data

    class Meta(TrekDetailSerializer.Meta):
        fields = TrekDetailSerializer.Meta.fields + ('children',)


class RoamingDetailGeoSerializer(TrekDetailGeoSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    def get_children(self, obj):
        return TrekDetailSerializer(obj.children.transform(settings.API_SRID, field_name='geom'), many=True).data

    class Meta(TrekDetailSerializer.Meta):
        fields = TrekDetailSerializer.Meta.fields + ('children',)


class POIListSerializer(TrekListSerializer):
    url = HyperlinkedIdentityField(view_name='apiv2:poi-detail')

    class Meta(TrekListSerializer.Meta):
        model = trekking_models.POI


class POIListGeoSerializer(POIListSerializer, geo_serializers.GeoFeatureModelSerializer):
    class Meta(POIListSerializer.Meta):
        geo_field = 'geom'


class POITypeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    label = serializers.SerializerMethodField(read_only=True)

    def get_label(self, obj):
        labels = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            labels.update({language: getattr(obj, 'label_{}'.format(language))})

        return labels

    class Meta:
        model = trekking_models.POIType
        fields = ('id', 'label', 'pictogram')


class POIDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    type = POITypeSerializer(read_only=True)
    pictures = serializers.SerializerMethodField(read_only=True)

    def get_name(self, obj):
        names = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            names.update({language: getattr(obj, 'name_{}'.format(language))})

        return names

    def get_description(self, obj):
        descriptions = {}

        for language in settings.MODELTRANSLATION_LANGUAGES:
            descriptions.update({language: getattr(obj, 'description_{}'.format(language))})

        return descriptions

    def get_pictures(self, obj):
        return obj.serializable_pictures

    class Meta:
        model = trekking_models.POI
        fields = (
            'id', 'name', 'description', 'type', 'eid', 'pictures', 'geom'
        )


class POIDetailGeoSerializer(POIDetailSerializer, geo_serializers.GeoFeatureModelSerializer):
    class Meta(POIDetailSerializer.Meta):
        geo_field = 'geom'
