from geotrek.common.utils import intersecting, queryset_or_all_objects
from geotrek.trekking.models import POI


class ExcludedPOIsMixin:
    @property
    def pois(self, queryset=None):
        queryset = queryset_or_all_objects(queryset, POI)
        pois = intersecting(queryset, self)
        pois = pois.exclude(pk__in=self.pois_excluded.values_list("pk", flat=True))
        return pois
