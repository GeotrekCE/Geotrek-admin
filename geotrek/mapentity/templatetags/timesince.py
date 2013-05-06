"""
http://djangosnippets.org/snippets/2275/
Humanized and localized version of built-in timesince template filter.
Based on Joey Bratton's idea.
"""
import datetime
from django.utils.timezone import utc

from django import template
from django.utils.translation import ugettext, ungettext

register = template.Library()


@register.filter(name='timesince')
def humanize_timesince(date):
    delta = datetime.datetime.utcnow().replace(tzinfo=utc) - date

    num_years = delta.days / 365
    if (num_years > 0):
        return ungettext(u"%d year ago", u"%d years ago", num_years) % num_years

    num_weeks = delta.days / 7
    if (num_weeks > 0):
        return ungettext(u"%d week ago", u"%d weeks ago", num_weeks) % num_weeks

    if (delta.days > 0):
        return ungettext(u"%d day ago", u"%d days ago", delta.days) % delta.days

    num_hours = delta.seconds / 3600
    if (num_hours > 0):
        return ungettext(u"%d hour ago", u"%d hours ago", num_hours) % num_hours

    num_minutes = delta.seconds / 60
    if (num_minutes > 0):
        return ungettext(u"%d minute ago", u"%d minutes ago", num_minutes) % num_minutes

    return ugettext(u"just a few seconds ago")