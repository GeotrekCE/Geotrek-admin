from datetime import datetime, timedelta

from django import template
from django.utils.translation import ugettext_lazy as _


register = template.Library()


@register.filter
def duration(value):
    """
    Returns a duration in hours to a human readable version (minutes, days, ...)
    """
    if value is None:
        return u""

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
