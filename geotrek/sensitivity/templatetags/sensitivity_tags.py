from django import template
from django.conf import settings


register = template.Library()


@register.assignment_tag
def is_sensitivity_enabled():
    return settings.SENSITIVITY_ENABLED
