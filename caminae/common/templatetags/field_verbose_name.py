from django import template

register = template.Library()

def field_verbose_name(obj, field):
    """Usage: {{ object|get_object_field }}"""

    return obj._meta.get_field(field).verbose_name

field_verbose_name = register.filter(field_verbose_name)

