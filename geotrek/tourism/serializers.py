from rest_framework import serializers as rest_serializers

from geotrek.common.serializers import TranslatedModelSerializer
from geotrek.tourism import models as tourism_models


class InformationDeskSerializer(TranslatedModelSerializer):
    photo_url = rest_serializers.Field(source='photo_url')
    latitude = rest_serializers.Field(source='latitude')
    longitude = rest_serializers.Field(source='longitude')

    class Meta:
        model = tourism_models.InformationDesk
        fields = ('name', 'description', 'phone', 'email', 'website',
                  'photo_url', 'street', 'postal_code', 'municipality',
                  'latitude', 'longitude')
