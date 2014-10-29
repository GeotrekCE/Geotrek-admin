from rest_framework import serializers as rest_serializers

from geotrek.common.serializers import (ThemeSerializer, PublishableSerializerMixin, PictogramSerializerMixin,
                                        PicturesSerializerMixin, TranslatedModelSerializer)
from geotrek.zoning.serializers import ZoningSerializerMixin
from geotrek.tourism import models as tourism_models


class InformationDeskTypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = tourism_models.InformationDeskType
        fields = ('id', 'pictogram', 'label')


class InformationDeskSerializer(TranslatedModelSerializer):
    type = InformationDeskTypeSerializer()
    photo_url = rest_serializers.Field(source='photo_url')
    latitude = rest_serializers.Field(source='latitude')
    longitude = rest_serializers.Field(source='longitude')

    class Meta:
        model = tourism_models.InformationDesk
        fields = ('name', 'description', 'phone', 'email', 'website',
                  'photo_url', 'street', 'postal_code', 'municipality',
                  'latitude', 'longitude', 'type')


class TouristicContentSerializer(PicturesSerializerMixin, PublishableSerializerMixin,
                                 ZoningSerializerMixin, TranslatedModelSerializer):
    themes = ThemeSerializer(many=True)

    class Meta:
        model = tourism_models.TouristicContent
        fields = ('id', 'description', 'description_teaser', 'category', 'themes',
            'contact', 'email', 'website', 'practical_info', 'type1', 'type2') + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields


class TouristicEventSerializer(PicturesSerializerMixin, PublishableSerializerMixin,
                               ZoningSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = tourism_models.TouristicEvent
        fields = ('id', ) + PublishableSerializerMixin.Meta.fields
