from django.utils.translation import gettext_lazy as _
from django_filters import ChoiceFilter
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.core.filters import TopologyFilter, ValidTopologyFilterSet
from geotrek.altimetry.filters import AltimetryPointFilterSet, AltimetryAllGeometriesFilterSet
from geotrek.zoning.filters import ZoningFilterSet

from .models import Trek, POI, Service


class TrekFilterSet(AltimetryAllGeometriesFilterSet, ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    provider = ChoiceFilter(
        field_name='provider',
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=Trek.objects.provider_choices()
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Trek
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'difficulty', 'duration', 'themes', 'networks',
            'practice', 'accessibilities', 'accessibility_level', 'route', 'labels',
            'source', 'portal', 'reservation_system', 'provider'
        ]


class POITrekFilter(TopologyFilter):
    queryset = Trek.objects.existing()


class POIFilterSet(AltimetryPointFilterSet, ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    trek = POITrekFilter(label=_("Trek"), required=False)
    provider = ChoiceFilter(
        field_name='provider',
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=POI.objects.provider_choices()
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = POI
        fields = StructureRelatedFilterSet.Meta.fields + [
            'published', 'type', 'trek', 'provider'
        ]


class ServiceFilterSet(AltimetryPointFilterSet, ValidTopologyFilterSet, ZoningFilterSet, StructureRelatedFilterSet):
    provider = ChoiceFilter(
        field_name='provider',
        empty_label=_("Provider"),
        label=_("Provider"),
        choices=Service.objects.provider_choices()
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Service
        fields = StructureRelatedFilterSet.Meta.fields + ['type', 'provider']
