from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers as rest_serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from django.conf import settings
from django.utils.translation import gettext as _

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import (ThemeSerializer, PublishableSerializerMixin,
                                        PictogramSerializerMixin, RecordSourceSerializer,
                                        PicturesSerializerMixin, TranslatedModelSerializer,
                                        TargetPortalSerializer)
from geotrek.zoning.serializers import ZoningSerializerMixin
from geotrek.trekking import serializers as trekking_serializers
from geotrek.tourism import models as tourism_models


class LabelAccessibilitySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = tourism_models.LabelAccessibility
        fields = ('id', 'pictogram', 'label')


class InformationDeskTypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = tourism_models.InformationDeskType
        fields = ('id', 'pictogram', 'label')


class InformationDeskSerializer(TranslatedModelSerializer):
    type = InformationDeskTypeSerializer()
    label_accessibility = LabelAccessibilitySerializer()

    class Meta:
        model = tourism_models.InformationDesk
        geo_field = 'geom'
        fields = ('name', 'description', 'accessibility', 'label_accessibility', 'phone', 'email', 'website',
                  'photo_url', 'street', 'postal_code', 'municipality',
                  'latitude', 'longitude', 'type')


class InformationDeskGeojsonSerializer(GeoFeatureModelSerializer, InformationDeskSerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(InformationDeskSerializer.Meta):
        geo_field = 'api_geom'
        fields = InformationDeskSerializer.Meta.fields + ('api_geom', )


class CloseTouristicContentSerializer(TranslatedModelSerializer):
    category_id = rest_serializers.ReadOnlyField(source='prefixed_category_id')

    class Meta:
        model = tourism_models.TouristicContent
        fields = ('id', 'category_id')


class CloseTouristicEventSerializer(TranslatedModelSerializer):
    category_id = rest_serializers.ReadOnlyField(source='prefixed_category_id')

    class Meta:
        model = tourism_models.TouristicEvent
        fields = ('id', 'category_id')


class TouristicContentTypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    name = rest_serializers.ReadOnlyField(source='label')

    class Meta:
        model = tourism_models.TouristicContentType
        fields = ('id', 'name', 'pictogram', 'in_list')


class TouristicContentCategorySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    id = rest_serializers.ReadOnlyField(source='prefixed_id')
    slug = rest_serializers.SerializerMethodField()

    class Meta:
        model = tourism_models.TouristicContentCategory
        fields = ('id', 'label', 'type1_label', 'type2_label', 'pictogram', 'order', 'slug')

    def get_slug(self, obj):
        return _('touristic-content')


class TouristicContentSerializer(DynamicFieldsMixin, rest_serializers.ModelSerializer):
    name = rest_serializers.CharField(source='name_display')
    structure = rest_serializers.SlugRelatedField('name', read_only=True)
    themes = rest_serializers.CharField(source='themes_display')
    category = rest_serializers.SlugRelatedField('label', read_only=True)
    label_accessibility = rest_serializers.SlugRelatedField('label', read_only=True)
    reservation_system = rest_serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = tourism_models.TouristicContent
        fields = "__all__"


class TouristicContentRandoV2GeojsonSerializer(PicturesSerializerMixin, PublishableSerializerMixin,
                                               ZoningSerializerMixin, TranslatedModelSerializer,
                                               GeoFeatureModelSerializer):
    themes = ThemeSerializer(many=True)
    category = TouristicContentCategorySerializer()
    label_accessibility = LabelAccessibilitySerializer()
    type1 = TouristicContentTypeSerializer(many=True)
    type2 = TouristicContentTypeSerializer(many=True)
    source = RecordSourceSerializer(many=True)
    portal = TargetPortalSerializer(many=True)
    reservation_system = rest_serializers.ReadOnlyField(source='reservation_system.name', default="")
    structure = StructureSerializer()

    # Nearby
    touristic_contents = CloseTouristicContentSerializer(many=True, source='published_touristic_contents')
    touristic_events = CloseTouristicEventSerializer(many=True, source='published_touristic_events')
    treks = trekking_serializers.CloseTrekSerializer(many=True, source='published_treks')
    pois = trekking_serializers.ClosePOISerializer(many=True, source='published_pois')
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if 'geotrek.diving' in settings.INSTALLED_APPS:

            from geotrek.diving.serializers import CloseDiveSerializer

            self.fields['dives'] = CloseDiveSerializer(many=True, source='published_dives')

    class Meta:
        model = tourism_models.TouristicContent
        geo_field = 'api_geom'
        fields = (
            'id', 'description', 'description_teaser', 'category',
            'themes', 'contact', 'email', 'website', 'practical_info', 'accessibility', 'label_accessibility',
            'type1', 'type2', 'touristic_contents', 'touristic_events',
            'treks', 'pois', 'source', 'portal', 'approved',
            'reservation_id', 'reservation_system', 'structure', 'api_geom'
        ) + ZoningSerializerMixin.Meta.fields + PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields


class TouristicEventTypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    name = rest_serializers.ReadOnlyField(source='type')

    class Meta:
        model = tourism_models.TouristicEventType
        fields = ('id', 'name', 'pictogram')


class TouristicEventSerializer(DynamicFieldsMixin, rest_serializers.ModelSerializer):
    name = rest_serializers.CharField(source='name_display')
    type = rest_serializers.SlugRelatedField('type', read_only=True)
    structure = rest_serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = tourism_models.TouristicEvent
        fields = "__all__"


class TouristicEventGeojsonSerializer(GeoFeatureModelSerializer):
    themes = ThemeSerializer(many=True)
    type = TouristicEventTypeSerializer()
    source = RecordSourceSerializer(many=True)
    portal = TargetPortalSerializer(many=True)
    structure = StructureSerializer()

    # Nearby
    touristic_contents = CloseTouristicContentSerializer(many=True, source='published_touristic_contents')
    touristic_events = CloseTouristicEventSerializer(many=True, source='published_touristic_events')
    treks = trekking_serializers.CloseTrekSerializer(many=True, source='published_treks')
    pois = trekking_serializers.ClosePOISerializer(many=True, source='published_pois')

    # For consistency with touristic contents
    type1 = TouristicEventTypeSerializer(many=True)
    category = rest_serializers.SerializerMethodField()
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if 'geotrek.diving' in settings.INSTALLED_APPS:
            from geotrek.diving.serializers import CloseDiveSerializer

            self.fields['dives'] = CloseDiveSerializer(many=True, source='published_dives')

    def get_category(self, obj):
        return {
            'id': obj.prefixed_category_id,
            'order': settings.TOURISTIC_EVENT_CATEGORY_ORDER,
            'label': obj._meta.verbose_name_plural,
            'type1_label': obj._meta.get_field('type').verbose_name,
            'pictogram': '/static/tourism/touristicevent.svg',
            'slug': _('touristic-event'),
        }

    class Meta:
        model = tourism_models.TouristicEvent
        geo_field = 'api_geom'
        fields = (
            'id', 'description_teaser', 'description', 'themes',
            'begin_date', 'end_date', 'duration', 'meeting_point',
            'meeting_time', 'contact', 'email', 'website', 'structure',
            'organizer', 'speaker', 'type', 'accessibility',
            'participant_number', 'booking', 'target_audience',
            'practical_info', 'touristic_contents', 'touristic_events',
            'treks', 'pois', 'type1', 'category', 'source', 'portal', 'approved', 'api_geom'
        ) + ZoningSerializerMixin.Meta.fields + PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields
