from django.db.models import Func
from django.db.models.fields import FloatField


class Length3D(Func):
    """
    ST_3DLENGTH postgis function
    """
    function = 'ST_3DLENGTH'
    output_field = FloatField()
