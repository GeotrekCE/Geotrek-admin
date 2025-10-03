from django.contrib.gis.db.models import PointField
from django.contrib.gis.db.models.functions import GeoFunc, GeomOutputGeoFunc
from django.db.models import BooleanField, CharField, FloatField


class Length(GeoFunc):
    """ST_Length postgis function"""

    output_field = FloatField()


class SimplifyPreserveTopology(GeomOutputGeoFunc):
    """ST_SimplifyPreserveTopology postgis function"""


class GeometryType(GeoFunc):
    """GeometryType postgis function"""

    output_field = CharField()
    function = "GeometryType"


class DumpGeom(GeomOutputGeoFunc):
    """ST_Dump postgis function returning only geometry."""

    function = "ST_Dump"
    template = '(%(function)s(%(expressions)s))."geom"'  # ST_DUMP return tuple as (path, geom). Keep geom only.


class StartPoint(GeoFunc):
    """ST_StartPoint postgis function"""

    output_field = PointField()


class EndPoint(GeoFunc):
    """ST_EndPoint postgis function"""

    output_field = PointField()


class Buffer(GeomOutputGeoFunc):
    """ST_Buffer postgis function"""

    pass


class Area(GeoFunc):
    """ST_Area postgis function"""

    output_field = FloatField()


class ST_X(GeoFunc):
    """ST_X postgis function"""

    output_field = FloatField()
    function = "ST_X"


class ST_Y(GeoFunc):
    """ST_Y postgis function"""

    output_field = FloatField()
    function = "ST_Y"


class IsSimple(GeoFunc):
    output_field = BooleanField()


class GeometryN(GeomOutputGeoFunc):
    """ST_GeometryN postgis function"""
