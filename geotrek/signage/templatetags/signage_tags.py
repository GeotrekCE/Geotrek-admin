from django import template
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import stringfilter


register = template.Library()


@stringfilter
@register.filter
def meters(value):
    if value:
        return '%s %s' % (value, _('meters'))
    return value


@stringfilter
@register.filter
def string(value):
    return value.__class__.__name__
