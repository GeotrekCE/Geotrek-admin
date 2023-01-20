import copy
import json

import gpxpy.gpx
from django.conf import settings
from django.urls import reverse
from django.utils.translation import get_language, gettext_lazy as _
from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import GPXSerializer, MapentityGeojsonModelSerializer
from rest_framework import serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.altimetry.serializers import AltimetrySerializerMixin
from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import (
    PictogramSerializerMixin, ThemeSerializer,
    TranslatedModelSerializer, PicturesSerializerMixin,
    PublishableSerializerMixin, RecordSourceSerializer,
    TargetPortalSerializer, LabelSerializer,
)
from geotrek.zoning.serializers import ZoningAPISerializerMixin
from . import models as trekking_models


class TrekGPXSerializer(GPXSerializer):
    def end_object(self, trek):
        super().end_object(trek)
        for poi in trek.published_pois.all():
            geom_3d = poi.geom_3d.transform(4326, clone=True)  # GPX uses WGS84
            wpt = gpxpy.gpx.GPXWaypoint(latitude=geom_3d.y,
                                        longitude=geom_3d.x,
                                        elevation=geom_3d.z)
            wpt.name = "%s: %s" % (poi.type, poi.name)
            wpt.description = poi.description
            self.gpx.waypoints.append(wpt)


class DifficultyLevelSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = serializers.ReadOnlyField(source='difficulty')

    class Meta:
        model = trekking_models.DifficultyLevel
        fields = ('id', 'pictogram', 'label')


class RouteSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = serializers.ReadOnlyField(source='route')

    class Meta:
        model = trekking_models.Route
        fields = ('id', 'pictogram', 'label')


class NetworkSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    name = serializers.ReadOnlyField(source='network')

    class Meta:
        model = trekking_models.Route
        fields = ('id', 'pictogram', 'name')


class PracticeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = serializers.ReadOnlyField(source='name')

    class Meta:
        model = trekking_models.Practice
        fields = ('id', 'pictogram', 'label')


class AccessibilitySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = serializers.ReadOnlyField(source='name')

    class Meta:
        model = trekking_models.Accessibility
        fields = ('id', 'pictogram', 'label')


class AccessibilityLevelSerializer(TranslatedModelSerializer):
    label = serializers.ReadOnlyField(source='name')

    class Meta:
        model = trekking_models.AccessibilityLevel
        fields = ('id', 'label')


class TypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.Practice
        fields = ('id', 'pictogram', 'name')


class WebLinkCategorySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.WebLinkCategory
        fields = ('id', 'pictogram', 'label')


class WebLinkSerializer(TranslatedModelSerializer):
    category = WebLinkCategorySerializer()

    class Meta:
        model = trekking_models.WebLink
        fields = ('id', 'name', 'category', 'url')


class CloseTrekSerializer(TranslatedModelSerializer):
    category_id = serializers.ReadOnlyField(source='prefixed_category_id')

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'category_id')


class RelatedTrekSerializer(TranslatedModelSerializer):
    pk = serializers.ReadOnlyField(source='id')
    category_slug = serializers.SerializerMethodField()

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'pk', 'slug', 'name', 'category_slug')

    def get_category_slug(self, obj):
        if settings.SPLIT_TREKS_CATEGORIES_BY_ITINERANCY and obj.children.exists():
            # Translators: This is a slug (without space, accent or special char)
            return _('itinerancy')
        if settings.SPLIT_TREKS_CATEGORIES_BY_PRACTICE and obj.practice:
            return obj.practice.slug
        else:
            # Translators: This is a slug (without space, accent or special char)
            return _('trek')


class TrekRelationshipSerializer(serializers.ModelSerializer):
    published = serializers.ReadOnlyField(source='trek_b.published')
    trek = RelatedTrekSerializer(source='trek_b')

    class Meta:
        model = trekking_models.TrekRelationship
        fields = ('has_common_departure', 'has_common_edge', 'is_circuit_step',
                  'trek', 'published')


class TrekSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    length_2d = serializers.ReadOnlyField()
    name = serializers.CharField(source='name_display')
    difficulty = serializers.SlugRelatedField('difficulty', read_only=True)
    practice = serializers.SlugRelatedField('name', read_only=True)
    themes = serializers.CharField(source='themes_display')
    thumbnail = serializers.CharField(source='thumbnail_display')
    structure = serializers.SlugRelatedField('name', read_only=True)
    reservation_system = serializers.SlugRelatedField('name', read_only=True)
    accessibilities = serializers.CharField(source='accessibilities_display')
    portal = serializers.CharField(source='portal_display')
    source = serializers.CharField(source='source_display')

    class Meta:
        model = trekking_models.Trek
        fields = "__all__"


class TrekGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = trekking_models.Trek
        fields = ('id', 'name', 'published')


class TrekAPISerializer(PublishableSerializerMixin, PicturesSerializerMixin, AltimetrySerializerMixin,
                        ZoningAPISerializerMixin, TranslatedModelSerializer):
    difficulty = DifficultyLevelSerializer()
    route = RouteSerializer()
    networks = NetworkSerializer(many=True)
    themes = ThemeSerializer(many=True)
    practice = PracticeSerializer()
    usages = PracticeSerializer(many=True)  # Rando v1 compat
    accessibilities = AccessibilitySerializer(many=True)
    accessibility_level = AccessibilityLevelSerializer()
    web_links = WebLinkSerializer(many=True)
    labels = LabelSerializer(many=True)
    relationships = TrekRelationshipSerializer(many=True, source='published_relationships')
    treks = CloseTrekSerializer(many=True, source='published_treks')
    source = RecordSourceSerializer(many=True)
    portal = TargetPortalSerializer(many=True)
    children = serializers.ReadOnlyField(source='children_id')
    parents = serializers.ReadOnlyField(source='parents_id')
    previous = serializers.ReadOnlyField(source='previous_id')
    next = serializers.ReadOnlyField(source='next_id')
    reservation_system = serializers.ReadOnlyField(source='reservation_system.name', default="")

    # Idea: use rest-framework-gis
    parking_location = serializers.SerializerMethodField()
    points_reference = serializers.SerializerMethodField()

    gpx = serializers.SerializerMethodField('get_gpx_url')
    kml = serializers.SerializerMethodField('get_kml_url')
    structure = StructureSerializer()

    # For consistency with touristic contents
    type2 = TypeSerializer(source='accessibilities', many=True)
    category = serializers.SerializerMethodField()

    # Method called to retrieve relevant pictures based on settings
    pictures = serializers.SerializerMethodField()

    length = serializers.ReadOnlyField(source='length_2d')

    def __init__(self, instance=None, *args, **kwargs):
        # duplicate each trek for each one of its accessibilities
        if instance and hasattr(instance, '__iter__') and settings.SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY:
            treks = []
            for trek in instance:
                treks.append(trek)
                for accessibility in trek.accessibilities.all():
                    clone = copy.copy(trek)
                    clone.accessibility = accessibility
                    treks.append(clone)
            instance = treks

        super().__init__(instance, *args, **kwargs)

        if settings.SPLIT_TREKS_CATEGORIES_BY_PRACTICE:
            del self.fields['practice']
        if settings.SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY:
            del self.fields['type2']

        if 'geotrek.tourism' in settings.INSTALLED_APPS:

            from geotrek.tourism import serializers as tourism_serializers

            self.fields['information_desks'] = tourism_serializers.InformationDeskSerializer(many=True)
            self.fields['touristic_contents'] = tourism_serializers.CloseTouristicContentSerializer(many=True, source='published_touristic_contents')
            self.fields['touristic_events'] = tourism_serializers.CloseTouristicEventSerializer(many=True, source='published_touristic_events')

        if 'geotrek.diving' in settings.INSTALLED_APPS:

            from geotrek.diving.serializers import CloseDiveSerializer

            self.fields['dives'] = CloseDiveSerializer(many=True, source='published_dives')

    class Meta:
        model = trekking_models.Trek
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = (
            'id', 'departure', 'arrival', 'duration', 'duration_pretty',
            'description', 'description_teaser', 'networks', 'advice', 'gear',
            'ambiance', 'difficulty', 'information_desks', 'themes',
            'labels', 'practice', 'accessibilities', 'accessibility_level',
            'accessibility_signage', 'accessibility_slope', 'accessibility_covering', 'accessibility_exposure',
            'accessibility_width', 'accessibility_advice',
            'usages', 'access', 'route',
            'public_transport', 'advised_parking', 'web_links',
            'accessibility_infrastructure', 'parking_location', 'relationships',
            'points_reference', 'gpx', 'kml', 'source', 'portal',
            'type2', 'category', 'structure', 'treks', 'reservation_id', 'reservation_system',
            'children', 'parents', 'previous', 'next', 'ratings', 'ratings_description'
        ) + AltimetrySerializerMixin.Meta.fields + ZoningAPISerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields + PicturesSerializerMixin.Meta.fields

    def get_pictures(self, obj):
        pictures_list = []
        pictures_list.extend(obj.serializable_pictures)
        if settings.TREK_WITH_POIS_PICTURES:
            for poi in obj.published_pois:
                pictures_list.extend(poi.serializable_pictures)
        return pictures_list

    def get_parking_location(self, obj):
        if not obj.parking_location:
            return None
        point = obj.parking_location.transform(settings.API_SRID, clone=True)
        return [round(point.x, 7), round(point.y, 7)]

    def get_points_reference(self, obj):
        if not obj.points_reference:
            return None
        geojson = obj.points_reference.transform(settings.API_SRID, clone=True).geojson
        return json.loads(geojson)

    def get_gpx_url(self, obj):
        return reverse('trekking:trek_gpx_detail', kwargs={'lang': get_language(), 'pk': obj.pk, 'slug': obj.slug})

    def get_kml_url(self, obj):
        return reverse('trekking:trek_kml_detail', kwargs={'lang': get_language(), 'pk': obj.pk, 'slug': obj.slug})

    def get_category(self, obj):
        if settings.SPLIT_TREKS_CATEGORIES_BY_ITINERANCY and obj.children.exists():
            data = {
                'id': 'I',
                'label': _("Itinerancy"),
                'pictogram': '/static/trekking/itinerancy.svg',
                # Translators: This is a slug (without space, accent or special char)
                'slug': _('itinerancy'),
            }
        elif settings.SPLIT_TREKS_CATEGORIES_BY_PRACTICE and obj.practice:
            data = {
                'id': obj.practice.prefixed_id,
                'label': obj.practice.name,
                'pictogram': obj.practice.get_pictogram_url(),
                'slug': obj.practice.slug,
            }
        else:
            data = {
                'id': trekking_models.Practice.id_prefix,
                'label': _("Hike"),
                'pictogram': '/static/trekking/trek.svg',
                # Translators: This is a slug (without space, accent or special char)
                'slug': _('trek'),
            }
        if settings.SPLIT_TREKS_CATEGORIES_BY_ITINERANCY and obj.children.exists():
            data['order'] = settings.ITINERANCY_CATEGORY_ORDER
        elif settings.SPLIT_TREKS_CATEGORIES_BY_PRACTICE:
            data['order'] = obj.practice and obj.practice.order
        else:
            data['order'] = settings.TREK_CATEGORY_ORDER
        if not settings.SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY:
            data['type2_label'] = obj._meta.get_field('accessibilities').verbose_name
        return data


class TrekAPIGeojsonSerializer(GeoFeatureModelSerializer, TrekAPISerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(TrekAPISerializer.Meta):
        geo_field = 'api_geom'
        fields = TrekAPISerializer.Meta.fields + ('api_geom', )


class POITypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.POIType
        fields = ('id', 'pictogram', 'label')


class ClosePOISerializer(TranslatedModelSerializer):
    type = POITypeSerializer()

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'slug', 'name', 'type')


class POISerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(source='name_display')
    type = serializers.CharField(source='type_display')
    thumbnail = serializers.CharField(source='thumbnail_display')
    structure = serializers.SlugRelatedField('name', read_only=True)

    class Meta:
        model = trekking_models.POI
        fields = "__all__"


class POIGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = trekking_models.POI
        fields = ('id', 'name', 'published')


class POIAPISerializer(PublishableSerializerMixin, PicturesSerializerMixin, ZoningAPISerializerMixin,
                       TranslatedModelSerializer):
    type = POITypeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = trekking_models.POI
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = (
            'id', 'description', 'type', 'min_elevation', 'max_elevation', 'structure'
        ) + ZoningAPISerializerMixin.Meta.fields + PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields


class POIAPIGeojsonSerializer(DynamicFieldsMixin, GeoFeatureModelSerializer, POIAPISerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(POIAPISerializer.Meta):
        geo_field = 'api_geom'
        fields = POIAPISerializer.Meta.fields + ('api_geom', )


class ServiceTypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.ServiceType
        fields = ('id', 'pictogram', 'name')


class ServiceSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    name = serializers.CharField(source='name_display')
    type = serializers.CharField(source='type_display')

    class Meta:
        model = trekking_models.Service
        fields = "__all__"


class ServiceGeojsonSerializer(MapentityGeojsonModelSerializer):
    name = serializers.CharField(source='type.name')
    published = serializers.BooleanField(source='type.published')

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = trekking_models.Service
        fields = ('id', 'name', 'published')


class ServiceAPISerializer(serializers.ModelSerializer):
    type = ServiceTypeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = trekking_models.Service
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = ('id', 'type', 'structure')


class ServiceAPIGeojsonSerializer(GeoFeatureModelSerializer, ServiceAPISerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(ServiceAPISerializer.Meta):
        geo_field = 'api_geom'
        fields = ServiceAPISerializer.Meta.fields + ('api_geom', )
