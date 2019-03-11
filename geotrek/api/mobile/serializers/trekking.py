from __future__ import unicode_literals

from django.conf import settings
from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers

from geotrek.common import models as common_models
from geotrek.zoning.models import City


class AttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)

    def get_url(self, obj):
        if not obj.attachment_file:
            return ""
        trek_pk = self.context.get('trek_pk') or obj.object_id
        return '/{id}{file}'.format(id=trek_pk, file=obj.attachment_file.url)

    class Meta:
        model = common_models.Attachment
        fields = (
            'url', 'author', 'title', 'legend',
        )


if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from geotrek.trekking import models as trekking_models

    class POIListSerializer(geo_serializers.GeoFeatureModelSerializer):
        pictures = serializers.ListField(read_only=True, source='serializable_pictures', child=AttachmentSerializer())
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='geom2d_transformed')
        type_pois = serializers.ReadOnlyField(source='type.pk')

        class Meta:
            model = trekking_models.POI
            geo_field = 'geometry'
            fields = (
                'id', 'pictures', 'name', 'description', 'type_pois', 'geometry',
            )

    class TrekDetailSerializer(geo_serializers.GeoFeatureModelSerializer):
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='geom2d_transformed')
        first_picture = serializers.ReadOnlyField(source='serializable_resized_picture_mobile')
        length = serializers.SerializerMethodField(read_only=True)
        pictures = AttachmentSerializer(many=True, source='serializable_pictures')
        cities = serializers.SerializerMethodField(read_only=True)
        departure_city = serializers.SerializerMethodField(read_only=True)
        arrival_city = serializers.SerializerMethodField(read_only=True)

        def get_cities(self, obj):
            qs = City.objects
            if hasattr(qs, 'existing'):
                qs = qs.existing()
            cities = qs.filter(geom__intersects=(obj.geom, 0))
            return [city.code for city in cities]

        def get_departure_city(self, obj):
            qs = City.objects
            if hasattr(qs, 'existing'):
                qs = qs.existing()
            if obj.start_point:
                city = qs.filter(geom__covers=(obj.start_point, 0)).first()
                if city:
                    return city.code
            return None

        def get_arrival_city(self, obj):
            qs = City.objects
            if hasattr(qs, 'existing'):
                qs = qs.existing()
            if obj.start_point:
                city = qs.filter(geom__covers=(obj.end_point, 0)).first()
                if city:
                    return city.code
            return None

        def get_length(self, obj):
            return round(obj.length_2d_m, 1)

        def get_geometry(self, obj):
            return obj.geom2d_transformed

        class Meta:
            model = trekking_models.Trek
            geo_field = 'geometry'
            fields = (
                'id', 'name', 'first_picture', 'accessibilities', 'description_teaser', 'cities',
                'description', 'departure', 'arrival', 'duration', 'access', 'advised_parking', 'advice',
                'difficulty', 'length', 'ascent', 'descent', 'route', 'is_park_centered',
                'min_elevation', 'max_elevation', 'themes', 'networks', 'practice', 'difficulty',
                'geometry', 'pictures', 'information_desks', 'cities', 'departure_city', 'arrival_city'
            )
            auto_bbox = True

    class TrekListSerializer(geo_serializers.GeoFeatureModelSerializer):
        first_picture = serializers.ReadOnlyField(source='serializable_resized_picture_mobile')
        length = serializers.SerializerMethodField(read_only=True)
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='start_point', )
        cities = serializers.SerializerMethodField(read_only=True)
        departure_city = serializers.SerializerMethodField(read_only=True)

        def get_cities(self, obj):
            qs = City.objects
            if hasattr(qs, 'existing'):
                qs = qs.existing()
            cities = qs.filter(geom__intersects=(obj.geom, 0))
            return [city.code for city in cities]

        def get_departure_city(self, obj):
            qs = City.objects
            if hasattr(qs, 'existing'):
                qs = qs.existing()
            if obj.start_point:
                city = qs.filter(geom__covers=(obj.start_point, 0)).first()
                if city:
                    return city.code
            return None

        def get_length(self, obj):
            return round(obj.length_2d_m, 1)

        class Meta:
            model = trekking_models.Trek
            geo_field = 'geometry'
            fields = (
                'id', 'first_picture', 'name', 'departure', 'accessibilities', 'route', 'departure_city',
                'difficulty', 'practice', 'themes', 'length', 'geometry', 'cities', 'duration'
            )
