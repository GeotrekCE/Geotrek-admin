import os

from django import template
from django.conf import settings
from django.template.base import TemplateDoesNotExist
from django.contrib.gis.geos import GEOSGeometry, Point

register = template.Library()

from .. import app_settings


class SmartIncludeNode(template.Node):
    def __init__(self, viewname):
        super(SmartIncludeNode, self).__init__()
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
                t = template.loader.get_template("%(module)s/%(module)s_%(viewname)s_fragment.html" % locals())
                result += t.render(context)
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
def latlngbounds(obj, fieldname=None):
    if fieldname is None:
        fieldname = app_settings['GEOM_FIELD_NAME']
    if obj is None or isinstance(obj, basestring):
        return 'null'
    if not isinstance(obj, GEOSGeometry):
        obj = getattr(obj, fieldname)
    if obj is None:
        return 'null'
    obj.transform(settings.API_SRID)
    if isinstance(obj, Point):
        extent = [obj.x - 0.005, obj.y - 0.005, obj.x + 0.005, obj.y + 0.005]
    else:
        extent = list(obj.extent)
    return [[extent[1], extent[0]], [extent[3], extent[2]]]


@register.simple_tag()
def media_static_fallback(media_file, static_file, *args, **kwarg):
    if os.path.exists(os.path.join(settings.MEDIA_ROOT, media_file)):
        return os.path.join(settings.MEDIA_URL, media_file)
    return os.path.join(settings.STATIC_URL, static_file)
