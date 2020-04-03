from django.urls import reverse
from django.utils.translation import get_language
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
    geometry = geo_serializers.GeometryField(read_only=True, source="geom2d_transformed", precision=7)
    kml_url = rest_serializers.SerializerMethodField(read_only=True)

    def get_kml_url(self, obj):
        return reverse('sensitivity:sensitivearea_kml_detail', kwargs={'lang': get_language(), 'pk': obj.pk})

    class Meta:
        model = sensitivity_models.SensitiveArea
        geo_field = 'geometry'
        fields = ('id', 'species', 'description', 'contact', 'published', 'publication_date', 'kml_url', 'geometry')
