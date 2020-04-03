import csv
from functools import partial

from django.core.serializers.base import Serializer
from django.utils.encoding import smart_str
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.core.exceptions import FieldDoesNotExist

from .helpers import smart_plain_text, field_as_string


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
                    f = model._meta.get_field(field)
                    if f.one_to_many:
                        c = f.field.model._meta.verbose_name_plural
                    else:
                        c = f.verbose_name
                except FieldDoesNotExist:
                    c = _(field.title())
            headers.append(smart_str(c))

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
            for obj in queryset:
                yield [getters[field](obj, field) for field in columns]
        writer = csv.writer(stream)
        writer.writerows(get_lines())
