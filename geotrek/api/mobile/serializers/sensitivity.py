from django.conf import settings
from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers


if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from geotrek.sensitivity import models as sensitivity_models

    class SensitiveAreaListSerializer(geo_serializers.GeoFeatureModelSerializer):
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='geom2d_transformed')
        name = serializers.ReadOnlyField(source='species.name')
        description = serializers.ReadOnlyField()
        practices = serializers.PrimaryKeyRelatedField(many=True, source='species.practices', read_only=True)
        info_url = serializers.URLField(source='species.url')
        period = serializers.SerializerMethodField()

        class Meta:
            model = sensitivity_models.SensitiveArea
            id_field = 'pk'
            geo_field = 'geometry'
            fields = (
                'id', 'pk', 'name', 'description', 'practices',
                'contact', 'info_url', 'period', 'geometry',
            )

        def get_period(self, obj):
            return [getattr(obj.species, 'period{:02}'.format(p)) for p in range(1, 13)]
