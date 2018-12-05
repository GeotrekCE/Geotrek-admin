from __future__ import unicode_literals

from django.db.models import Func, F
from django.db.models.fields import FloatField


def Transform(field_name, srid):
    """
    ST_TRANSFORM postgis function
    """
    return Func(F(field_name), srid, function='ST_TRANSFORM')


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
