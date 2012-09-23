import urllib
from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def convert_url(request, sourceurl, format='pdf'):
    fullurl = request.build_absolute_uri(sourceurl)
    conversion_url = "%s?url=%s" % (settings.CONVERSION_SERVER,
                                    urllib.quote(fullurl))
    return conversion_url
