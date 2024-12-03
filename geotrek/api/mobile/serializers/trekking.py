import os
from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from rest_framework import serializers
from rest_framework_gis import serializers as geo_serializers

from geotrek.api.mobile.serializers.tourism import InformationDeskSerializer
from geotrek.common.functions import StartPoint, EndPoint
from geotrek.zoning.models import City, District

if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from geotrek.trekking import models as trekking_models

    class POIListSerializer(geo_serializers.GeoFeatureModelSerializer):
        pictures = serializers.SerializerMethodField()
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='geom2d_transformed')
        type = serializers.ReadOnlyField(source='type.pk')

        def get_pictures(self, obj):
            if not obj.resized_pictures:
                return []
            root_pk = self.context.get('root_pk') or obj.pk
            return obj.serializable_pictures_mobile(root_pk)

        class Meta:
            model = trekking_models.POI
            id_field = 'pk'
            geo_field = 'geometry'
            fields = (
                'id', 'pk', 'pictures', 'name', 'description', 'type', 'geometry',
            )

    class TrekBaseSerializer(geo_serializers.GeoFeatureModelSerializer):
        cities = serializers.SerializerMethodField()
        districts = serializers.SerializerMethodField()
        length = serializers.FloatField(source='length_2d_display')
        departure_city = serializers.SerializerMethodField()

        def get_cities(self, obj):
            qs = City.objects.filter(published=True)
            cities = qs.filter(geom__intersects=(obj.geom, 0))
            return cities.values_list('code', flat=True)

        def get_departure_city(self, obj):
            qs = City.objects.filter(published=True)
            if obj.start_point:
                city = qs.filter(geom__covers=(obj.start_point, 0)).first()
                if city:
                    return city.code
            return None

        def get_districts(self, obj):
            qs = District.objects.filter(published=True)
            districts = qs.filter(geom__intersects=(obj.geom, 0))
            return [district.pk for district in districts]

        class Meta:
            model = trekking_models.Trek
            id_field = 'pk'
            geo_field = 'geometry'

    class TrekListSerializer(TrekBaseSerializer):
        first_picture = serializers.SerializerMethodField()
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='start_point', )

        def get_first_picture(self, obj):
            root_pk = self.context.get('root_pk') or obj.pk
            return obj.resized_picture_mobile(root_pk)

        class Meta(TrekBaseSerializer.Meta):
            fields = (
                'id', 'pk', 'first_picture', 'name', 'departure', 'accessibilities', 'route', 'departure_city',
                'difficulty', 'practice', 'themes', 'length', 'geometry', 'districts', 'cities', 'duration', 'ascent',
                'descent',
            )

    class TrekDetailSerializer(TrekBaseSerializer):
        geometry = geo_serializers.GeometryField(read_only=True, precision=7, source='geom2d_transformed')
        pictures = serializers.SerializerMethodField()
        arrival_city = serializers.SerializerMethodField()
        information_desks = serializers.SerializerMethodField()
        parking_location = serializers.SerializerMethodField()
        profile = serializers.SerializerMethodField()
        points_reference = serializers.SerializerMethodField()
        children = serializers.SerializerMethodField()

        def get_pictures(self, obj):
            root_pk = self.context.get('root_pk') or obj.pk
            return obj.serializable_pictures_mobile(root_pk)

        def get_children(self, obj):
            children = obj.children.all().annotate(start_point=Transform(StartPoint('geom'), settings.API_SRID),
                                                   end_point=Transform(EndPoint('geom'), settings.API_SRID))
            serializer_children = TrekListSerializer(children, many=True, context={'root_pk': obj.pk})
            return serializer_children.data

        def get_points_reference(self, obj):
            if not obj.points_reference:
                return None
            return obj.points_reference.transform(settings.API_SRID, clone=True).coords

        def get_parking_location(self, obj):
            if not obj.parking_location:
                return None
            return obj.parking_location.transform(settings.API_SRID, clone=True).coords

        def get_arrival_city(self, obj):
            qs = City.objects.filter(published=True)
            if obj.end_point:
                city = qs.filter(geom__covers=(obj.end_point, 0)).first()
                if city:
                    return city.code
            return None

        def get_information_desks(self, obj):
            return [
                InformationDeskSerializer(information_desk, context={'root_pk': obj.pk}).data
                for information_desk in obj.information_desks.all()
            ]

        def get_profile(self, obj):
            root_pk = self.context.get('root_pk') or obj.pk
            return os.path.join("/", str(root_pk), settings.MEDIA_URL.lstrip('/'), obj.get_elevation_chart_url_png())

        class Meta(TrekBaseSerializer.Meta):
            auto_bbox = True
            fields = (
                'id', 'pk', 'name', 'slug', 'accessibilities', 'description_teaser', 'cities', 'profile',
                'description', 'departure', 'arrival', 'duration', 'access', 'advised_parking', 'advice',
                'difficulty', 'length', 'ascent', 'descent', 'route', 'labels', 'parking_location',
                'min_elevation', 'max_elevation', 'themes', 'networks', 'practice', 'difficulty',
                'geometry', 'pictures', 'information_desks', 'cities', 'departure_city', 'arrival_city',
                'points_reference', 'districts', 'ambiance', 'children',
            )
