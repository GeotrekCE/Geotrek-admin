import os

from django import template
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import FieldDoesNotExist
from django.template import Context
from django.template.exceptions import TemplateDoesNotExist
from django.utils.timezone import now
from django.utils.translation import gettext, ngettext

from ..helpers import alphabet_enumeration

register = template.Library()


class SmartIncludeNode(template.Node):
    def __init__(self, viewname):
        super().__init__()
        self.viewname = viewname

    def render(self, context):
        apps = [app.split('.')[-1] for app in settings.INSTALLED_APPS]

        # Bring current app to the top of the list
        appname = context.get('appname', apps[0])
        apps.pop(apps.index(appname))
        apps = [appname] + apps

        viewname = self.viewname
        result = ""
        for module in apps:
            try:
                template_name = "%(module)s/%(module)s_%(viewname)s_fragment.html" % {'viewname': viewname,
                                                                                      'module': module}
                t = template.loader.get_template(template_name)
                result += t.render(Context.flatten(context))
            except TemplateDoesNotExist:
                pass
        return result


@register.tag(name="smart_include")
def do_smart_include(parser, token):
    try:
        tag_name, viewname = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires one argument" % token.contents.split()[0])
    if not (viewname[0] == viewname[-1] and viewname[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's viewname argument should be in quotes" % tag_name)
    return SmartIncludeNode(viewname[1:-1])


@register.filter
def latlngbounds(obj):
    if obj is None or isinstance(obj, str):
        return 'null'
    if isinstance(obj, GEOSGeometry):
        extent = obj.extent
    else:
        extent = obj.get_map_image_extent()
    return [[extent[1], extent[0]], [extent[3], extent[2]]]


@register.filter(name='verbose')
def field_verbose_name(obj, field):
    """Usage: {{ object|get_object_field }}"""
    if hasattr(obj, '%s_verbose_name' % field):
        return str(getattr(obj, '%s_verbose_name' % field))
    try:
        return obj._meta.get_field(field).verbose_name
    except FieldDoesNotExist:
        raise


@register.simple_tag()
def media_static_fallback(media_file, static_file, *args, **kwarg):
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, media_file)):
        return os.path.join(settings.MEDIA_URL, media_file)
    return os.path.join(settings.STATIC_URL, static_file)


@register.simple_tag()
def media_static_fallback_path(media_file, static_file, *args, **kwarg):
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, media_file)):
        return os.path.join(settings.MEDIA_ROOT, media_file)
    return os.path.join(settings.STATIC_ROOT, static_file)


@register.filter(name='timesince')
def humanize_timesince(date):
    """
    http://djangosnippets.org/snippets/2275/
    Humanized and localized version of built-in timesince template filter.
    Based on Joey Bratton's idea.
    """
    if not date:
        return ""

    delta = now() - date

    num_years = delta.days // 365
    if (num_years > 0):
        return ngettext("%d year ago", "%d years ago", num_years) % num_years

    num_weeks = delta.days // 7
    if (num_weeks > 0):
        return ngettext("%d week ago", "%d weeks ago", num_weeks) % num_weeks

    if (delta.days > 0):
        return ngettext("%d day ago", "%d days ago", delta.days) % delta.days

    num_hours = delta.seconds // 3600
    if (num_hours > 0):
        return ngettext("%d hour ago", "%d hours ago", num_hours) % num_hours

    num_minutes = delta.seconds // 60
    if (num_minutes > 0):
        return ngettext("%d minute ago", "%d minutes ago", num_minutes) % num_minutes

    return gettext("just a few seconds ago")


@register.inclusion_tag('mapentity/_detail_valuelist_fragment.html')
def valuelist(items, field=None, enumeration=False):
    """
    Common template tag to show a list of values in detail pages.

    :param field: Use this attribute on each item instead of their unicode representation
    :param enumeration: Show enumerations, useful to match those shown by ``mapentity/leaflet.enumeration.js``

    See https://github.com/makinacorpus/django-mapentity/issues/35
        https://github.com/makinacorpus/Geotrek/issues/960
        https://github.com/makinacorpus/Geotrek/issues/214
        https://github.com/makinacorpus/Geotrek/issues/871
    """
    if field:
        def display(v):
            return getattr(v, '%s_display' % field, getattr(v, field))
        itemslist = [display(v) for v in items]
    else:
        itemslist = items

    letters = alphabet_enumeration(len(items))

    valuelist = []
    for i, item in enumerate(itemslist):
        valuelist.append({
            'enumeration': letters[i] if enumeration else False,
            'pk': getattr(items[i], 'pk', None),
            'text': item
        })

    modelname = None
    if len(items) > 0:
        oneitem = items[0]
        if hasattr(oneitem, '_meta'):
            modelname = oneitem._meta.object_name.lower()

    return {
        'valuelist': valuelist,
        'modelname': modelname
    }


@register.inclusion_tag('mapentity/_detail_valuetable_fragment.html')
def valuetable(items, columns='', enumeration=False):
    """
    Common template tag to show a table with columns in detail pages.

    :param enumeration: Show enumerations, see ``valuelist`` template tag.
    """

    columns = columns.split(',')
    letters = alphabet_enumeration(len(items))

    records = []
    for i, item in enumerate(items):
        def display(column):
            return getattr(item, '%s_display' % column, getattr(item, column))
        attrs = [display(column) for column in columns]

        records.append({
            'enumeration': letters[i] if enumeration else False,
            'attrs': attrs,
            'pk': getattr(item, 'pk', None)
        })

    if len(items) > 0:
        oneitem = items[0]
        columns_titles = []
        for column in columns:
            columns_titles.append({'name': column,
                                   'text': field_verbose_name(oneitem, column)})
        modelname = oneitem._meta.object_name.lower()
    else:
        modelname = None
        columns_titles = None

    return {
        'nbcolumns': len(columns),
        'columns': columns_titles,
        'records': records,
        'modelname': modelname
    }
