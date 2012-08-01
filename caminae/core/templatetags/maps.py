from django import template
from django.template import Context

from djgeojson.serializers import Serializer

register = template.Library()


@register.filter
def fieldmap(obj, fieldname):
    """Usage: {{ object|fieldmap:"geom" }}"""
    name = "map%s%s" % (obj.__class__.__name__, fieldname)
    serializer = Serializer()
    geojson = serializer.serialize([obj], fields=[], srid=4326)
    
    t = template.loader.get_template("core/fieldmap_fragment.html")
    return t.render(Context(dict(mapname=name, geojson=geojson)))
