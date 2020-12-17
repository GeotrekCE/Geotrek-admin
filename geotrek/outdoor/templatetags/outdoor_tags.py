from django import template
from django.conf import settings
import json
from geotrek.outdoor.models import Practice


register = template.Library()


@register.simple_tag
def is_outdoor_enabled():
    return 'geotrek.outdoor' in settings.INSTALLED_APPS


@register.simple_tag
def site_practices():
    practices = {
        str(practice.pk): {
            'type_values': {
                str(type.pk): type.name
                for type in practice.types.all()
            },
        }
        for practice in Practice.objects.all()
    }
    return json.dumps(practices)
