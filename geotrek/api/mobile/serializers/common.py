import os

from django.conf import settings
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers

from geotrek.common import models as common_models
from geotrek.trekking import models as trekking_models
from geotrek.sensitivity import models as sensitivity_models


if 'geotrek.zoning' in settings.INSTALLED_APPS:
    from geotrek.zoning import models as zoning_models

    class DistrictSerializer(serializers.ModelSerializer):
        class Meta:
            model = zoning_models.District
            fields = ('id', 'name')

    class CitySerializer(serializers.ModelSerializer):
        id = serializers.ReadOnlyField(source='code')

        class Meta:
            model = zoning_models.City
            fields = ('id', 'name')

if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.tourism import models as tourism_models

    class InformationDeskTypeSerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='label')
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = tourism_models.InformationDeskType
            fields = ('id', 'name', 'pictogram')

    class TouristicContentTypeSerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='label')
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = tourism_models.TouristicContentType
            fields = ('id', 'name', 'pictogram')

    class TouristicEventTypeSerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='type')
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = tourism_models.TouristicEventType
            fields = ('id', 'name', 'pictogram')

    class TouristicContentCategorySerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='label')
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = tourism_models.TouristicContentCategory
            fields = ('id', 'name', 'pictogram', 'type1_label', 'type2_label', 'color')


if 'geotrek.trekking' in settings.INSTALLED_APPS:
    class DifficultySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='difficulty')
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = trekking_models.DifficultyLevel
            fields = ('id', 'name', 'pictogram')

    class PracticeSerializer(serializers.ModelSerializer):
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = trekking_models.Practice
            fields = ('id', 'name', 'slug', 'pictogram', 'color')

    class AccessibilitySerializer(serializers.ModelSerializer):
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = trekking_models.Accessibility
            fields = ('id', 'name', 'pictogram',)

    class RouteSerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='route')
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = trekking_models.Route
            fields = ('id', 'name', 'pictogram',)

    class ThemeSerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='label')
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = common_models.Theme
            fields = ('id', 'name', 'pictogram')

    class NetworkSerializer(serializers.ModelSerializer):
        name = serializers.ReadOnlyField(source='network')
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = trekking_models.TrekNetwork
            fields = ('id', 'name', 'pictogram')

    class POITypeSerializer(serializers.ModelSerializer):
        pictogram = serializers.SerializerMethodField()

        def get_pictogram(self, obj):
            if not obj.pictogram:
                return None
            file_name, file_extension = os.path.splitext(str(obj.pictogram.url))
            return '{file}.png'.format(file=file_name) if file_extension == '.svg' else obj.pictogram.url

        class Meta:
            model = trekking_models.POIType
            fields = ('id', 'label', 'pictogram')

if 'geotrek.sensitivity' in settings.INSTALLED_APPS:

    class SportPracticeSerializer(serializers.ModelSerializer):

        class Meta:
            model = sensitivity_models.SportPractice
            fields = ('id', 'name')


class MobileMenuItemListSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    title = serializers.CharField()


class MobileMenuItemDetailSerializer(MobileMenuItemListSerializer):

    external_url = serializers.CharField(source="link_url")
    content = serializers.SerializerMethodField()

    def get_content(self, obj):
        if obj.page:
            return obj.page.content
        else:
            return ""
