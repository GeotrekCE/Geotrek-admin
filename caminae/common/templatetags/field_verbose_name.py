from django import template
from django.db.models.fields.related import FieldDoesNotExist

register = template.Library()

def field_verbose_name(obj, field):
    """Usage: {{ object|get_object_field }}"""
    try:
        return obj._meta.get_field(field).verbose_name
    except FieldDoesNotExist:
        a = getattr(obj, '%s_verbose_name' % field)
        if a is None:
            raise
        return unicode(a)

register.filter(field_verbose_name)
register.filter('verbose', field_verbose_name)

