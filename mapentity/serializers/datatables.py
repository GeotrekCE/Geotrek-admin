import math

from django.core.serializers.base import Serializer
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ForeignKey, ManyToManyField


class DatatablesSerializer(Serializer):
    def serialize(self, queryset, **options):
        model = options.pop('model', None) or queryset.model
        columns = options.pop('fields')

        getters = {}
        for field in columns:
            if hasattr(model, field + '_display'):
                getters[field] = lambda obj, field: getattr(obj, field + '_display')
            else:
                modelfield = model._meta.get_field(field)
                if isinstance(modelfield, ForeignKey):
                    getters[field] = lambda obj, field: (getattr(obj, field) or _("None"))
                elif isinstance(modelfield, ManyToManyField):
                    getters[field] = lambda obj, field: (getattr(obj, field).all() or _("None"))
                else:
                    def fixfloat(obj, field):
                        value = getattr(obj, field)
                        if isinstance(value, float) and math.isnan(value):
                            value = 0.0
                        return value
                    getters[field] = fixfloat
        # Build list with fields
        map_obj_pk = []
        data_table_rows = []
        for obj in queryset:
            row = [getters[field](obj, field) for field in columns]
            data_table_rows.append(row)
            map_obj_pk.append(obj.pk)

        return {
            # aaData is the key looked up by dataTables
            'aaData': data_table_rows,
            'map_obj_pk': map_obj_pk,
        }
