from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def suricate_management_enabled():
    return settings.SURICATE_MANAGEMENT_ENABLED
