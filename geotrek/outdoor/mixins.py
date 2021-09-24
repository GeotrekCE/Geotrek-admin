from geotrek.trekking.models import POI
from geotrek.common.utils import intersecting


class ExcludedPOIsMixin:

    @property
    def pois(self):
        pois = intersecting(POI, self)
        pois = pois.exclude(pk__in=self.pois_excluded.values_list('pk', flat=True))
        return pois
