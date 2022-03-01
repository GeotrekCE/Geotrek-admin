from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityModelSerializer
from rest_framework import serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import PictogramSerializerMixin, BasePublishableSerializerMixin
from geotrek.infrastructure import models as infrastructure_models


class InfrastructureTypeSerializer(PictogramSerializerMixin):
    class Meta:
        model = infrastructure_models.InfrastructureType
        fields = ('id', 'pictogram', 'label')


class InfrastructureSerializer(DynamicFieldsMixin, BasePublishableSerializerMixin, MapentityModelSerializer):
    type = serializers.SlugRelatedField('label', read_only=True)
    condition = serializers.SlugRelatedField('label', read_only=True)
    cities = serializers.SerializerMethodField()
    structure = serializers.SlugRelatedField('name', read_only=True)
    usage_difficulty = serializers.SlugRelatedField('label', read_only=True)
    maintenance_difficulty = serializers.SlugRelatedField('label', read_only=True)

    def get_cities(self, obj):
        return obj.cities_display

    class Meta:
        model = infrastructure_models.Infrastructure
        fields = ('id', 'name', 'type', 'condition', 'type', 'cities', 'structure', "description",
                  "date_update",
                  "date_insert",
                  "implantation_year",
                  "usage_difficulty",
                  "maintenance_difficulty",
                  "published",
                  "uuid",)


class InfrastructureRandoV2GeojsonSerializer(GeoFeatureModelSerializer, serializers.ModelSerializer):
    # Annotated geom field with API_SRID
    type = InfrastructureTypeSerializer()
    structure = StructureSerializer()
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta:
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = ('id', ) + \
            ('id', 'structure', 'name', 'type', 'accessibility') + \
            BasePublishableSerializerMixin.Meta.fields


class InfrastructureGeojsonSerializer(GeoFeatureModelSerializer, InfrastructureSerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(InfrastructureSerializer.Meta):
        geo_field = 'api_geom'
        model = infrastructure_models.Infrastructure
        fields = ('id', 'structure', 'name', 'type', 'api_geom',)
