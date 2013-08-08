from HTMLParser import HTMLParser

from django.utils.encoding import smart_str
from django.utils.html import strip_tags


def plain_text(html):
    h = HTMLParser()
    return h.unescape(strip_tags(html))


def smart_plain_text(s, ascii=False):
    if s is None:
        return ''
    try:
        # Converts to unicode, remove HTML tags, convert HTML entities
        us = plain_text(unicode(s))
        if ascii:
            return smart_str(us)
        return us
    except UnicodeDecodeError:
        return smart_str(s)


from .commasv import *
from .gpx import *
from .datatables import *
from .shapefile import *
