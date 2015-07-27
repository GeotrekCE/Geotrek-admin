from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers as rest_serializers

from geotrek.feedback import models as feedback_models


class ReportSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = feedback_models.Report
        geo_field = 'geom'
        id_field = 'id'

    def validate_geom(self, attrs, source):
        if source not in attrs:
            return attrs
        geom = attrs[source]
        point = GEOSGeometry(geom, srid=4326)
        attrs[source] = point
        return attrs
