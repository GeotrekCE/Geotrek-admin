from django.db.models import CharField, FloatField
from django.contrib.gis.db.models.functions import GeoFunc, GeomOutputGeoFunc


class Length(GeoFunc):
    """ ST_Length postgis function """
    output_field = FloatField()


class SimplifyPreserveTopology(GeomOutputGeoFunc):
    pass


class GeometryType(GeoFunc):
    """
    GeometryType postgis function
    """
    output_field = CharField()
    function = 'GeometryType'
