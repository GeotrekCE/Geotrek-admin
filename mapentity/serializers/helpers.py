from decimal import Decimal
from functools import partial
import html
import json

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.query import QuerySet
from django.utils.encoding import force_str
from django.utils.encoding import smart_str
from django.utils.formats import number_format
from django.utils.functional import Promise
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _


def field_as_string(obj, field, ascii=False):
    value = getattr(obj, field + '_csv_display', None)
    if value is None:
        value = getattr(obj, field + '_display', None)
        if value is None:
            value = getattr(obj, field)
        if isinstance(value, bool):
            value = (_('no'), _('yes'))[value]
        if isinstance(value, float) or isinstance(value, int) or isinstance(value, Decimal):
            value = number_format(value)
        if isinstance(value, list) or isinstance(value, QuerySet):
            value = ", ".join([str(val) for val in value])
    return smart_plain_text(value, ascii)


def plain_text(html_content):
    return html.unescape(strip_tags(html_content))


def smart_plain_text(s, ascii=False):
    if s is None:
        return ''
    try:
        # Converts to unicode, remove HTML tags, convert HTML entities
        us = plain_text(str(s))
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
            return force_str(obj)
        if isinstance(obj, QuerySet):
            # `default` must return a python serializable
            # structure, the easiest way is to load the JSON
            # string produced by `serialize` and return it

            return json.loads(serialize('json', obj))
        return force_str(obj)


# partial function, we can now use dumps(my_dict) instead
# of dumps(my_dict, cls=DjangoJSONEncoder)
json_django_dumps = partial(json.dumps, cls=DjangoJSONEncoder)
