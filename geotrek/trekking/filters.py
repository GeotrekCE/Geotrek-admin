from django.utils.translation import gettext_lazy as _
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.core.filters import TopologyFilter, ValidTopologyFilterSet
from geotrek.altimetry.filters import AltimetryPointFilterSet, AltimetryAllGeometriesFilterSet
from geotrek.zoning.filters import ZoningFilterSet

from .models import Trek, POI, Service


class TrekFilterSet(AltimetryAllGeometriesFilterSet, ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):

    class Meta(StructureRelatedFilterSet.Meta):
        model = Trek
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'difficulty', 'duration', 'themes', 'networks',
            'practice', 'accessibilities', 'accessibility_level', 'route', 'labels',
            'source', 'portal', 'reservation_system',
        ]


class POITrekFilter(TopologyFilter):
    queryset = Trek.objects.existing()


class POIFilterSet(AltimetryPointFilterSet, ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    trek = POITrekFilter(label=_("Trek"), required=False)

    class Meta(StructureRelatedFilterSet.Meta):
        model = POI
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'type', 'trek',
        ]


class ServiceFilterSet(AltimetryPointFilterSet, ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    class Meta:
        model = Service
        fields = StructureRelatedFilterSet.Meta.fields + ['type']
