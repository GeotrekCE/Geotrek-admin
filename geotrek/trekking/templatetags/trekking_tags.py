from datetime import datetime, timedelta

from django import template
from django.utils.translation import ugettext_lazy as _


register = template.Library()


@register.filter
def duration(value):
    """ Returns a duration in hours to a human readable version (minutes, days, ...)
    """
    seconds = timedelta(minutes=float(value) * 60)
    duration = datetime(1, 1, 1) + seconds
    days = duration.day - 1
    if days >= 8:
        return _("More than %s days") % 8
    if days > 1:
        return _("%s days") % days
    if days == 1 or 12 <= duration.hour < 24:
        return _("%s day") % 1
    if duration.hour > 0:
        return _("%(hour)sH%(min)s") % {'hour': duration.hour,
                                        'min': "%s" % duration.minute if duration.minute > 0 else ""}
    return _("%s min") % duration.minute
