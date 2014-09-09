import json

import gpxpy
from django.db import models as django_db_models
from django.conf import settings
from django.core.urlresolvers import reverse
from rest_framework import serializers as rest_serializers

from rest_framework import serializers as rest_fields
from mapentity.serializers import GPXSerializer

from geotrek.core.models import AltimetryMixin
from geotrek.trekking import models as trekking_models
from geotrek.zoning import models as zoning_models


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


class TranslatedModelSerializer(rest_serializers.ModelSerializer):
    def get_field(self, model_field):
        kwargs = {}
        if issubclass(
                model_field.__class__,
                      (django_db_models.CharField,
                       django_db_models.TextField)):
            if model_field.null:
                kwargs['allow_none'] = True
            kwargs['max_length'] = getattr(model_field, 'max_length')
            return rest_fields.CharField(**kwargs)
        return super(TranslatedModelSerializer, self).get_field(model_field)


class AltimetrySerializerMixin(rest_serializers.ModelSerializer):
    elevation_area_url = rest_serializers.SerializerMethodField('get_elevation_area_url')
    altimetric_profile = rest_serializers.SerializerMethodField('get_altimetric_profile_url')

    class Meta:
        fields = ('elevation_area_url', 'altimetric_profile') + \
                 tuple(AltimetryMixin.COLUMNS)

    def get_elevation_area_url(self, obj):
        return reverse('trekking:trek_elevation_area', kwargs={'pk': obj.pk})

    def get_altimetric_profile_url(self, obj):
        return reverse('trekking:trek_profile', kwargs={'pk': obj.pk})


class PictogramSerializerMixin(rest_serializers.ModelSerializer):
    pictogram = rest_serializers.Field('get_pictogram_url')


class PicturesSerializerMixin(rest_serializers.ModelSerializer):
    thumbnail = rest_serializers.Field(source='serializable_thumbnail')
    pictures = rest_serializers.Field(source='serializable_pictures')

    class Meta:
        fields = ('thumbnail', 'pictures',)


class PublishableSerializerMixin(rest_serializers.ModelSerializer):
    slug = rest_serializers.Field(source='slug')
    published_status = rest_serializers.Field(source='published_status')

    map_image_url = rest_serializers.Field(source='map_image_url')
    printable = rest_serializers.SerializerMethodField('get_printable_url')
    filelist_url = rest_serializers.SerializerMethodField('get_filelist_url')

    def get_printable_url(self, obj):
        return reverse('trekking:trek_printable', kwargs={'pk': obj.pk})

    def get_filelist_url(self, obj):
        return reverse('get_attachments', kwargs={'app_label': 'trekking',
                                                  'module_name': 'trek',
                                                  'pk': obj.pk})

    class Meta:
        fields = ('name', 'slug', 'published', 'published_status', 'publication_date',
                  'map_image_url', 'filelist_url', 'printable')


class CitySerializer(rest_serializers.ModelSerializer):

    class Meta:
        model = zoning_models.City
        fields = ('code', 'name')


class DistrictSerializer(rest_serializers.ModelSerializer):

    class Meta:
        model = zoning_models.District
        fields = ('id', 'name')


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

    duration_pretty = rest_serializers.Field(source='duration_pretty')
    difficulty = DifficultyLevelSerializer()
    route = RouteSerializer()
    cities = CitySerializer(many=True)
    districts = DistrictSerializer(many=True)
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
                     AltimetrySerializerMixin, TranslatedModelSerializer):
    type = POITypeSerializer()

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'description', 'type') + \
                 AltimetrySerializerMixin.Meta.fields + \
                 PublishableSerializerMixin.Meta.fields + \
                 PicturesSerializerMixin.Meta.fields
