import csv

from drf_dynamic_fields import DynamicFieldsMixin
from mapentity.serializers import MapentityGeojsonModelSerializer
from mapentity.serializers.commasv import CSVSerializer
from mapentity.serializers.shapefile import ZipShapeSerializer
from rest_framework import serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.fields import GeometrySerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import PictogramSerializerMixin, BasePublishableSerializerMixin
from . import models as signage_models


class SignageTypeSerializer(PictogramSerializerMixin):
    class Meta:
        model = signage_models.SignageType
        fields = ('id', 'pictogram', 'label')


class SignageSerializer(DynamicFieldsMixin, BasePublishableSerializerMixin, serializers.ModelSerializer):
    name = serializers.CharField(source='name_display')
    structure = serializers.SlugRelatedField('name', read_only=True)
    type = serializers.CharField(source='type_display')
    condition = serializers.SlugRelatedField('label', read_only=True)
    manager = serializers.SlugRelatedField('organism', read_only=True)
    sealing = serializers.SlugRelatedField('label', read_only=True)

    class Meta:
        model = signage_models.Signage
        fields = "__all__"


class SignageGeojsonSerializer(MapentityGeojsonModelSerializer):
    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = signage_models.Signage
        fields = ('id', 'name', 'published')


class SignageAPISerializer(BasePublishableSerializerMixin):
    type = SignageTypeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = signage_models.Signage
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = ('id', 'structure', 'name', 'type', 'code', 'printed_elevation', 'condition',
                  'manager', 'sealing') + BasePublishableSerializerMixin.Meta.fields


class SignageAPIGeojsonSerializer(GeoFeatureModelSerializer, SignageAPISerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(SignageAPISerializer.Meta):
        geo_field = 'api_geom'
        fields = SignageAPISerializer.Meta.fields + ('api_geom', )


class BladeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = signage_models.BladeType
        fields = ('label', )


class BladeSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    type = serializers.SlugRelatedField('label', read_only=True)
    structure = serializers.SlugRelatedField('name', read_only=True)
    direction = serializers.SlugRelatedField('label', read_only=True)
    color = serializers.SlugRelatedField('label', read_only=True)
    condition = serializers.SlugRelatedField('label', read_only=True)
    number = serializers.CharField(source='number_display')

    class Meta:
        model = signage_models.Blade
        fields = "__all__"


class BladeGeojsonSerializer(MapentityGeojsonModelSerializer):
    api_geom = GeometrySerializerMethodField()

    def get_api_geom(self, obj):
        return obj.geom.transform(4326, clone=True)

    class Meta(MapentityGeojsonModelSerializer.Meta):
        model = signage_models.Blade
        fields = ('id', 'number')


class BladeAPISerializer(serializers.ModelSerializer):
    type = BladeTypeSerializer()
    structure = StructureSerializer()
    order_lines = serializers.SerializerMethodField()

    def get_order_lines(self, obj):
        return obj.order_lines.values_list('pk', flat=True)

    class Meta:
        model = signage_models.Blade
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = ('id', 'structure', 'number', 'order_lines', 'type', 'color', 'condition', 'direction')
        # TODO: Do a lineserializer for order_lines


class BladeAPIGeojsonSerializer(GeoFeatureModelSerializer, BladeAPISerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(BladeAPISerializer.Meta):
        geo_field = 'api_geom'
        fields = BladeAPISerializer.Meta.fields + ('api_geom', )


class CSVBladeSerializer(CSVSerializer):
    def serialize(self, queryset, **options):
        """
        Uses self.columns, containing fieldnames to produce the CSV.
        The header of the csv is made of the verbose name of each field.
        """
        model_blade = signage_models.Blade
        columns = options.pop('fields')
        columns_lines = options.pop('line_fields')
        model_line = signage_models.Line
        stream = options.pop('stream')
        ascii = options.get('ensure_ascii', True)
        max_lines = max([value.lines.count() for value in queryset])

        header = self.get_csv_header(columns, model_blade)

        header_line = self.get_csv_header(columns_lines, model_line)

        for i in range(max_lines):
            numbered_header_lines = ['%s %s' % (header, i + 1) for header in header_line]
            header.extend(numbered_header_lines)

        getters = self.getters_csv(columns, model_blade, ascii)

        getters_lines = self.getters_csv(columns_lines, model_line, ascii)

        def get_lines():
            yield header
            for blade in queryset.order_by('signage__code', 'number'):
                column_getter = [getters[field](blade, field) for field in columns]
                for obj in blade.lines.order_by('number'):
                    column_getter.extend(getters_lines[field](obj, field) for field in columns_lines)
                yield column_getter

        writer = csv.writer(stream)
        writer.writerows(get_lines())


class ZipBladeShapeSerializer(ZipShapeSerializer):
    def split_bygeom(self, iterable, geom_getter=lambda x: x.geom):
        lines = [blade for blade in iterable]
        return super().split_bygeom(lines, geom_getter)
