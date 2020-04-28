import csv
from functools import partial

from django.core.exceptions import FieldDoesNotExist
from django.core.serializers.base import Serializer
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import PictogramSerializerMixin, BasePublishableSerializerMixin
from geotrek.signage import models as signage_models

from mapentity.serializers.helpers import smart_plain_text, field_as_string
from mapentity.serializers.shapefile import ZipShapeSerializer

from rest_framework import serializers as rest_serializers
from rest_framework_gis import fields as rest_gis_fields
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class SignageTypeSerializer(PictogramSerializerMixin):
    class Meta:
        model = signage_models.SignageType
        fields = ('id', 'pictogram', 'label')


class SignageSerializer(BasePublishableSerializerMixin):
    type = SignageTypeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = signage_models.Signage
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = ('id', 'structure', 'name', 'type', 'code', 'printed_elevation', 'condition',
                  'manager', 'sealing') + \
            BasePublishableSerializerMixin.Meta.fields


class SignageGeojsonSerializer(GeoFeatureModelSerializer, SignageSerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(SignageSerializer.Meta):
        geo_field = 'api_geom'
        fields = SignageSerializer.Meta.fields + ('api_geom', )


class BladeTypeSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = signage_models.BladeType
        fields = ('label', )


class BladeSerializer(rest_serializers.ModelSerializer):
    type = BladeTypeSerializer()
    structure = StructureSerializer()
    order_lines = rest_serializers.SerializerMethodField(read_only=True)

    def get_order_lines(self, obj):
        return obj.order_lines.values_list('pk', flat=True)

    class Meta:
        model = signage_models.Blade
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        fields = ('id', 'structure', 'number', 'order_lines', 'type', 'color', 'condition', 'direction')
        # TODO: Do a lineserializer for order_lines


class BladeGeojsonSerializer(GeoFeatureModelSerializer, BladeSerializer):
    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField(read_only=True, precision=7)

    class Meta(BladeSerializer.Meta):
        geo_field = 'api_geom'
        fields = BladeSerializer.Meta.fields + ('api_geom', )


class CSVBladeSerializer(Serializer):
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
        headers = []
        for field in columns:
            c = getattr(model_blade, '%s_verbose_name' % field, None)
            if c is None:
                try:
                    f = model_blade._meta.get_field(field)
                    if f.one_to_many:
                        c = f.field.model._meta.verbose_name_plural
                    else:
                        c = f.verbose_name
                except FieldDoesNotExist:
                    c = _(field.title())
            headers.append(smart_str(str(c)))

        headers_lines = []
        for field in columns_lines:
            c = getattr(model_line, '%s_verbose_name' % field, None)
            if c is None:
                try:
                    f = model_line._meta.get_field(field)
                    if f.one_to_many:
                        c = f.field.model._meta.verbose_name_plural
                    else:
                        c = f.verbose_name
                except FieldDoesNotExist:
                    c = _(field.title())
            headers_lines.append(smart_str(str(c)))

        for i in range(max_lines):
            header_lines = ['%s %s' % (header, i + 1) for header in headers_lines]
            headers.extend(header_lines)

        getters = {}
        for field in columns:
            try:
                modelfield = model_blade._meta.get_field(field)
            except FieldDoesNotExist:
                modelfield = None
            if isinstance(modelfield, ForeignKey):
                getters[field] = lambda obj, field: smart_plain_text(getattr(obj, field), ascii)
            elif isinstance(modelfield, ManyToManyField):
                getters[field] = lambda obj, field: ','.join([smart_plain_text(o, ascii)
                                                              for o in getattr(obj, field).all()] or '')
            else:
                getters[field] = partial(field_as_string, ascii=ascii)

        getters_lines = {}
        for field in columns_lines:
            try:
                modelfield = model_line._meta.get_field(field)
            except FieldDoesNotExist:
                modelfield = None
            if isinstance(modelfield, ForeignKey):
                getters_lines[field] = lambda obj, field: smart_plain_text(getattr(obj, field), ascii)
            elif isinstance(modelfield, ManyToManyField):
                getters_lines[field] = lambda obj, field: ','.join([smart_plain_text(o, ascii)
                                                                   for o in getattr(obj, field).all()] or '')
            else:
                getters_lines[field] = partial(field_as_string, ascii=ascii)

        def get_lines():
            yield headers
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
        return super(ZipBladeShapeSerializer, self).split_bygeom(lines, geom_getter)
