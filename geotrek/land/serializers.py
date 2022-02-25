from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityModelSerializer
from rest_framework import serializers

from geotrek.land.models import LandEdge


class LandEdgeSerializer(DynamicFieldsMixin, MapentityModelSerializer):
    land_type = serializers.SlugRelatedField('name', read_only=True)
    length = serializers.FloatField(source='length_display')

    class Meta:
        model = LandEdge
        fields = (
            'id', 'land_type', 'min_elevation', 'max_elevation', 'date_update', 'length_2d', 'date_insert',
            'owner', 'agreement', 'uuid', 'length'
        )
