from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers as rest_serializers

from geotrek.feedback import models as feedback_models


class ReportSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = feedback_models.Report
        geo_field = 'geom'
        id_field = 'id'
        fields = ('id', 'name', 'email', 'comment', 'category', 'status', 'geom', 'context_object')

    def validate_geom(self, value):
        return GEOSGeometry(value, srid=4326)
