from django.contrib.gis.db.models.functions import GeoFunc
from django.db.models import CharField, FloatField, Func


class Length(GeoFunc):
    """ ST_Length postgis function """
    output_field = FloatField()


def GeometryType(geom):
    """
    GeometryType postgis function
    """
    return Func(geom, function='GeometryType', output_field=CharField())
