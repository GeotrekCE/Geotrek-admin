from rest_framework import serializers as rest_serializers
from geotrek.common.serializers import PictogramSerializerMixin, TranslatedModelSerializer
from geotrek.sensitivity import models as sensitivity_models


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


class SensitiveAreaSerializer(TranslatedModelSerializer):
    species = SpeciesSerializer()

    class Meta:
        model = sensitivity_models.SensitiveArea
        geo_field = 'geom'
        fields = ('id', 'species', 'description', 'email', 'published', 'publication_date')
