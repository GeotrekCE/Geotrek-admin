import json

from django import template
from django.conf import settings

from geotrek.outdoor.models import Practice, RatingScale, Site

register = template.Library()


@register.simple_tag
def is_outdoor_enabled():
    return "geotrek.outdoor" in settings.INSTALLED_APPS


@register.simple_tag
def site_practices():
    practices = {
        str(practice.pk): {
            "types": {str(type.pk): type.name for type in practice.site_types.all()},
            "scales": {
                str(scale.pk): scale.name for scale in practice.rating_scales.all()
            },
        }
        for practice in Practice.objects.prefetch_related(
            "site_types", "rating_scales"
        ).all()
    }
    return json.dumps(practices)


@register.simple_tag
def course_sites():
    sites = {
        str(site.pk): {
            "practice": site.practice.pk,
            "types": {
                str(type.pk): type.name for type in site.practice.course_types.all()
            },
            "scales": {
                str(scale.pk): scale.name for scale in site.practice.rating_scales.all()
            },
        }
        if site.practice is not None
        else {"practice": None, "types": {}, "scales": {}}
        for site in Site.objects.select_related("practice")
        .prefetch_related("practice__course_types", "practice__rating_scales")
        .all()
    }
    return json.dumps(sites)


@register.simple_tag
def all_ratings_scales():
    scales = {str(scale.pk): scale.name for scale in RatingScale.objects.all()}
    return json.dumps(scales)


@register.simple_tag
def site_as_list(site):
    return [site]


@register.filter
def orientation_display(orientation):
    return dict(Site.ORIENTATION_CHOICES)[orientation]


@register.filter
def wind_display(orientation):
    return dict(Site.WIND_CHOICES)[orientation]
