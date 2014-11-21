from django.utils.translation import ugettext_lazy as _

from geotrek.core.filters import TopologyFilter, PathFilterSet, TrailFilterSet
from geotrek.infrastructure.filters import InfrastructureFilterSet, SignageFilterSet
from geotrek.maintenance.filters import InterventionFilterSet, ProjectFilterSet
from geotrek.trekking.filters import TrekFilterSet, POIFilterSet
from geotrek.tourism.filters import TouristicContentFilterSet, TouristicEventFilterSet
from geotrek.zoning.models import City, District


class TopologyFilterCity(TopologyFilter):
    model = City

    def value_to_edges(self, value):
        return value.cityedge_set.all()


class TopologyFilterDistrict(TopologyFilter):
    model = District

    def value_to_edges(self, value):
        return value.districtedge_set.all()


def add_edge_filters(filter_set):
    filter_set.add_filters({
        'city': TopologyFilterCity(label=_('City'), required=False),
        'district': TopologyFilterDistrict(label=_('District'), required=False),
    })


add_edge_filters(TrekFilterSet)
add_edge_filters(POIFilterSet)
add_edge_filters(InterventionFilterSet)
add_edge_filters(ProjectFilterSet)
add_edge_filters(PathFilterSet)
add_edge_filters(InfrastructureFilterSet)
add_edge_filters(SignageFilterSet)
add_edge_filters(TrailFilterSet)


class IntersectionFilter(TopologyFilter):
    """Inherit from ``TopologyFilter``, just to make sure the widgets
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


TouristicContentFilterSet.add_filters({
    'city': IntersectionFilterCity(label=_('City'), required=False),
    'district': IntersectionFilterDistrict(label=_('District'), required=False),
})

TouristicEventFilterSet.add_filters({
    'city': IntersectionFilterCity(label=_('City'), required=False),
    'district': IntersectionFilterDistrict(label=_('District'), required=False),
})
