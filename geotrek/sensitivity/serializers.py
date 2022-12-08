from django.urls import reverse
from django.utils.translation import get_language
from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers as rest_serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.common.serializers import PictogramSerializerMixin, TranslatedModelSerializer
from . import models as sensitivity_models


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


class SensitiveAreaAPISerializer(TranslatedModelSerializer):
    species = SpeciesSerializer()
    kml_url = rest_serializers.SerializerMethodField()
    public_url = rest_serializers.SerializerMethodField()

    def get_kml_url(self, obj):
        return reverse('sensitivity:sensitivearea_kml_detail', kwargs={'lang': get_language(), 'pk': obj.pk})


    def get_public_url(self, obj):
        return reverse('sensitivity:sensitivearea_public_detail', kwargs={'pk': obj.pk})

    class Meta:
        model = sensitivity_models.SensitiveArea
        fields = ('id', 'species', 'description', 'contact', 'published', 'publication_date', 'kml_url', 'public_url')


class SensitiveAreaAPIGeojsonSerializer(GeoFeatureModelSerializer, SensitiveAreaAPISerializer):
    # Annotated geom field with API_SRID
    geom2d_transformed = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(SensitiveAreaAPISerializer.Meta):
        geo_field = 'geom2d_transformed'
        fields = SensitiveAreaAPISerializer.Meta.fields + ('geom2d_transformed', )
