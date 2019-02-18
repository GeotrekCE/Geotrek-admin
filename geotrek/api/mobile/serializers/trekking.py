from __future__ import unicode_literals

from django.conf import settings
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers

from geotrek.common import models as common_models


class AttachmentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = serializers.FileField(source='attachment_file')

    class Meta:
        model = common_models.Attachment
        fields = (
            'url', 'author', 'title', 'legend',
        )


if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from geotrek.trekking import models as trekking_models

    class TrekListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        thumbnail = serializers.ReadOnlyField(source='serializable_thumbnail_mobile')

        geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)
        length = serializers.SerializerMethodField(read_only=True)
        pictures = AttachmentSerializer(many=True, )

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
                'geometry', 'pictures', 'information_desks'
            )

    class MinimalTrekListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        thumbnail = serializers.ReadOnlyField(source='serializable_thumbnail_mobile')
        length = serializers.ReadOnlyField(read_only=True)
        geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)

        def get_length(self, obj):
            return round(obj.length_2d_m, 1)

        def get_geometry(self, obj):
            return obj.geom2d_transformed

        class Meta:
            model = trekking_models.Trek
            fields = (
                'id', 'thumbnail', 'name', 'departure', 'accessibilities',
                'difficulty', 'practice', 'themes', 'length', 'geometry'
            )

    class POIListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        pictures = AttachmentSerializer(many=True, )
        thumbnail = serializers.ReadOnlyField(source='serializable_thumbnail_mobile')
        geometry = geo_serializers.GeometrySerializerMethodField(read_only=True)

        def get_geometry(self, obj):
            return obj.geom2d_transformed

        class Meta:
            model = trekking_models.POI
            fields = (
                'id', 'pictures', 'name', 'description', 'thumbnail', 'type',
                'geometry',
            )
