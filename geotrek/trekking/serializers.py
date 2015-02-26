import json

import gpxpy
from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework import serializers as rest_serializers

from mapentity.serializers import GPXSerializer

from geotrek.common.serializers import (
    PictogramSerializerMixin, ThemeSerializer,
    TranslatedModelSerializer, PicturesSerializerMixin,
    PublishableSerializerMixin
)
from geotrek.authent import models as authent_models
from geotrek.zoning.serializers import ZoningSerializerMixin
from geotrek.altimetry.serializers import AltimetrySerializerMixin
from geotrek.trekking import models as trekking_models


class TrekGPXSerializer(GPXSerializer):
    def end_object(self, trek):
        super(TrekGPXSerializer, self).end_object(trek)
        for poi in trek.pois.all():
            wpt = gpxpy.gpx.GPXWaypoint(latitude=poi.geom.y,
                                        longitude=poi.geom.x,
                                        elevation=poi.geom.z)
            wpt.name = u"%s: %s" % (poi.type, poi.name)
            wpt.description = poi.description
            self.gpx.waypoints.append(wpt)


class DifficultyLevelSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.Field(source='difficulty')

    class Meta:
        model = trekking_models.DifficultyLevel
        fields = ('id', 'pictogram', 'label')


class RouteSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.Field(source='route')

    class Meta:
        model = trekking_models.Route
        fields = ('id', 'pictogram', 'label')


class NetworkSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    name = rest_serializers.Field(source='network')

    class Meta:
        model = trekking_models.Route
        fields = ('id', 'pictogram', 'name')


class PracticeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.Field(source='name')

    class Meta:
        model = trekking_models.Practice
        fields = ('id', 'pictogram', 'label')


class AccessibilitySerializer(TranslatedModelSerializer):
    label = rest_serializers.Field(source='name')

    class Meta:
        model = trekking_models.Accessibility
        fields = ('id', 'label')


class TypeSerializer(TranslatedModelSerializer):
    name = rest_serializers.Field(source='name')

    class Meta:
        model = trekking_models.Practice
        fields = ('id', 'name')


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
    category_id = rest_serializers.Field(source='category_id')

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'category_id')


class RelatedTrekSerializer(TranslatedModelSerializer):
    pk = rest_serializers.Field(source='id')
    slug = rest_serializers.Field(source='slug')
    url = rest_serializers.Field(source='get_detail_url')

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'pk', 'slug', 'name', 'url')


class TrekRelationshipSerializer(rest_serializers.ModelSerializer):
    published = rest_serializers.Field(source='trek_b.published')
    trek = RelatedTrekSerializer(source='trek_b')

    class Meta:
        model = trekking_models.TrekRelationship
        fields = ('has_common_departure', 'has_common_edge', 'is_circuit_step',
                  'trek', 'published')


class StructureSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = authent_models.Structure
        fields = ('id', 'name')


class TrekSerializer(PublishableSerializerMixin, PicturesSerializerMixin,
                     AltimetrySerializerMixin, ZoningSerializerMixin,
                     TranslatedModelSerializer):
    duration_pretty = rest_serializers.Field(source='duration_pretty')
    difficulty = DifficultyLevelSerializer()
    route = RouteSerializer()
    networks = NetworkSerializer(many=True)
    themes = ThemeSerializer(many=True)
    practice = PracticeSerializer()
    usages = PracticeSerializer(source='usages', many=True)  # Rando v1 compat
    accessibilities = AccessibilitySerializer(many=True)
    web_links = WebLinkSerializer(many=True)
    relationships = TrekRelationshipSerializer(many=True, source='published_relationships')
    treks = CloseTrekSerializer(many=True, source='published_treks')

    # Idea: use rest-framework-gis
    parking_location = rest_serializers.SerializerMethodField('get_parking_location')
    points_reference = rest_serializers.SerializerMethodField('get_points_reference')

    poi_layer = rest_serializers.SerializerMethodField('get_poi_layer_url')
    information_desk_layer = rest_serializers.SerializerMethodField('get_information_desk_layer_url')
    gpx = rest_serializers.SerializerMethodField('get_gpx_url')
    kml = rest_serializers.SerializerMethodField('get_kml_url')
    structure = StructureSerializer()

    # For consistency with touristic contents
    type1 = TypeSerializer(source='usages', many=True)
    type2 = TypeSerializer(source='accessibilities', many=True)
    category = rest_serializers.SerializerMethodField('get_category')

    def __init__(self, *args, **kwargs):
        super(TrekSerializer, self).__init__(*args, **kwargs)

        from geotrek.tourism import serializers as tourism_serializers

        self.fields['information_desks'] = tourism_serializers.InformationDeskSerializer(many=True)
        self.fields['touristic_contents'] = tourism_serializers.CloseTouristicContentSerializer(many=True, source='published_touristic_contents')
        self.fields['touristic_events'] = tourism_serializers.CloseTouristicEventSerializer(many=True, source='published_touristic_events')

    class Meta:
        model = trekking_models.Trek
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'geom'
        fields = ('id', 'departure', 'arrival', 'duration',
                  'duration_pretty', 'description', 'description_teaser',
                  'networks', 'advice', 'ambiance', 'difficulty',
                  'information_desks', 'themes', 'practice', 'accessibilities',
                  'usages', 'access', 'route', 'public_transport', 'advised_parking',
                  'web_links', 'is_park_centered', 'disabled_infrastructure',
                  'parking_location', 'relationships', 'points_reference',
                  'poi_layer', 'information_desk_layer', 'gpx', 'kml',
                  'type1', 'type2', 'category', 'structure', 'treks') + \
            AltimetrySerializerMixin.Meta.fields + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields

    def get_parking_location(self, obj):
        if not obj.parking_location:
            return None
        return obj.parking_location.transform(settings.API_SRID, clone=True).coords

    def get_points_reference(self, obj):
        if not obj.points_reference:
            return None
        geojson = obj.points_reference.transform(settings.API_SRID, clone=True).geojson
        return json.loads(geojson)

    def get_poi_layer_url(self, obj):
        return reverse('trekking:trek_poi_geojson', kwargs={'pk': obj.pk})

    def get_information_desk_layer_url(self, obj):
        return reverse('trekking:trek_information_desk_geojson', kwargs={'pk': obj.pk})

    def get_gpx_url(self, obj):
        return reverse('trekking:trek_gpx_detail', kwargs={'pk': obj.pk})

    def get_kml_url(self, obj):
        return reverse('trekking:trek_kml_detail', kwargs={'pk': obj.pk})

    def get_category(self, obj):
        return {
            'id': obj.category_id,
            'label': obj._meta.verbose_name,
            'type1_label': obj._meta.get_field('practice').verbose_name,
            'type2_label': obj._meta.get_field('accessibilities').verbose_name,
            'pictogram': '/static/trekking/trek.svg',
        }


class POITypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.POIType
        fields = ('id', 'pictogram', 'label')


class ClosePOISerializer(TranslatedModelSerializer):
    slug = rest_serializers.Field(source='slug')
    type = POITypeSerializer()

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'slug', 'name', 'type')


class POISerializer(PublishableSerializerMixin, PicturesSerializerMixin,
                    ZoningSerializerMixin, TranslatedModelSerializer):
    type = POITypeSerializer()
    structure = StructureSerializer()

    def __init__(self, *args, **kwargs):
        super(POISerializer, self).__init__(*args, **kwargs)

        from geotrek.tourism import serializers as tourism_serializers

        self.fields['touristic_contents'] = tourism_serializers.CloseTouristicContentSerializer(many=True, source='published_touristic_contents')
        self.fields['touristic_events'] = tourism_serializers.CloseTouristicEventSerializer(many=True, source='published_touristic_events')

    class Meta:
        model = trekking_models.Trek
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'geom'
        fields = ('id', 'description', 'type',) + \
            ('min_elevation', 'max_elevation', 'structure') + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields
