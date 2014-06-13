from django import template
from django.conf import settings

register = template.Library()


@register.assignment_tag
def settings_value(name):
    return getattr(settings, name, "")
