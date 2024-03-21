import gpxpy.gpx
from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import GPXSerializer, MapentityGeojsonModelSerializer
from rest_framework import serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import (
    PictogramSerializerMixin,
    TranslatedModelSerializer, PicturesSerializerMixin,
    PublishableSerializerMixin,
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


class POITypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.POIType
        fields = ('id', 'pictogram', 'label')


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


class TrekPOIAPIGeojsonSerializer(DynamicFieldsMixin, GeoFeatureModelSerializer, PublishableSerializerMixin,
                                  PicturesSerializerMixin, ZoningAPISerializerMixin, TranslatedModelSerializer):
    # Annotated geom field with API_SRID
    type = POITypeSerializer()
    structure = StructureSerializer()
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta:
        model = trekking_models.POI
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'api_geom'
        fields = (
            'id', 'description', 'type', 'min_elevation', 'max_elevation', 'structure', 'api_geom'
        ) + ZoningAPISerializerMixin.Meta.fields + PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields


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


class TrekServiceAPIGeojsonSerializer(GeoFeatureModelSerializer):
    type = ServiceTypeSerializer()
    structure = StructureSerializer()
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta:
        model = trekking_models.Service
        geo_field = 'api_geom'
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = ('id', 'type', 'structure', 'api_geom', )
