from django.contrib.gis.geos import GEOSGeometry
from rest_framework import serializers as rest_serializers
from rest_framework_gis.fields import GeometryField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.feedback import models as feedback_models


class ReportSerializer(rest_serializers.ModelSerializer):
    activity = rest_serializers.SlugRelatedField('label', read_only=True)
    category = rest_serializers.SlugRelatedField('label', read_only=True)
    problem_magnitude = rest_serializers.SlugRelatedField('label', read_only=True)
    status = rest_serializers.SlugRelatedField('label', read_only=True)

    class Meta:
        model = feedback_models.Report
        fields = "__all__"


class ReportGeojsonSerializer(GeoFeatureModelSerializer):
    # Annotated geom field with API_SRID
    api_geom = GeometryField(read_only=True, precision=7)

    def validate_geom(self, value):
        return GEOSGeometry(value, srid=4326)

    class Meta:
        model = feedback_models.Report
        id_field = 'id'
        geo_field = 'api_geom'
        fields = ('id', 'email', 'activity', 'comment', 'category',
                  'status', 'problem_magnitude', 'related_trek',
                  'geom', 'api_geom', )
        extra_kwargs = {
            'geom': {'write_only': True},
        }


class ReportActivitySerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = feedback_models.ReportActivity
        fields = ['id', 'label']


class ReportCategorySerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = feedback_models.ReportCategory
        fields = ['id', 'label']


class ReportProblemMagnitudeSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = feedback_models.ReportProblemMagnitude
        fields = ['id', 'label']
