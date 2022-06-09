from django.contrib.gis.db.models.functions import GeoFunc
from django.db.models import CharField, FloatField


class Length(GeoFunc):
    """ ST_Length postgis function """
    output_field = FloatField()


class GeometryType(GeoFunc):
    """
    GeometryType postgis function
    """
    output_field = CharField()
    function = 'GeometryType'
