import os

from rest_framework import serializers as rest_serializers
from rest_framework_gis import serializers as geo_serializers

from django.conf import settings


if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.tourism import models as tourism_models

    class TouristicContentListSerializer(geo_serializers.GeoFeatureModelSerializer):
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='geom2d_transformed')
        reservation_system = rest_serializers.ReadOnlyField(source='reservation_system.name', default="")
        pictures = rest_serializers.SerializerMethodField()

        def get_pictures(self, obj):
            if not obj.resized_pictures:
                return []
            first_picture = obj.resized_pictures[0][0]
            thdetail_first = obj.resized_pictures[0][1]
            return [{
                'author': first_picture.author,
                'title': first_picture.title,
                'legend': first_picture.legend,
                'url': os.path.join('/', str(self.context['root_pk']), settings.MEDIA_URL[1:], thdetail_first.name),
            }]

        class Meta:
            model = tourism_models.TouristicContent
            id_field = 'pk'
            geo_field = 'geometry'
            fields = ('id', 'pk', 'name', 'description', 'description_teaser', 'category',
                      'themes', 'contact', 'email', 'website', 'practical_info', 'pictures',
                      'type1', 'type2', 'approved', 'reservation_id', 'reservation_system', 'geometry')

    class TouristicEventListSerializer(geo_serializers.GeoFeatureModelSerializer):
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='geom2d_transformed')
        pictures = rest_serializers.SerializerMethodField()

        def get_pictures(self, obj):
            if not obj.resized_pictures:
                return []
            first_picture = obj.resized_pictures[0][0]
            thdetail_first = obj.resized_pictures[0][1]
            return [{
                'author': first_picture.author,
                'title': first_picture.title,
                'legend': first_picture.legend,
                'url': os.path.join('/', str(self.context['root_pk']), settings.MEDIA_URL[1:], thdetail_first.name),
            }]

        class Meta:
            model = tourism_models.TouristicEvent
            id_field = 'pk'
            geo_field = 'geometry'
            fields = ('id', 'pk', 'name', 'description_teaser', 'description', 'themes', 'pictures',
                      'begin_date', 'end_date', 'duration', 'meeting_point',
                      'start_time', 'contact', 'email', 'website',
                      'organizers', 'speaker', 'type', 'accessibility',
                      'capacity', 'booking', 'target_audience',
                      'practical_info', 'approved', 'geometry')

    class InformationDeskSerializer(rest_serializers.ModelSerializer):
        picture = rest_serializers.SerializerMethodField()

        class Meta:
            model = tourism_models.InformationDesk
            fields = ('id', 'description', 'email', 'latitude', 'longitude', 'municipality',
                      'name', 'phone', 'picture', 'postal_code', 'street', 'type',
                      'website')

        def get_picture(self, obj):
            if not obj.resized_picture:
                return None
            return '/{trek_id}{url}'.format(trek_id=self.context['root_pk'], url=obj.resized_picture.url),
