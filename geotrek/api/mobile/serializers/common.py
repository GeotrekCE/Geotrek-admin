from __future__ import unicode_literals

from django.conf import settings
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers

from geotrek.common import models as common_models
from geotrek.flatpages import models as flatpage_models
from geotrek.trekking import models as trekking_models


class BaseGeoJSONSerializer(geo_serializers.GeoFeatureModelSerializer):
    """
    Mixin used to serialize geojson
    """

    class Meta:
        geo_field = 'geometry'


def override_serializer(format_output, base_serializer_class):
    """
    Override Serializer switch output format and dimension data
    """
    if format_output == 'geojson':
        class GeneratedGeoSerializer(BaseGeoJSONSerializer,
                                     base_serializer_class):
            class Meta(BaseGeoJSONSerializer.Meta,
                       base_serializer_class.Meta):
                pass

        final_class = GeneratedGeoSerializer
    else:
        final_class = base_serializer_class
    return final_class


if 'geotrek.zoning' in settings.INSTALLED_APPS:
    from geotrek.zoning import models as zoning_models

    class CitySerializer(serializers.ModelSerializer):
        id = serializers.ReadOnlyField(source='code')

        class Meta:
            model = zoning_models.City
            fields = ('id', 'name')

if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.tourism import models as tourism_models

    class InformationDeskTypeSerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='label')
        pictogram = serializers.ReadOnlyField(source='pictogram.url')

        class Meta:
            model = tourism_models.InformationDeskType
            fields = ('id', 'name', 'pictogram')

    class InformationDeskSerializer(serializers.ModelSerializer):
        type = InformationDeskTypeSerializer(read_only=True)

        class Meta:
            model = tourism_models.InformationDesk
            fields = ('id', 'description', 'email', 'latitude', 'longitude', 'municipality',
                      'name', 'phone', 'photo_url', 'postal_code', 'street', 'type',
                      'website')


if 'geotrek.trekking' in settings.INSTALLED_APPS:
    class DifficultySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='difficulty')
        pictogram = serializers.ReadOnlyField(source='pictogram.url')

        class Meta:
            model = trekking_models.DifficultyLevel
            fields = ('id', 'name', 'pictogram')

    class PracticeSerializer(serializers.ModelSerializer):
        pictogram = serializers.ReadOnlyField(source='pictogram.url')

        class Meta:
            model = trekking_models.Practice
            fields = ('id', 'name', 'pictogram',)

    class AccessibilitySerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='label')
        pictogram = serializers.ReadOnlyField(source='pictogram.url')

        class Meta:
            model = trekking_models.Accessibility
            fields = ('id', 'name', 'pictogram',)

    class RouteSerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='route')
        pictogram = serializers.ReadOnlyField(source='pictogram.url')

        class Meta:
            model = trekking_models.Route
            fields = ('id', 'name', 'pictogram',)

    class ThemeSerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='label')
        pictogram = serializers.ReadOnlyField(source='pictogram.url')

        class Meta:
            model = common_models.Theme
            fields = ('id', 'name', 'pictogram')

    class NetworkSerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='network')
        pictogram = serializers.ReadOnlyField(source='pictogram.url')

        class Meta:
            model = trekking_models.TrekNetwork
            fields = ('id', 'name', 'pictogram')


class FlatPageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = flatpage_models.FlatPage
        fields = ('id', 'title')


class FlatPageDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = flatpage_models.FlatPage
        fields = ('id', 'title', 'content')
