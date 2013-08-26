from django import template

from ..helpers import convertit_url


register = template.Library()


@register.simple_tag
def convert_url(request, sourceurl, format='application/pdf'):
    return convertit_url(request, sourceurl, to_type=format, add_host=False)
