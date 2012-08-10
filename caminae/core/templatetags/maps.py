from django import template
from django.conf import settings
from django.template import Context
from django.contrib.gis.geos import GEOSGeometry, Point

register = template.Library()


@register.filter
def fieldmap(obj, fieldname):
    """Usage: {{ object|fieldmap:"geom" }}"""
    name = "map%s%s" % (obj.__class__.__name__, fieldname)
    t = template.loader.get_template("core/fieldmap_fragment.html")
    return t.render(Context(dict(object=obj, mapname=name)))


@register.filter
def latlngbounds(obj, fieldname='geom'):
    if obj is None or isinstance(obj, basestring):
        return 'null'
    if not isinstance(obj, GEOSGeometry):
        obj = getattr(obj, fieldname)
    if isinstance(obj, Point):
        # TODO: OMG why?
        obj.transform(settings.API_SRID)
        extent = [obj.x-0.005, obj.y-0.005, obj.x+0.005, obj.y+0.005]
    else:
        extent = list(obj.extent)
    return [[extent[1], extent[0]], [extent[3], extent[2]]]
