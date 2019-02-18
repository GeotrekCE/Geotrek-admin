from __future__ import unicode_literals

from django.conf import settings
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers

from geotrek.common import models as common_models
from geotrek.trekking import models as trekking_models


if 'geotrek.zoning' in settings.INSTALLED_APPS:
    from geotrek.zoning import models as zoning_models

    class CitySerializer(serializers.ModelSerializer):
        lat = serializers.SerializerMethodField(read_only=True)
        lng = serializers.SerializerMethodField(read_only=True)

        def get_lat(self, obj):
            return obj.geom.centroid.y

        def get_lng(self, obj):
            return obj.geom.centroid.x

        class Meta:
            model = zoning_models.City
            fields = ('name', 'code', 'lat', 'lng')

if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.tourism import models as tourism_models

    class InformationDeskTypeSerializer(serializers.ModelSerializer):
        class Meta:
            model = tourism_models.InformationDeskType
            fields = ('id', 'label', 'pictogram')

    class InformationDeskSerializer(serializers.ModelSerializer):
        type = InformationDeskTypeSerializer(read_only=True)

        class Meta:
            model = tourism_models.InformationDesk
            fields = ('id', 'description', 'email', 'latitude', 'longitude', 'municipality',
                      'name', 'phone', 'photo_url', 'postal_code', 'street', 'type',
                      'website')


if 'geotrek.trekking' in settings.INSTALLED_APPS:
    class DifficultySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        label = serializers.ReadOnlyField(source='difficulty')

        class Meta:
            model = trekking_models.DifficultyLevel
            fields = ('id', 'label', 'pictogram')

    class PracticeSerializer(serializers.ModelSerializer):
        label = serializers.ReadOnlyField(source='name')

        class Meta:
            model = trekking_models.Practice
            fields = ('id', 'label', 'pictogram',)

    class AccessibilitySerializer(serializers.ModelSerializer):
        class Meta:
            model = trekking_models.Accessibility
            fields = ('id', 'label', 'pictogram',)

    class RouteSerializer(serializers.ModelSerializer):
        label = serializers.ReadOnlyField(source='route')

        class Meta:
            model = trekking_models.Route
            fields = ('id', 'label', 'pictogram',)

    class ThemeSerializer(serializers.ModelSerializer):

        class Meta:
            model = common_models.Theme
            fields = ('id', 'label', 'pictogram')

    class NetworkSerializer(serializers.ModelSerializer):
        label = serializers.ReadOnlyField(source='network')

        class Meta:
            model = trekking_models.TrekNetwork
            fields = ('id', 'label', 'pictogram')
