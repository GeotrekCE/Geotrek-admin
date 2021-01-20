from django.utils.translation import gettext_lazy as _

from geotrek.common.filters import RightFilter
from geotrek.zoning.models import City, District


class IntersectionFilter(RightFilter):
    """Inherit from ``RightFilter``, just to make sure the widgets
    will be initialized the same way.
    """

    def filter(self, qs, value):
        if not value:
            return qs
        return qs.filter(geom__intersects=value.geom)


class IntersectionFilterCity(IntersectionFilter):
    model = City


class IntersectionFilterDistrict(IntersectionFilter):
    model = District


def add_filters_zoning(filter_set):
    filter_set.add_filters({
        'city': IntersectionFilterCity(label=_('City'), required=False),
        'district': IntersectionFilterDistrict(label=_('District'), required=False),
    })
