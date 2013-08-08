import csv
from functools import partial

from django.core.serializers.base import Serializer
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ForeignKey, ManyToManyField, FieldDoesNotExist

from . import smart_plain_text


def field_as_string(obj, field, ascii=False):
    value = getattr(obj, field + '_csv_display', None)
    if value is None:
        value = getattr(obj, field + '_display', None)
        if value is None:
            value = getattr(obj, field)
    if hasattr(value, '__iter__'):
        return ','.join([smart_plain_text(item, ascii) for item in value])
    return smart_plain_text(value, ascii)


class CSVSerializer(Serializer):
    def serialize(self, queryset, **options):
        """
        Uses self.columns, containing fieldnames to produce the CSV.
        The header of the csv is made of the verbose name of each field.
        """
        model = options.pop('model', None) or queryset.model
        columns = options.pop('fields')
        stream = options.pop('stream')
        ascii = options.get('ensure_ascii', True)

        headers = []
        for field in columns:
            c = getattr(model, '%s_verbose_name' % field, None)
            if c is None:
                try:
                    c = model._meta.get_field(field).verbose_name
                except FieldDoesNotExist:
                    c = _(field.title())
            headers.append(smart_str(unicode(c)))

        attr_getters = {}
        for field in columns:
            try:
                modelfield = model._meta.get_field(field)
            except FieldDoesNotExist:
                modelfield = None
            if isinstance(modelfield, ForeignKey):
                attr_getters[field] = lambda obj, field: smart_plain_text(getattr(obj, field), ascii)
            elif isinstance(modelfield, ManyToManyField):
                attr_getters[field] = lambda obj, field: ','.join([smart_plain_text(o, ascii) for o in getattr(obj, field).all()] or '')
            else:
                attr_getters[field] = partial(field_as_string, ascii=ascii)

        def get_lines():
            yield headers
            for obj in queryset:
                yield [attr_getters[field](obj, field) for field in columns]
        writer = csv.writer(stream)
        writer.writerows(get_lines())
