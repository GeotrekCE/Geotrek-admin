from dal import autocomplete
from django.utils.translation import gettext_lazy as _
from django_filters import ModelMultipleChoiceFilter

from geotrek.altimetry.filters import (
    AltimetryAllGeometriesFilterSet,
    AltimetryPointFilterSet,
)
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.models import Provider
from geotrek.core.filters import TopologyFilter, ValidTopologyFilterSet
from geotrek.zoning.filters import ZoningFilterSet

from .models import POI, Service, Trek


class TrekFilterSet(
    AltimetryAllGeometriesFilterSet,
    ValidTopologyFilterSet,
    ZoningFilterSet,
    StructureRelatedFilterSet,
):
    provider = ModelMultipleChoiceFilter(
        label=_("Provider"),
        queryset=Provider.objects.filter(trek__isnull=False).distinct(),
        widget=autocomplete.Select2Multiple(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Trek
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "published",
            "difficulty",
            "duration",
            "themes",
            "networks",
            "practice",
            "accessibilities",
            "accessibility_level",
            "route",
            "labels",
            "source",
            "portal",
            "reservation_system",
            "provider",
        ]


class POITrekFilter(TopologyFilter):
    queryset = Trek.objects.existing()


class POIFilterSet(
    AltimetryPointFilterSet,
    ValidTopologyFilterSet,
    ZoningFilterSet,
    StructureRelatedFilterSet,
):
    trek = POITrekFilter(
        label=_("Trek"), required=False, widget=autocomplete.Select2Multiple()
    )
    provider = ModelMultipleChoiceFilter(
        label=_("Provider"),
        queryset=Provider.objects.filter(poi__isnull=False).distinct(),
        widget=autocomplete.Select2Multiple(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = POI
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "published",
            "type",
            "trek",
            "provider",
        ]


class ServiceFilterSet(
    AltimetryPointFilterSet,
    ValidTopologyFilterSet,
    ZoningFilterSet,
    StructureRelatedFilterSet,
):
    provider = ModelMultipleChoiceFilter(
        label=_("Provider"),
        queryset=Provider.objects.filter(service__isnull=False).distinct(),
        widget=autocomplete.Select2Multiple(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Service
        fields = [*StructureRelatedFilterSet.Meta.fields, "type", "provider"]
