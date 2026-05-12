from rest_framework import serializers as rest_serializers

from geotrek.authent import models as authent_models


class StructureSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = authent_models.Structure
        fields = ("id", "name")
