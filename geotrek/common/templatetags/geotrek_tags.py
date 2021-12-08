from geotrek.zoning.models import RestrictedAreaType, RestrictedArea
from django import template
from django.conf import settings
from datetime import datetime, timedelta
import json

from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.simple_tag
def is_topology_model(model):
    return hasattr(model, 'kind') and hasattr(model, 'offset')


@register.simple_tag
def is_blade_model(model):
    return model._meta.model_name == 'blade'


@register.simple_tag
def is_site_model(model):
    return model._meta.model_name == 'site'


@register.simple_tag
def is_course_model(model):
    return model._meta.model_name == 'course'


@register.filter
def duration(value):
    """
    Returns a duration in hours to a human readable version (minutes, days, ...)
    """
    if value is None:
        return ""

    seconds = timedelta(minutes=float(value) * 60)
    duration = datetime(1, 1, 1) + seconds

    if duration.day > 1:
        if duration.hour > 0 or duration.minute > 0:
            final_duration = _("%s days") % duration.day

        else:
            final_duration = _("%s days") % (duration.day - 1)

    elif duration.hour > 0 and duration.minute > 0:
        final_duration = _("%(hour)s h %(min)s") % {'hour': duration.hour,
                                                    'min': duration.minute, }

    elif duration.hour > 0:
        final_duration = _("%(hour)s h") % {'hour': duration.hour}

    else:
        final_duration = _("%s min") % duration.minute

    return final_duration


@register.simple_tag
def restricted_area_types():
    restricted_areas_types = {
        str(type.pk): {
            'areas': [{
                str(area.pk): area.area_type.name + " - " + area.name
            } for area in type.restrictedarea_set.order_by('name')
            ]  # We use an array instead of dict because JS parsing would re-order JSON dict
        }
        for type in RestrictedAreaType.objects.all()
    }
    return json.dumps(restricted_areas_types)


@register.simple_tag
def all_restricted_areas():
    all_restricted_areas = [{
        str(area.pk): area.area_type.name + " - " + area.name
    } for area in RestrictedArea.objects.order_by('area_type__name', 'name')
    ]  # We use an array instead of dict because JS parsing would re-order JSON dict
    return json.dumps(all_restricted_areas)
