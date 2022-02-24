from django.contrib.gis.db.models.functions import GeoFunc
from django.db.models import Func
from django.db.models.fields import FloatField, CharField
from django.contrib.gis.db.models import GeometryField, PointField


def Buffer(geom, radius, num_seg):
    """
    ST_Buffer postgis function
    """
    return Func(geom, radius, num_seg, function='ST_Buffer', output_field=GeometryField())


def GeometryType(geom):
    """
    GeometryType postgis function
    """
    return Func(geom, function='GeometryType', output_field=CharField())


class Length3D(Func):
    """
    ST_3DLENGTH postgis function
    """
    function = 'ST_3DLENGTH'
    output_field = FloatField()


class Area(Func):
    """
    ST_Area postgis function
    """
    function = 'ST_Area'
    output_field = FloatField()


class StartPoint(Func):
    """
    ST_StartPoint postgis function
    """
    function = 'ST_StartPoint'
    output_field = PointField()


class EndPoint(Func):
    """
    ST_EndPoint postgis function
    """
    function = 'ST_EndPoint'
    output_field = PointField()
