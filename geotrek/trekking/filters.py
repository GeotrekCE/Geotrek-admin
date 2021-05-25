from django.utils.translation import gettext_lazy as _
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.core.filters import TopologyFilter, ValidTopologyFilterSet
from geotrek.zoning.filters import ZoningFilterSet

from .models import Trek, POI, Service


class TrekFilterSet(ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):

    class Meta(StructureRelatedFilterSet.Meta):
        model = Trek
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'difficulty', 'duration', 'themes', 'networks',
            'practice', 'accessibilities', 'route', 'labels',
            'source', 'portal', 'reservation_system',
        ]


class POITrekFilter(TopologyFilter):
    queryset = Trek.objects.existing()


class POIFilterSet(ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    trek = POITrekFilter(label=_("Trek"), required=False)

    class Meta(StructureRelatedFilterSet.Meta):
        model = POI
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'type', 'trek',
        ]


class ServiceFilterSet(ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    class Meta(StructureRelatedFilterSet.Meta):
        model = Service
        fields = StructureRelatedFilterSet.Meta.fields + ['type']
