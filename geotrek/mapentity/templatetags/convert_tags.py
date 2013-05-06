import urllib
from mimetypes import types_map

from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def convert_url(request, sourceurl, format='pdf'):
    if '/' not in format:
        extension = '.' + format if not format.startswith('.') else format
        format = types_map[extension]
    fullurl = request.build_absolute_uri(sourceurl)
    conversion_url = "%s?url=%s&to=%s" % (settings.CONVERSION_SERVER,
                                          urllib.quote(fullurl),
                                          format)
    return conversion_url
