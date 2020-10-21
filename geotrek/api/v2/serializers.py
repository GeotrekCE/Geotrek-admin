from django.conf import settings
from django.urls import reverse
from django.db.models import F
from django.utils.translation import get_language, ugettext_lazy as _
from drf_dynamic_fields import DynamicFieldsMixin
from rest_framework import serializers
from rest_framework.relations import HyperlinkedIdentityField
from rest_framework_gis import serializers as geo_serializers

from geotrek.api.v2.functions import Transform, Length, Length3D
from geotrek.api.v2.utils import get_translation_or_dict
from geotrek.common import models as common_models
from geotrek.core.models import simplify_coords
from geotrek.authent import models as authent_models

if 'geotrek.core' in settings.INSTALLED_APPS:
    from geotrek.core import models as core_models
if 'geotrek.tourism' in settings.INSTALLED_APPS:
    from geotrek.tourism import models as tourism_models
if 'geotrek.trekking' in settings.INSTALLED_APPS:
    from geotrek.trekking import models as trekking_models
if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    from geotrek.sensitivity import models as sensitivity_models
if 'geotrek.zoning' in settings.INSTALLED_APPS:
    from geotrek.zoning import models as zoning_models


class BaseGeoJSONSerializer(geo_serializers.GeoFeatureModelSerializer):
    """
    Mixin used to serialize geojson
    """

    def to_representation(self, instance):
        """Round bbox coordinates"""
        feature = super().to_representation(instance)
        feature['bbox'] = simplify_coords(feature['bbox'])
        return feature

    class Meta:
        geo_field = 'geometry'
        auto_bbox = True


def override_serializer(format_output, dimension, base_serializer_class):
    """
    Override Serializer switch output format and dimension data
    """
    if format_output == 'geojson':
        if dimension == '3':
            class GeneratedGeo3DSerializer(BaseGeoJSONSerializer,
                                           base_serializer_class):
                geometry = geo_serializers.GeometryField(read_only=True, source='geom3d_transformed', precision=7)

                class Meta(BaseGeoJSONSerializer.Meta,
                           base_serializer_class.Meta):
                    pass

            final_class = GeneratedGeo3DSerializer

        else:
            class GeneratedGeoSerializer(BaseGeoJSONSerializer,
                                         base_serializer_class):
                class Meta(BaseGeoJSONSerializer.Meta,
                           base_serializer_class.Meta):
                    pass

            final_class = GeneratedGeoSerializer
    else:
        if dimension == '3':
            class Generated3DSerializer(base_serializer_class):
                geometry = geo_serializers.GeometryField(read_only=True, source='geom3d_transformed', precision=7)

                class Meta(base_serializer_class.Meta):
                    pass

            final_class = Generated3DSerializer

        else:
            final_class = base_serializer_class

    return final_class


if 'geotrek.trekking' in settings.INSTALLED_APPS:
    class TrekThemeSerializer(serializers.ModelSerializer):
        class Meta:
            model = trekking_models.Theme
            fields = ('id',)

    class TrekNetworkSerializer(serializers.ModelSerializer):
        label = serializers.SerializerMethodField(read_only=True)

        def get_label(self, obj):
            return get_translation_or_dict('network', self, obj)

        class Meta:
            model = trekking_models.TrekNetwork
            fields = ('id', 'label', 'pictogram')

    class TrekPracticeInTrekSerializer(serializers.ModelSerializer):
        name = serializers.SerializerMethodField(read_only=True)

        def get_name(self, obj):
            return get_translation_or_dict('name', self, obj)

        class Meta:
            model = trekking_models.Practice
            fields = ('id', 'name', 'pictogram',)

    class TrekPracticeSerializer(serializers.ModelSerializer):
        name = serializers.SerializerMethodField(read_only=True)

        def get_name(self, obj):
            return get_translation_or_dict('name', self, obj)

        class Meta:
            model = trekking_models.Practice
            fields = ('id', 'name', 'order', 'pictogram',)

    class TrekDifficultySerializer(serializers.ModelSerializer):
        label = serializers.SerializerMethodField(read_only=True)

        def get_label(self, obj):
            return get_translation_or_dict('difficulty', self, obj)

        class Meta:
            model = trekking_models.DifficultyLevel
            fields = ('id', 'label', 'cirkwi_level', 'pictogram')

    class TrekAccessibilitySerializer(serializers.ModelSerializer):
        class Meta:
            model = trekking_models.Accessibility
            fields = ('id',)

    class TrekLabelSerializer(serializers.ModelSerializer):
        name = serializers.SerializerMethodField(read_only=True)
        advice = serializers.SerializerMethodField(read_only=True)

        def get_name(self, obj):
            return get_translation_or_dict('name', self, obj)

        def get_advice(self, obj):
            return get_translation_or_dict('advice', self, obj)

        class Meta:
            model = trekking_models.LabelTrek
            fields = ('id', 'pictogram', 'name', 'advice', 'filter_rando')


class TrekReservationSystemSerializer(serializers.ModelSerializer):
    class Meta:
        model = common_models.ReservationSystem
        fields = ('id', 'name')


class AttachmentSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    url = serializers.FileField(source='attachment_file')

    class Meta:
        model = common_models.Attachment
        fields = (
            'url', 'author', 'title', 'legend',
            'starred', 'date_insert', 'date_update'
        )


if 'geotrek.tourism' in settings.INSTALLED_APPS:
    class TouristicContentCategorySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        class Meta:
            model = tourism_models.TouristicContentCategory
            fields = ('id', 'label', 'pictogram', 'type1_label', 'type2_label', 'order')

    class TouristicContentListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        url = HyperlinkedIdentityField(view_name='apiv2:touristiccontent-detail')
        category = TouristicContentCategorySerializer()
        geometry = geo_serializers.GeometryField(read_only=True, source="geom2d_transformed", precision=7)

        class Meta:
            model = tourism_models.TouristicContent
            fields = ('id', 'url', 'description_teaser', 'description', 'category', 'approved', 'geometry')

    class TouristicContentDetailSerializer(TouristicContentListSerializer):

        class Meta(TouristicContentListSerializer.Meta):
            fields = tuple(field for field in TouristicContentListSerializer.Meta.fields if field != 'url') + ('pictures',)


if 'geotrek.core' in settings.INSTALLED_APPS:
    class PathListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        url = HyperlinkedIdentityField(view_name='apiv2:trek-detail')
        geometry = geo_serializers.GeometryField(read_only=True, source="geom2d_transformed", precision=7)
        length_2d = serializers.SerializerMethodField(read_only=True)
        length_3d = serializers.SerializerMethodField(read_only=True)

        def get_length_2d(self, obj):
            return round(obj.length_2d_m, 1)

        def get_length_3d(self, obj):
            return round(obj.length_3d_m, 1)

        class Meta:
            model = core_models.Path
            fields = ('id', 'name', 'comments', 'url', 'length_2d', 'length_3d', 'geometry')


if 'geotrek.trekking' in settings.INSTALLED_APPS:
    class TrekListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        url = HyperlinkedIdentityField(view_name='apiv2:trek-detail')
        published = serializers.SerializerMethodField(read_only=True)
        geometry = geo_serializers.GeometryField(read_only=True, source="geom2d_transformed", precision=7)
        length_2d = serializers.SerializerMethodField(read_only=True)
        length_3d = serializers.SerializerMethodField(read_only=True)
        name = serializers.SerializerMethodField(read_only=True)
        description = serializers.SerializerMethodField(read_only=True)
        description_teaser = serializers.SerializerMethodField(read_only=True)
        difficulty = TrekDifficultySerializer(read_only=True)
        departure = serializers.SerializerMethodField(read_only=True)
        arrival = serializers.SerializerMethodField(read_only=True)
        themes = TrekThemeSerializer(many=True, read_only=True)
        networks = TrekNetworkSerializer(many=True, read_only=True)
        practice = TrekPracticeInTrekSerializer(read_only=True)
        external_id = serializers.CharField(source='eid')
        second_external_id = serializers.CharField(source='eid2')
        create_datetime = serializers.SerializerMethodField(read_only=True)
        update_datetime = serializers.SerializerMethodField(read_only=True)

        def get_update_datetime(self, obj):
            return obj.topo_object.date_update

        def get_create_datetime(self, obj):
            return obj.topo_object.date_insert

        def get_published(self, obj):
            return get_translation_or_dict('published', self, obj)

        def get_name(self, obj):
            return get_translation_or_dict('name', self, obj)

        def get_description(self, obj):
            return get_translation_or_dict('description', self, obj)

        def get_departure(self, obj):
            return get_translation_or_dict('departure', self, obj)

        def get_arrival(self, obj):
            return get_translation_or_dict('arrival', self, obj)

        def get_description_teaser(self, obj):
            return get_translation_or_dict('description_teaser', self, obj)

        def get_length_2d(self, obj):
            return round(obj.length_2d_m, 1)

        def get_length_3d(self, obj):
            return round(obj.length_3d_m, 1)

        class Meta:
            model = trekking_models.Trek
            fields = (
                'id', 'url', 'name', 'description_teaser',
                'description', 'departure', 'arrival', 'duration',
                'difficulty', 'length_2d', 'length_3d', 'ascent', 'descent',
                'min_elevation', 'max_elevation', 'themes',
                'networks', 'practice', 'external_id', 'second_external_id',
                'published', 'geometry', 'update_datetime', 'create_datetime'
            )

    class TrekDetailSerializer(TrekListSerializer):
        pictures = AttachmentSerializer(many=True, )
        accessibilities = TrekAccessibilitySerializer(many=True, read_only=True)
        labels = TrekLabelSerializer(many=True)
        gpx = serializers.SerializerMethodField('get_gpx_url')
        kml = serializers.SerializerMethodField('get_kml_url')
        advice = serializers.SerializerMethodField(read_only=True)
        advised_parking = serializers.SerializerMethodField(read_only=True)
        parking_location = serializers.SerializerMethodField(read_only=True)
        children = serializers.ReadOnlyField(source='children_id')
        parents = serializers.ReadOnlyField(source='parents_id')
        public_transport = serializers.SerializerMethodField(read_only=True)
        elevation_area_url = serializers.SerializerMethodField()
        elevation_svg_url = serializers.SerializerMethodField()
        altimetric_profile = serializers.SerializerMethodField('get_altimetric_profile_url')
        reservation_system = TrekReservationSystemSerializer(many=False, read_only=True)

        def get_gpx_url(self, obj):
            return reverse('trekking:trek_gpx_detail', kwargs={'lang': get_language(), 'pk': obj.pk, 'slug': obj.slug})

        def get_kml_url(self, obj):
            return reverse('trekking:trek_kml_detail', kwargs={'lang': get_language(), 'pk': obj.pk, 'slug': obj.slug})

        def get_advice(self, obj):
            return get_translation_or_dict('advice', self, obj)

        def get_advised_parking(self, obj):
            return get_translation_or_dict('advised_parking', self, obj)

        def get_parking_location(self, obj):
            if not obj.parking_location:
                return None
            point = obj.parking_location.transform(settings.API_SRID, clone=True)
            return [round(point.x, 7), round(point.y, 7)]

        def get_public_transport(self, obj):
            return get_translation_or_dict('public_transport', self, obj)

        def get_elevation_area_url(self, obj):
            return reverse('trekking:trek_elevation_area', kwargs={'lang': get_language(), 'pk': obj.pk})

        def get_elevation_svg_url(self, obj):
            return reverse('trekking:trek_profile_svg', kwargs={'lang': get_language(), 'pk': obj.pk})

        def get_altimetric_profile_url(self, obj):
            return reverse('trekking:trek_profile', kwargs={'lang': get_language(), 'pk': obj.pk})

        class Meta(TrekListSerializer.Meta):
            fields = tuple((field for field in TrekListSerializer.Meta.fields if field != 'url')) + ('pictures', 'accessibilities', 'labels', 'advice', 'advised_parking', 'parking_location', 'gpx', 'kml', 'children', 'parents', 'public_transport', 'elevation_area_url', 'elevation_svg_url', 'altimetric_profile', 'reservation_system')

    class TourListSerializer(TrekListSerializer):
        url = HyperlinkedIdentityField(view_name='apiv2:tour-detail')
        count_children = serializers.SerializerMethodField(read_only=True)

        def get_count_children(self, obj):
            return obj.count_children

        class Meta(TrekListSerializer.Meta):
            fields = TrekListSerializer.Meta.fields + ('count_children',)

    class TourDetailSerializer(TrekDetailSerializer):
        steps = serializers.SerializerMethodField(read_only=True)

        def get_steps(self, obj):
            qs = obj.children \
                .select_related('topo_object', 'difficulty') \
                .prefetch_related('topo_object__aggregations', 'themes', 'networks', 'attachments') \
                .annotate(geom2d_transformed=Transform(F('geom'), settings.API_SRID),
                          geom3d_transformed=Transform(F('geom_3d'), settings.API_SRID),
                          length_2d_m=Length('geom'),
                          length_3d_m=Length3D('geom_3d'))
            FinalClass = override_serializer(self.context.get('request').GET.get('format'),
                                             self.context.get('request').GET.get('dim'),
                                             TrekDetailSerializer)
            return FinalClass(qs, many=True, context=self.context).data

        class Meta(TrekDetailSerializer.Meta):
            fields = TrekDetailSerializer.Meta.fields + ('steps',)

    class POITypeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        label = serializers.SerializerMethodField(read_only=True)

        def get_label(self, obj):
            return get_translation_or_dict('label', self, obj)

        class Meta:
            model = trekking_models.POIType
            fields = ('id', 'label', 'pictogram')

    class POIListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        url = HyperlinkedIdentityField(view_name='apiv2:poi-detail')
        name = serializers.SerializerMethodField(read_only=True)
        description = serializers.SerializerMethodField(read_only=True)
        external_id = serializers.SerializerMethodField(read_only=True, help_text=_("External ID"))
        published = serializers.SerializerMethodField(read_only=True)
        create_datetime = serializers.SerializerMethodField(read_only=True)
        update_datetime = serializers.SerializerMethodField(read_only=True)
        geometry = geo_serializers.GeometryField(read_only=True, source="geom2d_transformed", precision=7)
        type = POITypeSerializer(read_only=True)

        def get_published(self, obj):
            return get_translation_or_dict('published', self, obj)

        def get_external_id(self, obj):
            return obj.eid

        def get_name(self, obj):
            return get_translation_or_dict('name', self, obj)

        def get_update_datetime(self, obj):
            return obj.topo_object.date_update

        def get_create_datetime(self, obj):
            return obj.topo_object.date_insert

        def get_description(self, obj):
            return get_translation_or_dict('description', self, obj)

        class Meta:
            model = trekking_models.POI
            fields = (
                'id', 'url', 'name', 'type', 'description', 'external_id',
                'published', 'geometry', 'update_datetime', 'create_datetime'
            )

    class POIDetailSerializer(POIListSerializer):
        pictures = AttachmentSerializer(many=True, )

        class Meta(POIListSerializer.Meta):
            fields = tuple((field for field in POIListSerializer.Meta.fields if field != 'url')) + ('pictures',)

    class ThemeSerializer(TrekThemeSerializer):
        label = serializers.SerializerMethodField(read_only=True)

        def get_label(self, obj):
            return get_translation_or_dict('label', self, obj)

        class Meta(TrekThemeSerializer.Meta):
            fields = ('id', 'label', 'pictogram')

    class AccessibilitySerializer(TrekAccessibilitySerializer):
        name = serializers.SerializerMethodField(read_only=True)

        def get_name(self, obj):
            return get_translation_or_dict('name', self, obj)

        class Meta(TrekAccessibilitySerializer.Meta):
            fields = ('id', 'name', 'pictogram')

    class RouteSerializer(serializers.ModelSerializer):
        route = serializers.SerializerMethodField(read_only=True)

        def get_route(self, obj):
            return get_translation_or_dict('route', self, obj)

        class Meta:
            model = trekking_models.Route
            fields = ('id', 'route', 'pictogram')


if 'geotrek.sensitivity' in settings.INSTALLED_APPS:
    class SensitiveAreaListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        url = HyperlinkedIdentityField(view_name='apiv2:sensitivearea-detail')
        name = serializers.SerializerMethodField(read_only=True)
        elevation = serializers.SerializerMethodField(read_only=True)
        description = serializers.SerializerMethodField(read_only=True)
        period = serializers.SerializerMethodField(read_only=True)
        practices = serializers.SerializerMethodField(read_only=True)
        info_url = serializers.URLField(source='species.url')
        structure = serializers.CharField(source='structure.name')
        create_datetime = serializers.DateTimeField(source='date_insert')
        update_datetime = serializers.DateTimeField(source='date_update')
        geometry = geo_serializers.GeometryField(read_only=True, source="geom2d_transformed", precision=7)
        species_id = serializers.SerializerMethodField(read_only=True)
        kml_url = serializers.SerializerMethodField(read_only=True)

        def get_name(self, obj):
            return get_translation_or_dict('name', self, obj.species)

        def get_description(self, obj):
            return get_translation_or_dict('description', self, obj)

        def get_period(self, obj):
            return [getattr(obj.species, 'period{:02}'.format(p)) for p in range(1, 13)]

        def get_practices(self, obj):
            return obj.species.practices.values_list('id', flat=True)

        def get_elevation(self, obj):
            return obj.species.radius

        def get_species_id(self, obj):
            if obj.species.category == sensitivity_models.Species.SPECIES:
                return obj.species.id
            return None

        def get_kml_url(self, obj):
            url = reverse('sensitivity:sensitivearea_kml_detail', kwargs={'lang': get_language(), 'pk': obj.pk})
            return self.context['request'].build_absolute_uri(url)

        class Meta:
            model = sensitivity_models.SensitiveArea
            fields = (
                'id', 'url', 'name', 'elevation', 'description', 'period', 'contact', 'practices', 'info_url',
                'published', 'structure', 'species_id', 'kml_url',
                'geometry', 'update_datetime', 'create_datetime'
            )

    class BubbleSensitiveAreaListSerializer(SensitiveAreaListSerializer):
        radius = serializers.SerializerMethodField(read_only=True)

        def get_radius(self, obj):
            if obj.species.category == sensitivity_models.Species.SPECIES and obj.geom.geom_typeid == 0:
                return obj.species.radius
            else:
                return None

        class Meta:
            model = SensitiveAreaListSerializer.Meta.model
            fields = SensitiveAreaListSerializer.Meta.fields + ('radius', )

    class SportPracticeListSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
        name = serializers.SerializerMethodField(read_only=True)

        def get_name(self, obj):
            return get_translation_or_dict('name', self, obj)

        class Meta:
            model = sensitivity_models.SportPractice
            fields = (
                'id', 'name'
            )

if 'geotrek.zoning' in settings.INSTALLED_APPS:
    class CitySerializer(serializers.ModelSerializer):
        geom = geo_serializers.GeometryField(read_only=True, source="geom2d_transformed", precision=7)

        class Meta:
            model = zoning_models.City
            fields = ('code', 'name', 'published', 'geom')

    class DistrictsSerializer(serializers.ModelSerializer):
        geom = geo_serializers.GeometryField(read_only=True, source="geom2d_transformed", precision=7)

        class Meta:
            model = zoning_models.District
            fields = ('id', 'name', 'published', 'geom')


class StructureSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = authent_models.Structure
        fields = (
            'id', 'name'
        )


class TargetPortalListSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField(read_only=True)
    description = serializers.SerializerMethodField(read_only=True)

    def get_title(self, obj):
        return get_translation_or_dict('title', self, obj)

    def get_description(self, obj):
        return get_translation_or_dict('description', self, obj)

    class Meta:
        model = common_models.TargetPortal
        fields = (
            'id', 'name', 'website', 'title', 'description'
        )


class TargetPortalDetailSerializer(TargetPortalListSerializer):
    class Meta(TargetPortalListSerializer.Meta):
        fields = tuple((field for field in TargetPortalListSerializer.Meta.fields if field != 'url')) + ('facebook_id', 'facebook_image_url')
