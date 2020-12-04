from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def is_outdoor_enabled():
    return 'geotrek.outdoor' in settings.INSTALLED_APPS
