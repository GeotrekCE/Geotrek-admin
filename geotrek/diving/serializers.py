from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer

from rest_framework import serializers as rest_serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.common.serializers import (ThemeSerializer, PublishableSerializerMixin,
                                        PictogramSerializerMixin, RecordSourceSerializer,
                                        PicturesSerializerMixin, TranslatedModelSerializer,
                                        TargetPortalSerializer)
from geotrek.diving import models as diving_models
from geotrek.trekking import serializers as trekking_serializers


class DifficultySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.ReadOnlyField(source='name')

    class Meta:
        model = diving_models.Difficulty
        fields = ('id', 'pictogram', 'label')


class LevelSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.ReadOnlyField(source='name')

    class Meta:
        model = diving_models.Level
        fields = ('id', 'pictogram', 'label', 'description')


class PracticeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.ReadOnlyField(source='name')

    class Meta:
        model = diving_models.Practice
        fields = ('id', 'pictogram', 'label')


class CloseDiveSerializer(TranslatedModelSerializer):
    category_id = rest_serializers.ReadOnlyField(source='prefixed_category_id')

    class Meta:
        model = diving_models.Dive
        fields = ('id', 'category_id')


class DiveSerializer(DynamicFieldsMixin, rest_serializers.ModelSerializer):
    checkbox = rest_serializers.CharField(source='checkbox_display')
    name = rest_serializers.CharField(source='name_display')
    thumbnail = rest_serializers.CharField(source='thumbnail_display')
    levels = rest_serializers.CharField(source='levels_display')
    structure = rest_serializers.SlugRelatedField('name', read_only=True)
    practice = rest_serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = diving_models.Dive
        fields = "__all__"


class DiveGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = diving_models.Dive
        fields = ['id', 'name', 'published']


class DiveAPISerializer(PicturesSerializerMixin, PublishableSerializerMixin, TranslatedModelSerializer):
    themes = ThemeSerializer(many=True)
    practice = PracticeSerializer()
    difficulty = DifficultySerializer()
    levels = LevelSerializer(many=True)
    source = RecordSourceSerializer(many=True)
    portal = TargetPortalSerializer(many=True)
    category = rest_serializers.SerializerMethodField()
    dives = CloseDiveSerializer(many=True, source='published_dives')
    treks = trekking_serializers.CloseTrekSerializer(many=True, source='published_treks')
    pois = trekking_serializers.ClosePOISerializer(many=True, source='published_pois')

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if 'geotrek.tourism' in settings.INSTALLED_APPS:

            from geotrek.tourism import serializers as tourism_serializers

            self.fields['touristic_contents'] = tourism_serializers.CloseTouristicContentSerializer(many=True,
                                                                                                    source='published_touristic_contents')
            self.fields['touristic_events'] = tourism_serializers.CloseTouristicEventSerializer(many=True,
                                                                                                source='published_touristic_events')

    class Meta:
        model = diving_models.Dive
        fields = (
            'id', 'practice', 'description_teaser', 'description', 'advice',
            'difficulty', 'levels', 'themes', 'owner', 'depth',
            'facilities', 'departure', 'disabled_sport', 'category',
            'source', 'portal', 'eid', 'dives', 'treks', 'pois'
        ) + PublishableSerializerMixin.Meta.fields + PicturesSerializerMixin.Meta.fields

    def get_category(self, obj):
        if settings.SPLIT_DIVES_CATEGORIES_BY_PRACTICE and obj.practice:
            data = {
                'id': obj.prefixed_category_id,
                'label': obj.practice.name,
                'pictogram': obj.practice.get_pictogram_url(),
                'slug': obj.practice.slug,
            }
        else:
            data = {
                'id': obj.prefixed_category_id,
                'label': _("Dive"),
                'pictogram': '/static/diving/dive.svg',
                # Translators: This is a slug (without space, accent or special char)
                'slug': _('dive'),
            }
        if settings.SPLIT_DIVES_CATEGORIES_BY_PRACTICE:
            data['order'] = obj.practice and obj.practice.order
        else:
            data['order'] = settings.DIVE_CATEGORY_ORDER
        return data


class DiveAPIGeojsonSerializer(GeoFeatureModelSerializer, DiveAPISerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(DiveAPISerializer.Meta):
        geo_field = 'api_geom'
        fields = DiveAPISerializer.Meta.fields + ('api_geom', )
