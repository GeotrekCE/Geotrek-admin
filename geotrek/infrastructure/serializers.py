from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from rest_framework import serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import PictogramSerializerMixin, BasePublishableSerializerMixin
from . import models as infrastructure_models


class InfrastructureTypeSerializer(PictogramSerializerMixin):
    class Meta:
        model = infrastructure_models.InfrastructureType
        fields = ('id', 'pictogram', 'label')


class InfrastructureSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    checkbox = serializers.CharField(source='checkbox_display')
    name = serializers.CharField(source='name_display')
    type = serializers.CharField(source='type_display')
    condition = serializers.SlugRelatedField('label', read_only=True)
    cities = serializers.CharField(source='cities_display')
    structure = serializers.SlugRelatedField('name', read_only=True)
    usage_difficulty = serializers.SlugRelatedField('label', read_only=True)
    maintenance_difficulty = serializers.SlugRelatedField('label', read_only=True)

    class Meta:
        model = infrastructure_models.Infrastructure
        fields = "__all__"


class InfrastructureGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = infrastructure_models.Infrastructure
        fields = ['id', 'name', 'published']


class InfrastructureAPISerializer(BasePublishableSerializerMixin):
    type = InfrastructureTypeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = infrastructure_models.Infrastructure
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = ('id', 'structure', 'name', 'type', 'accessibility') + BasePublishableSerializerMixin.Meta.fields


class InfrastructureAPIGeojsonSerializer(GeoFeatureModelSerializer, InfrastructureAPISerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(InfrastructureAPISerializer.Meta):
        geo_field = 'api_geom'
        fields = InfrastructureAPISerializer.Meta.fields + ('api_geom', )
