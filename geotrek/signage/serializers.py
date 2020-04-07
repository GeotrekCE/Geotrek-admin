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


class SignageTypeSerializer(PictogramSerializerMixin):
    class Meta:
        model = signage_models.SignageType
        fields = ('id', 'pictogram', 'label')


class SignageSerializer(BasePublishableSerializerMixin):
    type = SignageTypeSerializer()
    structure = StructureSerializer()

    # Annotated geom field with API_SRID
    api_geom = rest_gis_fields.GeometryField()

    class Meta:
        model = signage_models.Signage
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'api_geom'
        fields = ('id', 'structure', 'name', 'type', 'code', 'printed_elevation', 'condition',
                  'manager', 'sealing') + \
            BasePublishableSerializerMixin.Meta.fields


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

    # TODO: Fix problem with topology.geom should be possible to use a geom of an other model for the serialization

    class Meta:
        model = signage_models.Blade
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'geom'
        fields = ('id', 'structure', 'number', 'order_lines', 'type', 'color', 'condition', 'direction')
        # TODO: Do a lineserializer for order_lines


class CSVBladeSerializer(Serializer):
    def serialize(self, queryset, **options):
        """
        Uses self.columns, containing fieldnames to produce the CSV.
        The header of the csv is made of the verbose name of each field.
        """
        model = signage_models.Line
        columns = options.pop('fields')
        stream = options.pop('stream')
        ascii = options.get('ensure_ascii', True)

        headers = []
        for field in columns:
            c = getattr(model, '%s_verbose_name' % field, None)
            if c is None:
                try:
                    f = model._meta.get_field(field)
                    if f.one_to_many:
                        c = f.field.model._meta.verbose_name_plural
                    else:
                        c = f.verbose_name
                except FieldDoesNotExist:
                    c = _(field.title())
            headers.append(smart_str(str(c)))
        getters = {}
        for field in columns:
            try:
                modelfield = model._meta.get_field(field)
            except FieldDoesNotExist:
                modelfield = None
            if isinstance(modelfield, ForeignKey):
                getters[field] = lambda obj, field: smart_plain_text(getattr(obj, field), ascii)
            elif isinstance(modelfield, ManyToManyField):
                getters[field] = lambda obj, field: ','.join([smart_plain_text(o, ascii)
                                                              for o in getattr(obj, field).all()] or '')
            else:
                getters[field] = partial(field_as_string, ascii=ascii)

        def get_lines():
            yield headers
            for blade in queryset.order_by('number'):
                for obj in blade.lines.order_by('number'):
                    yield [getters[field](obj, field) for field in columns]

        writer = csv.writer(stream)
        writer.writerows(get_lines())


class ZipBladeShapeSerializer(ZipShapeSerializer):
    def split_bygeom(self, iterable, geom_getter=lambda x: x.geom):
        lines = [line for blade in iterable for line in blade.lines.all()]
        return super(ZipBladeShapeSerializer, self).split_bygeom(lines, geom_getter)
