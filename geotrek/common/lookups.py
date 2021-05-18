from django.contrib.gis.db.models.fields import BaseSpatialField

from geotrek.common.utils.functions import IsEmpty as IsEmptyFunc


@BaseSpatialField.register_lookup
class IsEmpty(IsEmptyFunc):
    lookup_name = 'isempty'
