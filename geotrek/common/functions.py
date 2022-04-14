from django.contrib.gis.db.models.functions import GeoFunc
from django.db.models import FloatField


class Length(GeoFunc):
    """ ST_Length postgis function """
    output_field = FloatField()
