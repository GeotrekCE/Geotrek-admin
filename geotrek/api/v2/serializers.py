from django.conf import settings
from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_gis import serializers as geo_serializers
from geotrek.tourism import models as tourism_models
from geotrek.trekking import models as trekking_models


class TouristicContentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = tourism_models.TouristicContentCategory
        fields = ('id', 'label', 'pictogram', 'type1_label', 'type2_label', 'order')


class TouristicContentSerializer(geo_serializers.GeoFeatureModelSerializer):
    category = TouristicContentCategorySerializer()

    class Meta:
        model = tourism_models.TouristicContent
        geo_field = 'geom'
        fields = ('id', 'description_teaser', 'description', 'category', 'approved')


class TouristicContentDetailSerializer(geo_serializers.GeoFeatureModelSerializer):
    category = TouristicContentCategorySerializer()

    class Meta:
        model = tourism_models.TouristicContent
        geo_field = 'geom'
        fields = (
            'id', 'description_teaser', 'description', 'themes',
            'category', 'contact', 'email', 'website', 'practical_info',
            'source', 'portal', 'eid',
            'reservation_id', 'approved'
        )


class TrekListSerializer(serializers.ModelSerializer):
    last_modified = serializers.SerializerMethodField(read_only=True)
    url = HyperlinkedIdentityField(view_name='apiv2:trek-detail')

    def get_last_modified(self, obj):
        #return obj.last_author.logentry_set.last().action_time
        return obj.topo_object.date_update

    class Meta:
        model = trekking_models.Trek
        fields = (
            'id', 'url', 'last_modified'
        )


class TrekDetailSerializer(geo_serializers.GeoFeatureModelSerializer):
    length = serializers.SerializerMethodField(read_only=True)
    name = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)
    description_teaser = serializers.SerializerMethodField(read_only=True)
    pictures = serializers.SerializerMethodField(read_only=True)
    difficulty = serializers.SerializerMethodField(read_only=True)

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
        difficulties = {}

        if obj.difficulty:
            for language in settings.MODELTRANSLATION_LANGUAGES:
                difficulties.update({language: getattr(obj.difficulty, 'difficulty_{}'.format(language), '')})

            return difficulties

        else:
            return None

    class Meta:
        model = trekking_models.Trek
        geo_field = 'geom'
        auto_bbox = True
        fields = (
            'id', 'name', 'description_teaser', 'description',
            'duration', 'difficulty', 'length', 'ascent', 'descent',
            'min_elevation', 'max_elevation', 'pictures'
        )


class ItineranceDetailSerializer(TrekDetailSerializer):
    children = serializers.SerializerMethodField(read_only=True)

    def get_children(self, obj):
        return TrekDetailSerializer(obj.children.transform(settings.API_SRID, field_name='geom'), many=True).data

    class Meta(TrekDetailSerializer.Meta):
        fields = TrekDetailSerializer.Meta.fields + ('children',)