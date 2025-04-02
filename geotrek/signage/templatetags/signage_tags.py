from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.translation import gettext_lazy as _

register = template.Library()


@stringfilter
@register.filter
def meters(value):
    if value:
        return "%s %s" % (value, _("meters"))
    return value


@stringfilter
@register.filter
def class_name(value):
    return value.__class__.__name__


@register.simple_tag
def blades_enabled():
    return settings.BLADE_ENABLED


@register.simple_tag
def lines_enabled():
    return settings.LINE_ENABLED


@register.simple_tag
def direction_on_lines_enabled():
    return settings.DIRECTION_ON_LINES_ENABLED
