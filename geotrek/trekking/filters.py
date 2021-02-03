from django.utils.translation import gettext_lazy as _
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.core.filters import TopologyFilter
from geotrek.zoning.filters import ZoningFilterSet

from .models import Trek, POI, Service


class TrekFilterSet(ZoningFilterSet, StructureRelatedFilterSet):

    class Meta(StructureRelatedFilterSet.Meta):
        model = Trek
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'difficulty', 'duration', 'themes', 'networks',
            'practice', 'accessibilities', 'route', 'labels',
            'source', 'portal', 'reservation_system',
        ]


class POITrekFilter(TopologyFilter):
    queryset = Trek.objects.existing()


class POIFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    trek = POITrekFilter(label=_("Trek"), required=False)

    class Meta(StructureRelatedFilterSet.Meta):
        model = POI
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'type', 'trek',
        ]


class ServiceFilterSet(ZoningFilterSet, StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Service
        fields = StructureRelatedFilterSet.Meta.fields + ['type']
