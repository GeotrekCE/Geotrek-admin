import csv
from functools import partial

from django.core.serializers.base import Serializer
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import FieldDoesNotExist
from django.utils.encoding import smart_str
from django.db.models.fields.related import ForeignKey, ManyToManyField

from geotrek.authent.serializers import StructureSerializer
from geotrek.common.serializers import PictogramSerializerMixin, BasePublishableSerializerMixin
from geotrek.signage import models as signage_models

from mapentity.serializers.helpers import smart_plain_text, field_as_string


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
        geo_field = 'geom'
        fields = ('id', 'structure', 'name', 'type', 'code', 'printed_elevation',
                  'manager', 'sealing') + \
            BasePublishableSerializerMixin.Meta.fields


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
            headers.append(smart_str(unicode(c)))
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
