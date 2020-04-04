import json

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.utils.encoding import force_text
from django.utils.encoding import smart_str
from django.utils.formats import number_format
from django.utils.functional import Promise, curry
from django.utils.html import strip_tags
from django.utils.six.moves.html_parser import HTMLParser
from django.utils.translation import ugettext_lazy as _


def field_as_string(obj, field, ascii=False):
    value = getattr(obj, field + '_csv_display', None)
    if value is None:
        value = getattr(obj, field + '_display', None)
        if value is None:
            value = getattr(obj, field)
        if isinstance(value, bool):
            value = (_('no'), _('yes'))[value]
        if isinstance(value, float) or isinstance(value, int):
            value = number_format(value)
    return smart_plain_text(value, ascii)


def plain_text(html):
    h = HTMLParser()
    return h.unescape(strip_tags(html))


def smart_plain_text(s, ascii=False):
    if s is None:
        return ''
    try:
        # Converts to unicode, remove HTML tags, convert HTML entities
        us = plain_text(u"{}".format(s))
        if ascii:
            return smart_str(us)
        return us
    except UnicodeDecodeError:
        return smart_str(s)


class DjangoJSONEncoder(DjangoJSONEncoder):
    """
    Taken (slightly modified) from:
    http://stackoverflow.com/questions/2249792/json-serializing-django-models-with-simplejson
    """
    def default(self, obj):
        # https://docs.djangoproject.com/en/dev/topics/serialization/#id2
        if isinstance(obj, Promise):
            return force_text(obj)
        if isinstance(obj, QuerySet):
            # `default` must return a python serializable
            # structure, the easiest way is to load the JSON
            # string produced by `serialize` and return it

            return json.loads(serialize('json', obj))
        return force_text(obj)


# partial function, we can now use dumps(my_dict) instead
# of dumps(my_dict, cls=DjangoJSONEncoder)
json_django_dumps = curry(json.dumps, cls=DjangoJSONEncoder)
