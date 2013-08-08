import math

from django.core.serializers.base import Serializer
from django.utils.translation import ugettext_lazy as _
from django.db.models.fields.related import ForeignKey, ManyToManyField


class DatatablesSerializer(Serializer):
    def serialize(self, queryset, **options):
        model = options.pop('model', None) or queryset.model
        columns = options.pop('fields')

        attr_getters = {}
        for field in columns:
            if hasattr(model, field + '_display'):
                attr_getters[field] = lambda obj, field: getattr(obj, field + '_display')
            else:
                modelfield = model._meta.get_field(field)
                if isinstance(modelfield, ForeignKey):
                    attr_getters[field] = lambda obj, field: unicode(getattr(obj, field) or _("None"))
                elif isinstance(modelfield, ManyToManyField):
                    attr_getters[field] = lambda obj, field: [unicode(o) for o in getattr(obj, field).all()] or _("None")
                else:
                    def fixfloat(obj, field):
                        value = getattr(obj, field)
                        if isinstance(value, float) and math.isnan(value):
                            value = 0.0
                        return value
                    attr_getters[field] = fixfloat
        # Build list with fields
        map_obj_pk = []
        data_table_rows = []
        for obj in queryset:
            row = [attr_getters[field](obj, field) for field in columns]
            data_table_rows.append(row)
            map_obj_pk.append(obj.pk)

        return {
            # aaData is the key looked up by dataTables
            'aaData': data_table_rows,
            'map_obj_pk': map_obj_pk,
        }
