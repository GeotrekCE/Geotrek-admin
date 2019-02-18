from __future__ import unicode_literals

from django.db.models import Func
from django.db.models.fields import FloatField, CharField
from django.contrib.gis.db.models import GeometryField, PointField


def Transform(geom, srid):
    """
    ST_TRANSFORM postgis function
    """
    return Func(geom, srid, function='ST_TRANSFORM')


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


class Length(Func):
    """
    ST_LENGTH postgis function
    """
    function = 'ST_LENGTH'
    output_field = FloatField()


class Length3D(Func):
    """
    ST_3DLENGTH postgis function
    """
    function = 'ST_3DLENGTH'
    output_field = FloatField()


class Area(Func):
    """
    ST_AREA postgis function
    """
    function = 'ST_AREA'
    output_field = FloatField()


class StartPoint(Func):
    """
    ST_TRANSFORM postgis function
    """
    function = 'ST_STARTPOINT'
    output_field = PointField()
