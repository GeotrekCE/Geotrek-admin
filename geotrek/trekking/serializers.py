import json

import gpxpy
from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework import serializers as rest_serializers

from mapentity.serializers import GPXSerializer

from geotrek.common.serializers import (
    PictogramSerializerMixin,
    TranslatedModelSerializer, PicturesSerializerMixin,
    PublishableSerializerMixin
)
from geotrek.zoning.serializers import (DistrictSerializer, CitySerializer)
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


class ThemeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.Theme
        fields = ('id', 'pictogram', 'label')


class UsageSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.Field(source='usage')

    class Meta:
        model = trekking_models.Usage
        fields = ('id', 'pictogram', 'label')


class WebLinkCategorySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.WebLinkCategory
        fields = ('id', 'pictogram', 'label')


class WebLinkSerializer(TranslatedModelSerializer):
    category = WebLinkCategorySerializer()

    class Meta:
        model = trekking_models.WebLink
        fields = ('id', 'name', 'category', 'url')


class RelatedTrekSerializer(TranslatedModelSerializer):
    pk = rest_serializers.Field(source='id')
    slug = rest_serializers.Field(source='slug')
    url = rest_serializers.Field(source='get_detail_url')

    class Meta:
        model = trekking_models.Trek
        fields = ('pk', 'slug', 'name', 'url')


class TrekRelationshipSerializer(rest_serializers.ModelSerializer):
    published = rest_serializers.Field(source='trek_b.published')
    trek = RelatedTrekSerializer(source='trek_b')

    class Meta:
        model = trekking_models.TrekRelationship
        fields = ('has_common_departure', 'has_common_edge', 'is_circuit_step',
                  'trek', 'published')


class InformationDeskSerializer(TranslatedModelSerializer):
    photo_url = rest_serializers.Field(source='photo_url')
    latitude = rest_serializers.Field(source='latitude')
    longitude = rest_serializers.Field(source='longitude')

    class Meta:
        model = trekking_models.InformationDesk
        fields = ('name', 'description', 'phone', 'email', 'website',
                  'photo_url', 'street', 'postal_code', 'municipality',
                  'latitude', 'longitude')


class TrekSerializer(PublishableSerializerMixin, PicturesSerializerMixin,
                     AltimetrySerializerMixin, TranslatedModelSerializer):

    cities = CitySerializer(many=True)
    districts = DistrictSerializer(many=True)

    duration_pretty = rest_serializers.Field(source='duration_pretty')
    difficulty = DifficultyLevelSerializer()
    route = RouteSerializer()
    information_desks = InformationDeskSerializer(many=True)
    networks = NetworkSerializer(many=True)
    themes = ThemeSerializer(many=True)
    usages = UsageSerializer(many=True)
    web_links = WebLinkSerializer(many=True)
    relationships = TrekRelationshipSerializer(many=True, source='relationships')

    # Idea: use rest-framework-gis
    parking_location = rest_serializers.SerializerMethodField('get_parking_location')
    points_reference = rest_serializers.SerializerMethodField('get_points_reference')

    poi_layer = rest_serializers.SerializerMethodField('get_poi_layer_url')
    information_desk_layer = rest_serializers.SerializerMethodField('get_information_desk_layer_url')
    gpx = rest_serializers.SerializerMethodField('get_gpx_url')
    kml = rest_serializers.SerializerMethodField('get_kml_url')

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'departure', 'arrival', 'duration',
                  'duration_pretty', 'description', 'description_teaser',
                  'networks', 'advice', 'ambiance', 'difficulty',
                  'information_desks',
                  'themes', 'usages', 'access', 'route', 'public_transport', 'advised_parking',
                  'web_links', 'is_park_centered', 'disabled_infrastructure',
                  'parking_location',
                  'cities', 'districts', 'relationships', 'points_reference',
                  'poi_layer', 'information_desk_layer', 'gpx', 'kml') + \
            AltimetrySerializerMixin.Meta.fields + \
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


class POITypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.POIType
        fields = ('id', 'pictogram', 'label')


class POISerializer(PublishableSerializerMixin, PicturesSerializerMixin,
                    TranslatedModelSerializer):
    cities = CitySerializer(many=True)
    districts = DistrictSerializer(many=True)
    type = POITypeSerializer()

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'description', 'type', 'cities', 'districts') + \
            ('min_elevation', 'max_elevation') + \
            PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields
