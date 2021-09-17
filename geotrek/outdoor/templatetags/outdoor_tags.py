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
                for type in practice.site_types.all()
            },
            'scales': {
                str(scale.pk): scale.name
                for scale in practice.rating_scales.all()
            },
        }
        for practice in Practice.objects.all()
    }

    return json.dumps(practices)


@register.simple_tag
def course_sites():
    sites = {
        str(site.pk): {
            'types': {
                str(type.pk): type.name
                for type in site.practice.course_types.all()
            }
        } if not(site.practice is None) else {'types': {}}
        for site in Site.objects.all()
    }
    return json.dumps(sites)


@register.filter
def orientation_display(orientation):
    return dict(Site.ORIENTATION_CHOICES)[orientation]


@register.filter
def wind_display(orientation):
    return dict(Site.WIND_CHOICES)[orientation]
