from django_filters import FilterSet
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from geotrek.common.filters import RightFilter
from geotrek.zoning.models import City, District


class IntersectionFilter(RightFilter):
    """Inherit from ``RightFilter``, just to make sure the widgets
    will be initialized the same way.
    """

    def filter(self, qs, value):
        q = Q()
        for subvalue in value:
            q |= Q(geom__intersects=subvalue.geom)
        return qs.filter(q)


class IntersectionFilterCity(IntersectionFilter):
    model = City


class IntersectionFilterDistrict(IntersectionFilter):
    model = District


class ZoningFilterSet(FilterSet):
    city = IntersectionFilterCity(label=_('City'), required=False)
    district = IntersectionFilterDistrict(label=_('District'), required=False)
