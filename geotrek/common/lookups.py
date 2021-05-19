from django.contrib.gis.db.models.fields import BaseSpatialField

from django.contrib.gis.db.models import BooleanField
from django.db.models.lookups import Transform


class IsEmptyFunc(Transform):
    function = 'ST_ISEMPTY'
    output_field = BooleanField()


@BaseSpatialField.register_lookup
class IsEmpty(IsEmptyFunc):
    lookup_name = 'isempty'
