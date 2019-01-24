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
