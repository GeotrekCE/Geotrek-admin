from __future__ import unicode_literals

from django.conf import settings
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers

from geotrek.common import models as common_models


class AttachmentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = serializers.CharField(source='attachment_file.url')

    class Meta:
        model = common_models.Attachment
        fields = (
            'url', 'author', 'title', 'legend',
        )


if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from geotrek.trekking import models as trekking_models

    class POIListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        pictures = AttachmentSerializer(many=True, )
        thumbnail = serializers.ReadOnlyField(source='serializable_thumbnail_mobile')
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='geom2d_transformed')

        class Meta:
            model = trekking_models.POI
            fields = (
                'id', 'pictures', 'name', 'description', 'thumbnail', 'type', 'geometry',
            )

    class TrekDetailSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        thumbnail = serializers.ReadOnlyField(source='serializable_thumbnail_mobile')

        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='geom2d_transformed')
        length = serializers.SerializerMethodField(read_only=True)
        pictures = AttachmentSerializer(many=True, )
        cities = serializers.SerializerMethodField(read_only=True)

        def get_cities(self, obj):
            return [city.code for city in obj.cities]

        def get_length(self, obj):
            return round(obj.length_2d_m, 1)

        def get_geometry(self, obj):
            return obj.geom2d_transformed

        class Meta:
            model = trekking_models.Trek
            fields = (
                'id', 'thumbnail', 'name', 'accessibilities', 'description_teaser', 'cities',
                'description', 'departure', 'arrival', 'duration', 'access', 'advised_parking', 'advice',
                'difficulty', 'length', 'ascent', 'descent', 'route', 'is_park_centered',
                'min_elevation', 'max_elevation', 'themes', 'networks', 'practice', 'difficulty',
                'geometry', 'pictures', 'information_desks', 'cities',
            )
            auto_bbox = True

    class TrekListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        thumbnail = serializers.ReadOnlyField(source='serializable_thumbnail_mobile')
        length = serializers.SerializerMethodField(read_only=True)
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='start_point', )
        cities = serializers.SerializerMethodField(read_only=True)

        def get_cities(self, obj):
            return [city.code for city in obj.cities]

        def get_length(self, obj):
            return round(obj.length_2d_m, 1)

        class Meta:
            model = trekking_models.Trek
            fields = (
                'id', 'thumbnail', 'name', 'departure', 'accessibilities', 'route',
                'difficulty', 'practice', 'themes', 'length', 'geometry', 'cities', 'duration'
            )
