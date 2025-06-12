from datetime import datetime, timedelta

from django import template
from django.conf import settings
from django.utils.translation import gettext_lazy as _

register = template.Library()


@register.simple_tag
def is_photos_accessibilities_enabled():
    return settings.ACCESSIBILITY_ATTACHMENTS_ENABLED


@register.simple_tag
def are_hdviews_enabled():
    return settings.ENABLE_HD_VIEWS


@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")


@register.simple_tag
def is_topology_model(model):
    return hasattr(model, "kind") and hasattr(model, "offset")


@register.simple_tag
def is_blade_model(model):
    return model._meta.model_name == "blade"


@register.simple_tag
def is_site_model(model):
    return model._meta.model_name == "site"


@register.simple_tag
def is_course_model(model):
    return model._meta.model_name == "course"


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
            final_duration = _("%(nb)s days") % {"nb": duration.day}

        else:
            if duration.day - 1 == 1:
                final_duration = _("%s day") % (duration.day - 1)
            else:
                final_duration = _("%s days") % (duration.day - 1)

    elif duration.hour > 0 and duration.minute > 0:
        final_duration = _("%(hour)s h %(min)s") % {
            "hour": duration.hour,
            "min": duration.minute,
        }

    elif duration.hour > 0:
        final_duration = _("%(hour)s h") % {"hour": duration.hour}

    else:
        final_duration = _("%s min") % duration.minute

    return final_duration
