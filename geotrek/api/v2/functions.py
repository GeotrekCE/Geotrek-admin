from django.db.models import Func
from django.db.models.fields import FloatField
from django.contrib.gis.db.models import GeometryField


def Buffer(geom, radius, num_seg):
    """
    ST_Buffer postgis function
    """
    return Func(geom, radius, num_seg, function='ST_Buffer', output_field=GeometryField())


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
