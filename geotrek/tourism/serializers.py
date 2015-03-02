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


class CloseTouristicContentSerializer(TranslatedModelSerializer):
    category_id = rest_serializers.Field(source='category.id')

    class Meta:
        model = tourism_models.TouristicContent
        fields = ('id', 'category_id')


class CloseTouristicEventSerializer(TranslatedModelSerializer):
    category_id = rest_serializers.Field(source='category_id')

    class Meta:
        model = tourism_models.TouristicEvent
        fields = ('id', 'category_id')


class TouristicContentTypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    name = rest_serializers.Field(source='label')

    class Meta:
        model = tourism_models.TouristicContentType
        fields = ('id', 'name', 'pictogram', 'in_list')


class TouristicContentCategorySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = tourism_models.TouristicContentCategory
        fields = ('id', 'label', 'type1_label', 'type2_label', 'pictogram')


class TouristicContentSerializer(PicturesSerializerMixin, PublishableSerializerMixin,
                                 ZoningSerializerMixin, TranslatedModelSerializer):
    themes = ThemeSerializer(many=True)
    category = TouristicContentCategorySerializer()
    type1 = TouristicContentTypeSerializer(many=True)
    type2 = TouristicContentTypeSerializer(many=True)

    # Nearby
    touristic_contents = CloseTouristicContentSerializer(many=True, source='published_touristic_contents')
    touristic_events = CloseTouristicEventSerializer(many=True, source='published_touristic_events')
    treks = trekking_serializers.CloseTrekSerializer(many=True, source='published_treks')
    pois = trekking_serializers.ClosePOISerializer(many=True, source='published_pois')

    class Meta:
        model = tourism_models.TouristicContent
        geo_field = 'geom'
        fields = ('id', 'description', 'description_teaser', 'category', 'themes',
                  'contact', 'email', 'website', 'practical_info', 'type1', 'type2',
                  'touristic_contents', 'touristic_events', 'treks', 'pois') + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields


class TouristicEventTypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    name = rest_serializers.Field(source='type')

    class Meta:
        model = tourism_models.TouristicEventType
        fields = ('id', 'name', 'pictogram')


class TouristicEventSerializer(PicturesSerializerMixin, PublishableSerializerMixin,
                               ZoningSerializerMixin, TranslatedModelSerializer):
    themes = ThemeSerializer(many=True)
    type = TouristicEventTypeSerializer()

    # Nearby
    touristic_contents = CloseTouristicContentSerializer(many=True, source='published_touristic_contents')
    touristic_events = CloseTouristicEventSerializer(many=True, source='published_touristic_events')
    treks = trekking_serializers.CloseTrekSerializer(many=True, source='published_treks')
    pois = trekking_serializers.ClosePOISerializer(many=True, source='published_pois')

    # For consistency with touristic contents
    type1 = TouristicEventTypeSerializer(many=True)
    category = rest_serializers.SerializerMethodField('get_category')

    class Meta:
        model = tourism_models.TouristicEvent
        geo_field = 'geom'
        fields = ('id', 'description_teaser', 'description', 'themes',
                  'begin_date', 'end_date', 'duration', 'meeting_point',
                  'meeting_time', 'contact', 'email', 'website',
                  'organizer', 'speaker', 'type', 'accessibility',
                  'participant_number', 'booking', 'target_audience',
                  'practical_info', 'touristic_contents', 'touristic_events',
                  'treks', 'pois', 'type1', 'category') + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields

    def get_category(self, obj):
        return {
            'id': obj.category_id,
            'label': obj._meta.verbose_name,
            'type1_label': obj._meta.get_field('type').verbose_name,
            'pictogram': '/static/tourism/touristicevent.svg',
        }
