from rest_framework import serializers as rest_serializers
from rest_framework_gis import serializers as geo_serializers
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
    geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)

    def get_geometry(self, obj):
        return obj.geom2d_transformed

    class Meta:
        model = sensitivity_models.SensitiveArea
        geo_field = 'geometry'
        fields = ('id', 'species', 'description', 'contact', 'published', 'publication_date')
