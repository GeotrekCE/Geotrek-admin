from django.contrib.gis.db.models.functions import GeoFunc
from django.db.models import FloatField


class RasterValue(GeoFunc):
    """SQL Function class to get value from raster band (ST_VALUE)"""

    function = "ST_VALUE"
    geom_param_pos = (1,)
    output_field = FloatField()
