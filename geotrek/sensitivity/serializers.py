from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers as rest_serializers

from geotrek.common.serializers import PictogramSerializerMixin, TranslatedModelSerializer
from . import models as sensitivity_models


class RuleSerializer(PictogramSerializerMixin, rest_serializers.ModelSerializer):
    class Meta:
        model = sensitivity_models.Rule
        fields = ('id', 'code', 'name', 'pictogram', 'description', 'url')


class SportPracticeSerializer(TranslatedModelSerializer):
    class Meta:
        model = sensitivity_models.SportPractice
        fields = ('id', 'name')


class SpeciesSerializer(TranslatedModelSerializer, PictogramSerializerMixin):
    practices = SportPracticeSerializer(many=True)
    period = rest_serializers.SerializerMethodField()

    def get_period(self, obj):
        return [getattr(obj, 'period{:02}'.format(p)) for p in range(1, 13)]

    class Meta:
        model = sensitivity_models.Species
        fields = ['id', 'name', 'practices', 'url', 'pictogram', 'period']


class SensitiveAreaSerializer(DynamicFieldsMixin, rest_serializers.ModelSerializer):
    category = rest_serializers.CharField(source='category_display')
    structure = rest_serializers.SlugRelatedField('name', read_only=True)
    species = rest_serializers.CharField(source='species_display')

    class Meta:
        model = sensitivity_models.SensitiveArea
        fields = "__all__"


class SensitiveAreaGeojsonSerializer(MapentityGeojsonModelSerializer):
    radius = rest_serializers.IntegerField()

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = sensitivity_models.SensitiveArea
        fields = ['id', 'species', 'radius', 'published']
