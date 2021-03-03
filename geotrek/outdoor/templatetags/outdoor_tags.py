from django import template
from django.conf import settings
import json
from geotrek.outdoor.models import Practice, Site


register = template.Library()


@register.simple_tag
def is_outdoor_enabled():
    return 'geotrek.outdoor' in settings.INSTALLED_APPS


@register.simple_tag
def site_practices():
    practices = {
        str(practice.pk): {
            'types': {
                str(type.pk): type.name
                for type in practice.types.all()
            },
            'scales': {
                str(scale.pk): {
                    'name': scale.name,
                    'ratings': {
                        str(rating.pk): rating.name
                        for rating in scale.ratings.all()
                    },
                }
                for scale in practice.rating_scales.all()
            },
        }
        for practice in Practice.objects.all()
    }
    return json.dumps(practices)


@register.filter
def orientation_display(orientation):
    return dict(Site.ORIENTATION_CHOICES)[orientation]
