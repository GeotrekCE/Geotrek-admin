from rest_framework_gis import fields as rest_gis_fields
from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import PictogramSerializerMixin, BasePublishableSerializerMixin

from geotrek.infrastructure import models as infrastructure_models


class InfrastructureTypeSerializer(PictogramSerializerMixin):
    class Meta:
        model = infrastructure_models.InfrastructureType
        fields = ('id', 'pictogram', 'label')


class InfrastructureSerializer(BasePublishableSerializerMixin):
    type = InfrastructureTypeSerializer()
    structure = StructureSerializer()

    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField()

    class Meta:
        model = infrastructure_models.Infrastructure
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'api_geom'
        fields = ('id', ) + \
            ('id', 'structure', 'name', 'type') + \
            BasePublishableSerializerMixin.Meta.fields
