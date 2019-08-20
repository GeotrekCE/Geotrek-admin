from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers as rest_serializers

from geotrek.common.serializers import (ThemeSerializer, PublishableSerializerMixin,
                                        PictogramSerializerMixin, RecordSourceSerializer,
                                        PicturesSerializerMixin, TranslatedModelSerializer,
                                        TargetPortalSerializer)
from geotrek.diving import models as diving_models


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


class DiveSerializer(PicturesSerializerMixin, PublishableSerializerMixin,
                     TranslatedModelSerializer):
    themes = ThemeSerializer(many=True)
    practice = PracticeSerializer()
    difficulty = DifficultySerializer()
    levels = LevelSerializer(many=True)
    source = RecordSourceSerializer(many=True)
    portal = TargetPortalSerializer(many=True)
    category = rest_serializers.SerializerMethodField()

    class Meta:
        model = diving_models.Dive
        geo_field = 'geom'
        fields = (
            'id', 'practice', 'description_teaser', 'description', 'advice',
            'difficulty', 'levels', 'themes', 'owner', 'depth',
            'facilities', 'departure', 'disabled_sport', 'category',
            'source', 'portal', 'eid',
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
                'id': obj.category_id_prefix,
                'label': _(u"Dive"),
                'pictogram': '/static/diving/dive.svg',
                # Translators: This is a slug (without space, accent or special char)
                'slug': _('dive'),
            }
        if settings.SPLIT_DIVES_CATEGORIES_BY_PRACTICE:
            data['order'] = obj.practice and obj.practice.order
        else:
            data['order'] = settings.DIVE_CATEGORY_ORDER
        return data
