import gpxpy

from django.db import models as django_db_models
from rest_framework import serializers as rest_serializers
from rest_framework_gis import serializers as rest_gis_serializers

from rest_framework import serializers as rest_fields
from mapentity.serializers import GPXSerializer

from geotrek.core.models import AltimetryMixin
from . import models as trekking_models


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


class TrekSerializer(TranslatedModelSerializer):

    slug = rest_serializers.Field(source='slug')
    duration_pretty = rest_serializers.Field(source='duration_pretty')
    published_status = rest_serializers.Field(source='published_status')
    thumbnail = rest_serializers.Field(source='thumbnail')
    pictures = rest_serializers.Field(source='pictures')
    cities = rest_serializers.Field(source='cities')
    districts = rest_serializers.Field(source='districts')
    relationships = rest_serializers.Field(source='relationships')
    map_image_url = rest_serializers.Field(source='map_image_url')
    elevation_area_url = rest_serializers.Field(source='elevation_area_url')
    altimetric_profile = rest_serializers.Field(source='altimetric_profile_url')
    poi_layer = rest_serializers.Field(source='poi_layer_url')
    information_desk_layer = rest_serializers.Field(source='information_desk_layer_url')
    filelist_url = rest_serializers.Field(source='filelist_url')
    gpx = rest_serializers.Field(source='gpx_url')
    kml = rest_serializers.Field(source='kml_url')
    printable = rest_serializers.Field(source='printable_url')

    class Meta:
        model = trekking_models.Trek
        fields = ['id', 'name', 'slug', 'departure', 'arrival', 'duration',
                  'duration_pretty', 'description', 'description_teaser'] + \
                 AltimetryMixin.COLUMNS + \
                 ['published', 'published_status',
                  'networks', 'advice', 'ambiance', 'difficulty',
                  'information_desks',
                  'themes', 'usages', 'access', 'route', 'public_transport', 'advised_parking',
                  'web_links', 'is_park_centered', 'disabled_infrastructure',
                  'parking_location', 'thumbnail', 'pictures',
                  'cities', 'districts', 'relationships', 'points_reference'] + \
                 ['map_image_url', 'elevation_area_url',
                  'altimetric_profile', 'poi_layer', 'information_desk_layer',
                  'filelist_url', 'gpx', 'kml', 'printable']


    # @property
    # def serializable_relationships(self):
    #     return [{
    #             'has_common_departure': rel.has_common_departure,
    #             'has_common_edge': rel.has_common_edge,
    #             'is_circuit_step': rel.is_circuit_step,
    #             'trek': {
    #                 'pk': rel.trek_b.pk,
    #                 'slug': rel.trek_b.slug,
    #                 'name': rel.trek_b.name,
    #                 'url': reverse('trekking:trek_json_detail', args=(rel.trek_b.pk,)),
    #             },
    #             'published': rel.trek_b.published} for rel in self.relationships]

    # @property
    # def serializable_cities(self):
    #     return [{'code': city.code,
    #              'name': city.name} for city in self.cities]

    # @property
    # def serializable_networks(self):
    #     return [{'id': network.id,
    #              'pictogram': network.serializable_pictogram,
    #              'name': network.network} for network in self.networks.all()]

    # @property
    # def serializable_difficulty(self):
    #     if not self.difficulty:
    #         return None
    #     return {'id': self.difficulty.pk,
    #             'pictogram': self.difficulty.serializable_pictogram,
    #             'label': self.difficulty.difficulty}

    # @property
    # def serializable_themes(self):
    #     return [{'id': t.pk,
    #              'pictogram': t.serializable_pictogram,
    #              'label': t.label} for t in self.themes.all()]

    # @property
    # def serializable_usages(self):
    #     return [{'id': u.pk,
    #              'pictogram': u.serializable_pictogram,
    #              'label': u.usage} for u in self.usages.all()]

    # @property
    # def serializable_districts(self):
    #     return [{'id': d.pk,
    #              'name': d.name} for d in self.districts]

    # @property
    # def serializable_route(self):
    #     if not self.route:
    #         return None
    #     return {'id': self.route.pk,
    #             'pictogram': self.route.serializable_pictogram,
    #             'label': self.route.route}

    # @property
    # def serializable_web_links(self):
    #     return [{'id': w.pk,
    #              'name': w.name,
    #              'category': w.serializable_category,
    #              'url': w.url} for w in self.web_links.all()]

    # @property
    # def serializable_information_desks(self):
    #     return [d.__json__() for d in self.information_desks.all()]

    # @property
    # def serializable_parking_location(self):
    #     if not self.parking_location:
    #         return None
    #     return self.parking_location.transform(settings.API_SRID, clone=True).coords

    # @property
    # def serializable_points_reference(self):
    #     if not self.points_reference:
    #         return None
    #     geojson = self.points_reference.transform(settings.API_SRID, clone=True).geojson
    #     return json.loads(geojson)
