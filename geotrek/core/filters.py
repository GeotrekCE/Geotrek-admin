from dal import autocomplete
from django.conf import settings
from django.forms import widgets
from django.utils.translation import gettext_lazy as _
from django_filters import (
    BooleanFilter,
    FilterSet,
    ModelMultipleChoiceFilter,
)

from geotrek.altimetry.filters import AltimetryAllGeometriesFilterSet
from geotrek.authent.filters import StructureRelatedFilterSet
from geotrek.common.filters import RightFilter
from geotrek.common.models import Provider
from geotrek.maintenance import models as maintenance_models
from geotrek.maintenance.filters import InterventionFilterSet, ProjectFilterSet
from geotrek.zoning.filters import ZoningFilterSet
from .functions import TopologyIsValid

from .models import CertificationLabel, Comfort, Network, Path, Topology, Trail, Usage


class ValidTopologyFilterSet(FilterSet):
    if settings.TREKKING_TOPOLOGY_ENABLED:
        coupled = BooleanFilter()
        is_valid_topology = BooleanFilter(
            label=_("Valid topology"),
            method="filter_valid_topology",
            widget=widgets.NullBooleanSelect(
                attrs={"class": "form-control form-control-sm"}
            ),
        )

    def filter_valid_topology(self, qs, name, value):
        if value is not None:
            id_column = 'id' if qs.model == Topology else 'topo_object_id'
            qs = qs.alias(topology_is_valid=TopologyIsValid(id_column)).filter(topology_is_valid=value)
        return qs


class TopologyFilter(RightFilter):
    def filter(self, qs, values):
        """Overrides parent filter() method completely."""
        if not values:
            return qs
        if issubclass(values[0].__class__, Topology):
            edges = Topology.objects.filter(pk__in=[value.pk for value in values])
        else:
            edges = self.values_to_edges(values)
        return self._topology_filter(qs, edges)

    def values_to_edges(self, values):
        """
        For an instance of this filter model, returns a Topology queryset.
        """
        raise NotImplementedError

    def _topology_filter(self, qs, edges):
        """
        This piece of code should be rewritten nicely with managers : TODO !
        """
        # In case, we filter on paths
        if qs.model == Path:
            paths = []
            for edge in edges:
                paths.extend(edge.paths.all())
            return qs.filter(pk__in=[path.pk for path in set(paths)])

        overlapping = Topology.overlapping(edges)

        # TODO: This is (amazingly) ugly in terms of OOP. Should refactor overlapping()
        if issubclass(qs.model, maintenance_models.Intervention):
            return qs.filter(target_id__in=[topo.pk for topo in overlapping])
        elif issubclass(qs.model, maintenance_models.Project):
            # Find all interventions overlapping those edges
            interventions = self._topology_filter(
                maintenance_models.Intervention.objects.existing()
                .select_related("project")
                .filter(project__in=qs),
                edges,
            )
            # Return only the projects concerned by the interventions
            projects = []
            for intervention in interventions:
                projects.append(intervention.project.pk)
            return qs.filter(pk__in=set(projects))

        else:
            assert issubclass(qs.model, Topology), (
                f"{qs.model} is not a Topology as expected"
            )
            return qs.filter(pk__in=[topo.pk for topo in overlapping])


class PathFilterSet(
    AltimetryAllGeometriesFilterSet, ZoningFilterSet, StructureRelatedFilterSet
):
    provider = ModelMultipleChoiceFilter(
        label=_("Provider"),
        queryset=Provider.objects.filter(path__isnull=False).distinct(),
        widget=autocomplete.Select2Multiple(),
    )
    networks = ModelMultipleChoiceFilter(
        queryset=Network.objects.all().select_related("structure"),
        widget=autocomplete.Select2Multiple(),
    )
    usages = ModelMultipleChoiceFilter(
        queryset=Usage.objects.all().select_related("structure"),
        widget=autocomplete.Select2Multiple(),
    )
    comfort = ModelMultipleChoiceFilter(
        queryset=Comfort.objects.all().select_related("structure"),
        widget=autocomplete.Select2Multiple(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Path
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "name",
            "comments",
            "valid",
            "networks",
            "usages",
            "comfort",
            "stake",
            "draft",
            "provider",
        ]


class TrailFilterSet(
    AltimetryAllGeometriesFilterSet,
    ValidTopologyFilterSet,
    ZoningFilterSet,
    StructureRelatedFilterSet,
):
    certification_labels = ModelMultipleChoiceFilter(
        field_name="certifications__certification_label",
        label=_("Certification labels"),
        queryset=CertificationLabel.objects.all(),
        widget=autocomplete.Select2Multiple(),
    )
    provider = ModelMultipleChoiceFilter(
        label=_("Provider"),
        queryset=Provider.objects.filter(trail__isnull=False).distinct(),
        widget=autocomplete.Select2Multiple(),
    )

    class Meta(StructureRelatedFilterSet.Meta):
        model = Trail
        fields = [
            *StructureRelatedFilterSet.Meta.fields,
            "name",
            "category",
            "departure",
            "arrival",
            "certification_labels",
            "comments",
            "provider",
        ]


class TopologyFilterTrail(TopologyFilter):
    queryset = Trail.objects.existing()


if settings.TRAIL_MODEL_ENABLED:
    for filterset in (PathFilterSet, InterventionFilterSet, ProjectFilterSet):
        filterset.add_filters(
            {
                "trail": TopologyFilterTrail(
                    label=_("Trail"),
                    required=False,
                    widget=autocomplete.Select2Multiple(),
                )
            }
        )
