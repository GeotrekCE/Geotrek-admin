from datetime import datetime, timedelta

from django import template
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


register = template.Library()


@register.filter
def duration(value):
    """ Returns a duration in hours to a human readable version (minutes, days, ...)
    """
    if value is None:
        return u""
    seconds = timedelta(minutes=float(value) * 60)
    duration = datetime(1, 1, 1) + seconds
    days = duration.day - 1
    if days >= 8:
        return _("More than %s days") % 8
    if days > 1:
        return _("%s days") % days
    if days <= 1:
        hours = (settings.TREK_DAY_DURATION * days) + duration.hour
        if hours > settings.TREK_DAY_DURATION:
            return _("%s days") % 2
    if duration.hour > 0 and duration.minute > 0:
        return _("%(hour)s h %(min)s") % {'hour': duration.hour,
                                          'min': duration.minute}
    if duration.hour > 0:
        return _("%(hour)s h") % {'hour': duration.hour}
    return _("%s min") % duration.minute
