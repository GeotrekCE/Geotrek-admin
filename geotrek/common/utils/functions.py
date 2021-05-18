from django.contrib.gis.db.models import BooleanField
from django.db.models.lookups import Transform


class IsEmpty(Transform):
    function = 'ST_ISEMPTY'
    output_field = BooleanField()
