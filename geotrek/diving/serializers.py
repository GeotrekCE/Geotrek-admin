from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer

from rest_framework import serializers as rest_serializers

from geotrek.common.serializers import PictogramSerializerMixin, TranslatedModelSerializer
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


class CloseDiveSerializer(TranslatedModelSerializer):
    category_id = rest_serializers.ReadOnlyField(source='prefixed_category_id')

    class Meta:
        model = diving_models.Dive
        fields = ('id', 'category_id')


class DiveSerializer(DynamicFieldsMixin, rest_serializers.ModelSerializer):
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
