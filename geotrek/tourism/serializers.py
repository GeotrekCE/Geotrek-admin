from rest_framework import serializers as rest_serializers

from geotrek.common.serializers import (ThemeSerializer, PublishableSerializerMixin, PictogramSerializerMixin,
                                        PicturesSerializerMixin, TranslatedModelSerializer)
from geotrek.zoning.serializers import ZoningSerializerMixin
from geotrek.trekking import serializers as trekking_serializers
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


class RelatedTouristicContentSerializer(TranslatedModelSerializer):
    slug = rest_serializers.Field(source='slug')

    class Meta:
        model = tourism_models.TouristicContent
        fields = ('id', 'name', 'slug')


class RelatedTouristicEventSerializer(TranslatedModelSerializer):
    slug = rest_serializers.Field(source='slug')

    class Meta:
        model = tourism_models.TouristicEvent
        fields = ('id', 'name', 'slug')


class TouristicContentTypeSerializer(TranslatedModelSerializer):
    name = rest_serializers.Field(source='label')

    class Meta:
        model = tourism_models.TouristicContentType
        fields = ('id', 'name', 'in_list')


class TouristicContentCategorySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    types = TouristicContentTypeSerializer(many=True)

    class Meta:
        model = tourism_models.TouristicContentCategory
        fields = ('id', 'types', 'label', 'type1_label', 'type2_label', 'pictogram')


class TouristicContentSerializer(PicturesSerializerMixin, PublishableSerializerMixin,
                                 ZoningSerializerMixin, TranslatedModelSerializer):
    themes = ThemeSerializer(many=True)
    category = TouristicContentCategorySerializer()
    type1 = TouristicContentTypeSerializer(many=True)
    type2 = TouristicContentTypeSerializer(many=True)

    touristic_contents = RelatedTouristicContentSerializer(many=True)
    touristic_events = RelatedTouristicEventSerializer(many=True)

    treks = trekking_serializers.RelatedTrekSerializer(many=True)
    pois = trekking_serializers.RelatedPOISerializer(many=True)

    class Meta:
        model = tourism_models.TouristicContent
        fields = ('id', 'description', 'description_teaser', 'category', 'themes',
                  'contact', 'email', 'website', 'practical_info', 'type1', 'type2',
                  'touristic_contents', 'touristic_events', 'treks', 'pois') + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields


class TouristicEventTypeSerializer(TranslatedModelSerializer):
    name = rest_serializers.Field(source='type')

    class Meta:
        model = tourism_models.TouristicEventType
        fields = ('id', 'name')


class TouristicEventPublicSerializer(TranslatedModelSerializer):
    name = rest_serializers.Field(source='public')

    class Meta:
        model = tourism_models.TouristicEventPublic
        fields = ('id', 'name')


class TouristicEventSerializer(PicturesSerializerMixin, PublishableSerializerMixin,
                               ZoningSerializerMixin, TranslatedModelSerializer):
    themes = ThemeSerializer(many=True)
    type = TouristicEventTypeSerializer()
    public = TouristicEventPublicSerializer()

    touristic_contents = RelatedTouristicContentSerializer(many=True)
    touristic_events = RelatedTouristicEventSerializer(many=True)

    treks = trekking_serializers.RelatedTrekSerializer(many=True)
    pois = trekking_serializers.RelatedPOISerializer(many=True)

    class Meta:
        model = tourism_models.TouristicEvent
        fields = ('id', 'description_teaser', 'description', 'themes',
                  'begin_date', 'end_date', 'duration', 'meeting_point',
                  'meeting_time', 'contact', 'email', 'website',
                  'organizer', 'speaker', 'type', 'accessibility',
                  'participant_number', 'booking', 'public', 'practical_info',
                  'touristic_contents', 'touristic_events', 'treks', 'pois') + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields
